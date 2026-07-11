"""Benchmark Docling PDF conversion throughput (pages/second) across processing configs.

Reads every PDF from INPUT_DIR and converts each with the shared build_converter,
once per config JSON found in CONFIG_DIR (the same fast/accurate presets the worker
uses). Reports per-document and aggregate throughput plus a profiler-based stage
breakdown for each config, then a side-by-side comparison. Runs in one of two modes
so intra-op threading (Option A) and process-level parallelism (Option B) can be
compared on the same core budget.

Environment variables:
  INPUT_DIR            Directory to scan for *.pdf  (default: /data)
  OUTPUT_DIR           Directory for the per-config results JSON (default: /out)
  CONFIG_DIR           Directory of config JSON presets to benchmark (default: /configs)
  WORKERS              Parallel converter processes (default: 1 -> single-process, Option A)
  CPU_CORES            Core budget used to auto-split threads across workers (default: 2)
  DOCLING_NUM_THREADS  Threads per worker; overrides the CPU_CORES // WORKERS default
  DOCLING_DO_OCR       "true"/"false" run OCR with each config's engine (default: false)
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

from converter import ProcessingConfig, build_converter
from docling.datamodel.settings import settings
from docling.document_converter import DocumentConverter

_WORKER_CONVERTER: DocumentConverter | None = None


def _env_bool(name: str, default: bool) -> bool:
    """Parse a boolean-ish environment variable."""
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def load_configs() -> list[tuple[str, ProcessingConfig]]:
    """Load every config preset in CONFIG_DIR, keyed by file stem."""
    config_dir = Path(os.environ.get("CONFIG_DIR", "/configs"))
    files = sorted(config_dir.glob("*.json"))
    if not files:
        raise SystemExit(f"No config JSON found in {config_dir}")
    return [(f.stem, ProcessingConfig.model_validate_json(f.read_text())) for f in files]


def stage_timings(conv: Any) -> dict[str, dict[str, float]]:
    """Extract per-stage wall time (seconds) from a conversion result's profiler data."""
    timings = {}
    for scope, item in conv.timings.items():
        timings[scope] = {"count": item.count, "total_sec": round(sum(item.times), 4)}
    return timings


def _init_worker(warmup_pdf: str, config: ProcessingConfig, ocr: bool, barrier: Any = None) -> None:
    """Build a per-process converter, warm the models, then sync on the barrier."""
    global _WORKER_CONVERTER
    settings.debug.profile_pipeline_timings = True
    _WORKER_CONVERTER = build_converter(config, ocr)
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
    }


def run_conversions(
    paths: list[str], warmup_pdf: str, config: ProcessingConfig, ocr: bool
) -> tuple[list[dict[str, Any]], float]:
    """Run all conversions in the configured mode and return (results, processing_wall_sec)."""
    if WORKERS == 1:
        _init_worker(warmup_pdf, config, ocr)
        start = time.perf_counter()
        results = [_convert_task(p) for p in paths]
        return results, time.perf_counter() - start

    ctx = mp.get_context("spawn")
    manager = ctx.Manager()
    barrier = manager.Barrier(WORKERS + 1)
    with ctx.Pool(WORKERS, initializer=_init_worker, initargs=(warmup_pdf, config, ocr, barrier)) as pool:
        barrier.wait()
        start = time.perf_counter()
        results = list(pool.imap(_convert_task, paths))
        elapsed = time.perf_counter() - start
    return results, elapsed


def run_config(name: str, config: ProcessingConfig, ocr: bool, paths: list[str], output_dir: Path) -> dict[str, Any]:
    """Benchmark one config over all PDFs, print its report, and write its results JSON."""
    print(f"\n{'=' * 68}\nConfig '{name}': table_mode={config.table_mode} "
          f"do_table_structure={config.do_table_structure} images_scale={config.images_scale} "
          f"num_threads={config.num_threads} ocr={ocr} engine={config.ocr_engine if ocr else '-'}\n{'=' * 68}")

    print("Warming up (loading models, excluded from timing)...")
    raw, proc_wall = run_conversions(paths, paths[0], config, ocr)
    raw.sort(key=lambda r: r["file"])

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

    agg_pps = total_pages / proc_wall if proc_wall else 0.0
    print("-" * 68)
    print(f"{'TOTAL (wall)':<45} {total_pages:>6} {proc_wall:>8.2f} {agg_pps:>7.2f}")

    substage_sum = sum(v for k, v in stage_totals.items() if k != "pipeline_total")
    print("\nStage breakdown (hottest first):")
    print(f"{'stage':<22} {'sec':>8} {'share':>8}")
    print("-" * 40)
    for scope, secs in sorted(stage_totals.items(), key=lambda kv: -kv[1]):
        if scope == "pipeline_total":
            continue
        pct = (secs / substage_sum * 100) if substage_sum else 0.0
        print(f"{scope:<22} {secs:>8.2f} {pct:>7.1f}%")

    summary = {
        "config_name": name,
        "num_documents": len(paths),
        "total_pages": total_pages,
        "processing_wall_sec": round(proc_wall, 3),
        "sum_convert_sec": round(sum_seconds, 3),
        "aggregate_pages_per_sec": round(agg_pps, 3),
        "config": {
            "table_mode": config.table_mode,
            "do_table_structure": config.do_table_structure,
            "images_scale": config.images_scale,
            "num_threads": config.num_threads,
            "ocr": ocr,
            "ocr_engine": config.ocr_engine if ocr else None,
            "workers": WORKERS,
            "threads_per_worker": THREADS_PER_WORKER,
            "cpu_cores": CPU_CORES,
        },
        "stage_totals_sec": {k: round(v, 3) for k, v in sorted(stage_totals.items(), key=lambda kv: -kv[1])},
        "per_document": raw,
    }
    output_file = output_dir / f"benchmark_{name}.json"
    output_file.write_text(json.dumps(summary, indent=2))
    print(f"\nWrote results to {output_file}")
    return summary


def main() -> None:
    """Benchmark every config preset over the PDF corpus and print a comparison."""
    input_dir = Path(os.environ.get("INPUT_DIR", "/data"))
    output_dir = Path(os.environ.get("OUTPUT_DIR", "/out"))
    ocr = _env_bool("DOCLING_DO_OCR", False)

    pdfs = sorted(input_dir.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {input_dir}")
    paths = [str(p) for p in pdfs]

    configs = load_configs()
    print(f"Found {len(pdfs)} PDF(s) in {input_dir}; benchmarking configs: {[n for n, _ in configs]}")
    print(f"workers={WORKERS} threads/worker={THREADS_PER_WORKER} core_budget={CPU_CORES} ocr={ocr}")

    summaries = [run_config(name, config, ocr, paths, output_dir) for name, config in configs]

    print(f"\n{'=' * 68}\nComparison\n{'=' * 68}")
    print(f"{'config':<16} {'pages':>6} {'wall_sec':>10} {'pages/sec':>10}")
    print("-" * 46)
    for s in summaries:
        print(f"{s['config_name']:<16} {s['total_pages']:>6} {s['processing_wall_sec']:>10.2f} "
              f"{s['aggregate_pages_per_sec']:>10.3f}")


if __name__ == "__main__":
    main()
