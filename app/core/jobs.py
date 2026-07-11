"""Per-document processing job status tracked in Redis."""

from typing import Literal

import redis
from arq.jobs import JobStatus
from pydantic import BaseModel

from app.core.processing.types import OcrEngine

_PREFIX = "job:"


class JobRecord(BaseModel):
    """The processing selection and status for one document.

    Status uses arq's JobStatus (queued, in_progress, complete). A complete job
    with a non-null error is a failure; a complete job with error None succeeded.

    Attributes
    ----------
    doc_id : str
        The document id.
    filename : str
        Original filename, carried through for display.
    status : JobStatus
        Current queue lifecycle state.
    mode : Literal["fast", "accurate"]
        The selected processing preset.
    ocr : OcrEngine
        The selected OCR engine, or none.
    source_path : str
        Path to the source PDF on the shared store.
    error : str | None
        Failure message when a complete job failed.

    """

    doc_id: str
    filename: str
    status: JobStatus
    mode: Literal["fast", "accurate"]
    ocr: OcrEngine
    source_path: str
    error: str | None = None


def set_job(client: redis.Redis, record: JobRecord) -> None:
    """Store a job record, overwriting any existing one."""
    client.set(f"{_PREFIX}{record.doc_id}", record.model_dump_json())


def get_job(client: redis.Redis, doc_id: str) -> JobRecord | None:
    """Return a stored job record, or None if absent."""
    raw = client.get(f"{_PREFIX}{doc_id}")
    return JobRecord.model_validate_json(raw) if raw else None


def update_status(
    client: redis.Redis, doc_id: str, status: JobStatus, error: str | None = None
) -> JobRecord | None:
    """Update the status (and optional error) of an existing job record."""
    record = get_job(client, doc_id)
    if record is None:
        return None
    record.status = status
    record.error = error
    set_job(client, record)
    return record
