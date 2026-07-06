"""Benchmark docling PDF conversion throughput on CPU (pages/second).

Reads every PDF from INPUT_DIR and converts each with a CPU-pinned docling
pipeline, reporting per-document and aggregate throughput plus a profiler-based
stage breakdown. Runs in one of two modes so intra-op threading (Option A) and
process-level parallelism (Option B) can be compared on the same core budget.

Environment variables:
  INPUT_DIR            Directory to scan for *.pdf  (default: /data)
  OUTPUT_JSON          Where to write the results summary (default: <INPUT_DIR>/benchmark_results.json)
  DOCLING_DEVICE       cpu | cuda | auto accelerator device (default: cpu)
  WORKERS              Parallel converter processes (default: 1 -> single-process, Option A)
  CPU_CORES            Core budget used to auto-split threads across workers (default: 2)
  DOCLING_NUM_THREADS  Threads per worker; overrides the CPU_CORES // WORKERS default
  DOCLING_DO_OCR       "true"/"false" run OCR (default: false; these specs are digital PDFs)
  DOCLING_OCR_ENGINE   easyocr | rapidocr | tesseract (only used when DOCLING_DO_OCR=true)
  DOCLING_DO_TABLES    "true"/"false" run table-structure model (default: true)
"""

import os

WORKERS = max(1, int(os.environ.get("WORKERS", "1")))
CPU_CORES = max(1, int(os.environ.get("CPU_CORES", "2")))
THREADS_PER_WORKER = int(os.environ.get("DOCLING_NUM_THREADS", str(max(1, CPU_CORES // WORKERS))))
for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_var] = str(THREADS_PER_WORKER)

import json
import multiprocessing as mp
import time
from pathlib import Path
from typing import Any

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    EasyOcrOptions,
    PdfPipelineOptions,
    RapidOcrOptions,
    TesseractCliOcrOptions,
)
from docling.datamodel.settings import settings
from docling.document_converter import DocumentConverter, PdfFormatOption

OCR_ENGINES = {
    "easyocr": EasyOcrOptions,
    "rapidocr": RapidOcrOptions,
    "tesseract": TesseractCliOcrOptions,
}

DEVICES = {
    "cpu": AcceleratorDevice.CPU,
    "cuda": AcceleratorDevice.CUDA,
    "auto": AcceleratorDevice.AUTO,
}

_WORKER_CONVERTER: DocumentConverter | None = None


def _env_bool(name: str, default: bool) -> bool:
    """Parse a boolean-ish environment variable."""
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def build_converter() -> DocumentConverter:
    """Construct a docling converter on the configured device with a bounded thread count."""
    device_name = os.environ.get("DOCLING_DEVICE", "cpu").strip().lower()
    if device_name not in DEVICES:
        raise SystemExit(f"Unknown DOCLING_DEVICE={device_name!r}; choose from {sorted(DEVICES)}")
    accelerator = AcceleratorOptions(num_threads=THREADS_PER_WORKER, device=DEVICES[device_name])

    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options = accelerator
    pipeline_options.generate_picture_images = True
    pipeline_options.images_scale = 2.0
    pipeline_options.do_ocr = _env_bool("DOCLING_DO_OCR", False)
    pipeline_options.do_table_structure = _env_bool("DOCLING_DO_TABLES", True)

    if pipeline_options.do_ocr:
        engine = os.environ.get("DOCLING_OCR_ENGINE", "easyocr").strip().lower()
        if engine not in OCR_ENGINES:
            raise SystemExit(f"Unknown DOCLING_OCR_ENGINE={engine!r}; choose from {sorted(OCR_ENGINES)}")
        pipeline_options.ocr_options = OCR_ENGINES[engine]()

    return DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)})


def stage_timings(conv: Any) -> dict[str, dict[str, float]]:
    """Extract per-stage wall time (seconds) from a conversion result's profiler data."""
    timings = {}
    for scope, item in conv.timings.items():
        timings[scope] = {"count": item.count, "total_sec": round(sum(item.times), 4)}
    return timings


def save_converted_document(document_json: str, pdf_name: str, output_dir: Path) -> None:
    """Save a converted document's JSON (named after its source PDF) to output_dir."""
    output_file = output_dir / f"{Path(pdf_name).stem}.json"
    output_file.write_text(document_json)
    print(f"Saved converted document to {output_file}")


def _init_worker(warmup_pdf: str, barrier: Any = None) -> None:
    """Build a per-process converter, warm the models, then sync on the barrier."""
    global _WORKER_CONVERTER
    settings.debug.profile_pipeline_timings = True
    _WORKER_CONVERTER = build_converter()
    _WORKER_CONVERTER.convert(warmup_pdf)
    if barrier is not None:
        barrier.wait()


def _convert_task(pdf_path_str: str) -> dict[str, Any]:
    """Convert one PDF using the process-local converter and return timed results."""
    assert _WORKER_CONVERTER is not None
    start = time.perf_counter()
    conv = _WORKER_CONVERTER.convert(pdf_path_str)
    elapsed = time.perf_counter() - start
    return {
        "file": Path(pdf_path_str).name,
        "pages": conv.document.num_pages(),
        "seconds": round(elapsed, 3),
        "status": str(conv.status),
        "stage_timings": stage_timings(conv),
        "document_json": conv.document.model_dump_json(indent=4),
    }


def run_conversions(paths: list[str], warmup_pdf: str) -> tuple[list[dict[str, Any]], float]:
    """Run all conversions in the configured mode and return (results, processing_wall_sec)."""
    if WORKERS == 1:
        _init_worker(warmup_pdf)
        start = time.perf_counter()
        results = [_convert_task(p) for p in paths]
        return results, time.perf_counter() - start

    ctx = mp.get_context("spawn")
    manager = ctx.Manager()
    barrier = manager.Barrier(WORKERS + 1)
    with ctx.Pool(WORKERS, initializer=_init_worker, initargs=(warmup_pdf, barrier)) as pool:
        barrier.wait()
        start = time.perf_counter()
        results = list(pool.imap(_convert_task, paths))
        elapsed = time.perf_counter() - start
    return results, elapsed


def main() -> None:
    """Run the benchmark and print a summary table plus a JSON results file."""
    input_dir = Path(os.environ.get("INPUT_DIR", "/data"))
    output_json = Path(os.environ.get("OUTPUT_JSON", str(input_dir / "benchmark_results.json")))

    pdfs = sorted(input_dir.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {input_dir}")

    print(f"Found {len(pdfs)} PDF(s) in {input_dir}")
    print(
        f"Config: device={os.environ.get('DOCLING_DEVICE', 'cpu')} "
        f"workers={WORKERS} threads/worker={THREADS_PER_WORKER} core_budget={CPU_CORES} "
        f"ocr={_env_bool('DOCLING_DO_OCR', False)} "
        f"engine={os.environ.get('DOCLING_OCR_ENGINE', 'easyocr') if _env_bool('DOCLING_DO_OCR', False) else '-'} "
        f"tables={_env_bool('DOCLING_DO_TABLES', True)}"
    )

    paths = [str(p) for p in pdfs]
    warmup_pdf = paths[0]

    print("\nWarming up workers (loading models, excluded from timing)...")
    raw, proc_wall = run_conversions(paths, warmup_pdf)
    raw.sort(key=lambda r: r["file"])

    results = []
    stage_totals: dict[str, float] = {}
    total_pages = 0
    sum_seconds = 0.0

    print(f"\n{'document':<45} {'pages':>6} {'sec':>8} {'p/s':>7}")
    print("-" * 68)
    for r in raw:
        total_pages += r["pages"]
        sum_seconds += r["seconds"]
        for scope, t in r["stage_timings"].items():
            stage_totals[scope] = stage_totals.get(scope, 0.0) + t["total_sec"]
        per_doc_pps = r["pages"] / r["seconds"] if r["seconds"] else 0.0
        print(f"{r['file'][:44]:<45} {r['pages']:>6} {r['seconds']:>8.2f} {per_doc_pps:>7.2f}")
        results.append({k: v for k, v in r.items() if k != "document_json"})

    agg_pps = total_pages / proc_wall if proc_wall else 0.0
    print("-" * 68)
    print(f"{'TOTAL (wall)':<45} {total_pages:>6} {proc_wall:>8.2f} {agg_pps:>7.2f}")
    print(f"Sum of per-doc convert time: {sum_seconds:.2f}s (parallel overlap = {sum_seconds - proc_wall:.2f}s saved)")

    substage_sum = sum(v for k, v in stage_totals.items() if k != "pipeline_total")
    print(f"\nStage breakdown (across {len(pdfs)} docs, hottest first):")
    print(f"{'stage':<22} {'sec':>8} {'share':>8}")
    print("-" * 40)
    for scope, secs in sorted(stage_totals.items(), key=lambda kv: -kv[1]):
        if scope == "pipeline_total":
            continue
        pct = (secs / substage_sum * 100) if substage_sum else 0.0
        print(f"{scope:<22} {secs:>8.2f} {pct:>7.1f}%")

    summary = {
        "num_documents": len(pdfs),
        "total_pages": total_pages,
        "processing_wall_sec": round(proc_wall, 3),
        "sum_convert_sec": round(sum_seconds, 3),
        "aggregate_pages_per_sec": round(agg_pps, 3),
        "config": {
            "device": os.environ.get("DOCLING_DEVICE", "cpu"),
            "workers": WORKERS,
            "threads_per_worker": THREADS_PER_WORKER,
            "cpu_cores": CPU_CORES,
            "do_ocr": _env_bool("DOCLING_DO_OCR", False),
            "do_table_structure": _env_bool("DOCLING_DO_TABLES", True),
        },
        "stage_totals_sec": {k: round(v, 3) for k, v in sorted(stage_totals.items(), key=lambda kv: -kv[1])},
        "per_document": results,
    }
    output_json.write_text(json.dumps(summary, indent=2))
    print(f"\nWrote results to {output_json}")

    output_dir = output_json.parent
    print(f"\nWriting {len(raw)} converted document(s) to {output_dir}")
    for r in raw:
        save_converted_document(r["document_json"], r["file"], output_dir)


if __name__ == "__main__":
    main()
