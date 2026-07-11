"""Document processing endpoints."""

from collections import Counter
from pathlib import Path
from typing import Any, Literal, get_args

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from app.core.config import settings
from app.core.embedder import FakeEmbedder
from app.core.jobs import JobRecord, get_job, set_job
from app.core.processing.types import OcrEngine
from app.core.redis_client import redis_client
from app.storage.factory import get_repository

router = APIRouter(prefix="/documents", tags=["documents"])

_repo = get_repository()
_redis = redis_client(decode_responses=True)
_embedder = FakeEmbedder()

Mode = Literal["fast", "accurate"]
_MODES: tuple[Mode, ...] = get_args(Mode)
_OCRS: tuple[OcrEngine, ...] = get_args(OcrEngine)


def _variant_id(stem: str, mode: str, ocr: str) -> str:
    """Return the stored document id for one config variant of a file."""
    return f"{stem}__{mode}-{ocr}"


def _doc_id(rel_path: str) -> str:
    """Derive a stable, collision-free document id from a PDF's path under pdf_dir."""
    return Path(rel_path).with_suffix("").as_posix().replace("/", "__").replace(" ", "_")


def _resolve_sample(rel_path: str) -> Path:
    """Resolve a sample PDF path under pdf_dir, rejecting traversal outside it."""
    root = settings.pdf_dir.resolve()
    source = (root / rel_path).resolve()
    if not source.is_relative_to(root) or not source.exists():
        raise HTTPException(status_code=404, detail="Sample not found.")
    return source


class SearchRequest(BaseModel):
    """A RAG search request."""

    query: str
    top_k: int = 5
    document_id: str | None = None


class OpenRequest(BaseModel):
    """A request to open a sample document by filename."""

    filename: str
    mode: Mode = "fast"
    ocr: OcrEngine = "none"


class ReprocessRequest(BaseModel):
    """A request to reprocess a stored document with a new mode or OCR engine."""

    mode: Mode = "fast"
    ocr: OcrEngine = "none"


class CompareRequest(BaseModel):
    """A request to process a sample under all mode x OCR configs for comparison."""

    filename: str


def _pdf_path(doc_id: str) -> Path:
    """Return the shared-store path for a document's source PDF."""
    return settings.pdf_store_dir / f"{doc_id}.pdf"


async def _enqueue(request: Request, record: JobRecord) -> dict[str, Any]:
    """Persist the job selection and enqueue a processing job; return its status."""
    settings.pdf_store_dir.mkdir(parents=True, exist_ok=True)
    set_job(_redis, record)
    await request.app.state.arq.enqueue_job("process_document_task", record.doc_id)
    return {"document_id": record.doc_id, "status": record.status.value}


@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    mode: Mode = Form("fast"),
    ocr: OcrEngine = Form("none"),
) -> dict[str, Any]:
    """Upload a PDF, store it, and enqueue real processing."""
    filename = file.filename or "upload.pdf"
    doc_id = Path(filename).stem
    dest = _pdf_path(doc_id)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(await file.read())
    record = JobRecord(
        doc_id=doc_id, filename=filename, status="queued", mode=mode, ocr=ocr, source_path=str(dest)
    )
    return await _enqueue(request, record)


@router.get("/available")
async def list_available() -> dict[str, Any]:
    """List every PDF under the data root (recursively) with its processed/queued state."""
    processed = set(_repo.list_ids())
    available = []
    for pdf in sorted(settings.pdf_dir.rglob("*.pdf")):
        rel = pdf.relative_to(settings.pdf_dir).as_posix()
        doc_id = _doc_id(rel)
        job = get_job(_redis, doc_id)
        available.append(
            {
                "id": doc_id,
                "filename": rel,
                "name": pdf.name,
                "folder": pdf.parent.relative_to(settings.pdf_dir).as_posix() or ".",
                "processed": doc_id in processed,
                "status": job.status.value if job else None,
            }
        )
    return {"available": available}


@router.post("/open")
async def open_document(request: Request, body: OpenRequest) -> dict[str, Any]:
    """Open a sample document by relative path, copying it to the store and enqueueing it."""
    source = _resolve_sample(body.filename)
    doc_id = _doc_id(body.filename)
    dest = _pdf_path(doc_id)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(source.read_bytes())
    record = JobRecord(
        doc_id=doc_id, filename=body.filename, status="queued", mode=body.mode, ocr=body.ocr, source_path=str(dest)
    )
    return await _enqueue(request, record)


@router.post("/{document_id}/reprocess")
async def reprocess_document(request: Request, document_id: str, body: ReprocessRequest) -> dict[str, Any]:
    """Reprocess a document's stored PDF with a new mode or OCR engine."""
    job = get_job(_redis, document_id)
    source = _pdf_path(document_id)
    if job is None or not source.exists():
        raise HTTPException(status_code=404, detail="No source PDF to reprocess.")
    record = JobRecord(
        doc_id=document_id,
        filename=job.filename,
        status="queued",
        mode=body.mode,
        ocr=body.ocr,
        source_path=str(source),
    )
    return await _enqueue(request, record)


@router.get("/{document_id}/status")
async def get_status(document_id: str) -> dict[str, Any]:
    """Return the processing job status and selection for a document."""
    job = get_job(_redis, document_id)
    if job is None:
        raise HTTPException(status_code=404, detail="No job for this document.")
    return {
        "document_id": document_id,
        "status": job.status.value,
        "mode": job.mode,
        "ocr": job.ocr,
        "filename": job.filename,
        "error": job.error,
    }


@router.post("/compare")
async def compare_document(request: Request, body: CompareRequest) -> dict[str, Any]:
    """Process a sample under all six mode x OCR configs, each as its own variant doc."""
    source = _resolve_sample(body.filename)
    stem = _doc_id(body.filename)
    dest = _pdf_path(stem)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(source.read_bytes())

    variants = []
    for mode in _MODES:
        for ocr in _OCRS:
            variant = _variant_id(stem, mode, ocr)
            record = JobRecord(
                doc_id=variant, filename=body.filename, status="queued", mode=mode, ocr=ocr, source_path=str(dest)
            )
            set_job(_redis, record)
            await request.app.state.arq.enqueue_job("process_document_task", variant)
            variants.append({"id": variant, "mode": mode, "ocr": ocr, "status": "queued"})
    return {"stem": stem, "variants": variants}


@router.get("/compare/{stem}")
async def get_compare(stem: str) -> dict[str, Any]:
    """Return the status and chunk summary of every config variant for a file."""
    variants = []
    for mode in _MODES:
        for ocr in _OCRS:
            variant = _variant_id(stem, mode, ocr)
            job = get_job(_redis, variant)
            document = _repo.get(variant)
            summary = None
            if document is not None:
                summary = {
                    "num_chunks": len(document.chunks),
                    "by_kind": dict(Counter(c.kind for c in document.chunks)),
                }
            variants.append(
                {
                    "id": variant,
                    "mode": mode,
                    "ocr": ocr,
                    "status": job.status.value if job else None,
                    "error": job.error if job else None,
                    "summary": summary,
                }
            )
    return {"stem": stem, "variants": variants}


@router.get("")
async def list_documents() -> dict[str, list[str]]:
    """List stored document ids."""
    return {"documents": _repo.list_ids()}


@router.post("/search")
async def search_documents(request: SearchRequest) -> dict[str, Any]:
    """Vector-search stored chunks (RAG retrieval), optionally scoped to a document."""
    query_vector = _embedder.embed([request.query])[0]
    hits = _repo.search(query_vector, top_k=request.top_k, doc_id=request.document_id)
    return {"query": request.query, "hits": [hit.model_dump() for hit in hits]}


@router.get("/{document_id}")
async def get_document(document_id: str) -> dict[str, Any]:
    """Return document metadata: pages and chunk count."""
    document = _repo.get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {
        "id": document.id,
        "filename": document.filename,
        "num_pages": document.num_pages,
        "num_chunks": len(document.chunks),
        "pages": [page.model_dump() for page in document.pages],
    }


@router.get("/{document_id}/chunks")
async def get_chunks(document_id: str) -> dict[str, Any]:
    """Return the flat, reading-ordered chunk list (no embeddings)."""
    document = _repo.get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"document_id": document.id, "chunks": [chunk.model_dump() for chunk in document.chunks]}


@router.get("/{document_id}/file")
async def get_file(document_id: str) -> FileResponse:
    """Serve the stored source PDF for the viewer (variants share one stored PDF)."""
    job = get_job(_redis, document_id)
    source = Path(job.source_path) if job else _pdf_path(document_id)
    if not source.exists():
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(source, media_type="application/pdf")


@router.get("/{document_id}/chunks/{chunk_id}/image")
async def get_chunk_image(document_id: str, chunk_id: str) -> Response:
    """Serve a chunk's stored PNG image."""
    png = _repo.get_image(document_id, chunk_id)
    if png is None:
        raise HTTPException(status_code=404, detail="Image not found.")
    return Response(content=png, media_type="image/png")
