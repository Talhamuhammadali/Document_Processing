"""arq worker that runs real Docling processing jobs."""

import asyncio
import logging
from typing import Any

from arq.connections import RedisSettings
from arq.jobs import JobStatus
from docling.document_converter import DocumentConverter

from app.core.captioning import enqueue_captioning
from app.core.config import settings
from app.core.jobs import get_job, update_status
from app.core.pipeline import process_document
from app.core.processing.config_store import load_config, seed_configs
from app.core.processing.converter import build_converter
from app.core.processing.types import OcrEngine
from app.core.redis_client import redis_client
from app.storage.factory import get_repository

logger = logging.getLogger(__name__)

MAX_JOBS = 4
THREADS_PER_JOB = 1

_CONVERTERS: dict[tuple[str, OcrEngine], DocumentConverter] = {}
_CONVERTER_LOCKS: dict[tuple[str, OcrEngine], asyncio.Lock] = {}


def _get_converter(client: Any, mode: str, ocr: OcrEngine) -> DocumentConverter:
    """Return a cached converter for (mode, ocr), building it on first use."""
    key = (mode, ocr)
    if key not in _CONVERTERS:
        config = load_config(client, mode).model_copy(update={"num_threads": THREADS_PER_JOB})
        _CONVERTERS[key] = build_converter(config, ocr)
    return _CONVERTERS[key]


async def process_document_task(ctx: dict[str, Any], doc_id: str) -> str:
    """Convert, normalize, embed, and store one document; update its job record."""
    client = ctx["redis_sync"]
    repo = ctx["repo"]

    record = get_job(client, doc_id)
    if record is None:
        logger.error("no job record for %s; skipping", doc_id)
        return "missing"

    update_status(client, doc_id, JobStatus.in_progress)
    try:
        key = (record.mode, record.ocr)
        converter = _get_converter(client, record.mode, record.ocr)
        lock = _CONVERTER_LOCKS.setdefault(key, asyncio.Lock())
        async with lock:
            result = await asyncio.to_thread(converter.convert, record.source_path)
        document, embeddings, images = process_document(result.document, doc_id, record.filename)
        repo.save(document, embeddings, images)
        update_status(client, doc_id, JobStatus.complete)
        enqueue_captioning(doc_id)
        logger.info("processed %s (%s chunks)", doc_id, len(document.chunks))
        return "done"
    except Exception as exc:  # noqa: BLE001
        logger.exception("processing failed for %s", doc_id)
        update_status(client, doc_id, JobStatus.complete, error=str(exc))
        return "failed"


async def startup(ctx: dict[str, Any]) -> None:
    """Seed configs, open a sync Redis client and repo, and warm default converters."""
    client = redis_client(decode_responses=True)
    ctx["redis_sync"] = client
    ctx["repo"] = get_repository()
    seed_configs(client, settings.configs_dir)
    for mode in ("fast", "accurate"):
        _get_converter(client, mode, "none")
    logger.info("worker ready; converters warmed for fast/accurate")


class WorkerSettings:
    """arq worker configuration."""

    functions = [process_document_task]
    on_startup = startup
    max_jobs = MAX_JOBS
    redis_settings = RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        database=settings.redis_db,
    )
