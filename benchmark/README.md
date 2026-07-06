# Docling CPU benchmark

Runs docling over the sample PDFs inside a container capped at **1 CPU core / 4 GB RAM**,
fully on CPU, and reports **pages/second**.

## Run

```bash
docker compose -f docker-compose.benchmark.yml build   # one-time: pulls CPU torch + docling + models
docker compose -f docker-compose.benchmark.yml up       # runs the benchmark, prints the table
```

Results table prints to the console; a machine-readable summary lands in
`benchmark/out/benchmark_results.json`.

## The four things that make this "CPU-only, 1 core, 4 GB"

1. **The cap itself** — `deploy.resources.limits` in the compose file (`cpus: "1.0"`,
   `memory: 4G`). Compose v2 enforces these as a cgroup limit on plain `up`, not just in swarm.
2. **CPU-only torch** — the Dockerfile installs torch from PyTorch's `whl/cpu` index.
   The default PyPI wheels bundle CUDA (multi-GB) for a GPU we don't have.
3. **Thread pinning** — docling's accelerator is set to `AcceleratorDevice.CPU` with
   `num_threads=1`, and `OMP/MKL/OPENBLAS_NUM_THREADS=1` guard the math backends
   underneath. With only 1 core, more threads just thrash.
4. **Pre-downloaded models** — layout + tableformer are fetched at build time, so the
   benchmark times *inference*, not a cold network download.

## Knobs (env vars in `docker-compose.benchmark.yml`)

| var | default | meaning |
|-----|---------|---------|
| `DOCLING_NUM_THREADS` | `1` | threads for docling's accelerator |
| `DOCLING_DO_OCR` | `false` | run OCR — leave off for digital PDFs (else you measure easyocr, and you must add `easyocr` to the model-download line in the Dockerfile) |
| `DOCLING_DO_TABLES` | `true` | run the table-structure model |

## How p/s is measured

The first `convert()` loads the models into memory and is timed separately as
"warm-up". Every subsequent document is timed individually; aggregate
pages/second = `total pages / total warm conversion seconds`.
