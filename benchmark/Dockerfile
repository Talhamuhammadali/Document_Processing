FROM python:3.13-slim

# System libraries + tesseract OCR (stable; rarely changes)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-osd \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1 \
    HF_HUB_DISABLE_TELEMETRY=1 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    DOCLING_ARTIFACTS_PATH=/root/.cache/docling/models

WORKDIR /app

# torch is large and version-stable: its own cached layer
ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu
RUN pip install --index-url ${TORCH_INDEX_URL} torch==2.9.1 torchvision==0.24.1

# docling + OCR engines: cached until a version bumps
RUN pip install \
        "docling==2.66.0" \
        "easyocr>=1.7.2" \
        "rapidocr-onnxruntime>=1.2.0"

# Model weights: cached layer, never invalidated by code or config changes
RUN docling-tools models download layout tableformer easyocr rapidocr

# Code changes last (also bind-mounted in compose, so tuning needs no rebuild)
COPY benchmark.py /app/benchmark.py

CMD ["python", "/app/benchmark.py"]
