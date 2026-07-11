"""Document processing endpoints."""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from app.core.embedder import FakeEmbedder
from app.core.mock_index import build_index, match
from app.core.pipeline import process_document
from app.storage.factory import get_repository

router = APIRouter(prefix="/documents", tags=["documents"])

_repo = get_repository()
_embedder = FakeEmbedder()


class SearchRequest(BaseModel):
    """A RAG search request."""

    query: str
    top_k: int = 5
    document_id: str | None = None


class OpenRequest(BaseModel):
    """A request to open a sample document by filename."""

    filename: str


def _process_and_store(filename: str) -> str:
    """Match a filename to a mock, process and store it if new, and return its id."""
    entry = match(filename)
    if entry is None:
        raise HTTPException(status_code=404, detail="No mock available for this file.")
    doc_id = Path(filename).stem
    if not _repo.exists(doc_id):
        raw = json.loads(entry.mock_json_path.read_text())
        document, embeddings, images = process_document(raw, doc_id, filename)
        _repo.save(document, embeddings, images)
    return doc_id


def _summary(doc_id: str) -> dict[str, Any]:
    """Return a short summary of a stored document."""
    document = _repo.get(doc_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {
        "document_id": document.id,
        "filename": document.filename,
        "num_pages": document.num_pages,
        "num_chunks": len(document.chunks),
    }


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict[str, Any]:
    """Upload a PDF, match it to a mock, process it, and store the result."""
    return _summary(_process_and_store(file.filename or ""))


@router.get("/available")
async def list_available() -> dict[str, Any]:
    """List sample documents in the data folder that have a precomputed mock."""
    processed = set(_repo.list_ids())
    return {
        "available": [
            {"id": Path(name).stem, "filename": name, "processed": Path(name).stem in processed}
            for name in build_index()
        ]
    }


@router.post("/open")
async def open_document(request: OpenRequest) -> dict[str, Any]:
    """Open a sample document by filename, processing and storing it on first use."""
    return _summary(_process_and_store(request.filename))


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
    """Serve the original PDF for the viewer."""
    entry = match(f"{document_id}.pdf")
    if entry is None or not entry.pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(entry.pdf_path, media_type="application/pdf")


@router.get("/{document_id}/chunks/{chunk_id}/image")
async def get_chunk_image(document_id: str, chunk_id: str) -> Response:
    """Serve a chunk's stored PNG image."""
    png = _repo.get_image(document_id, chunk_id)
    if png is None:
        raise HTTPException(status_code=404, detail="Image not found.")
    return Response(content=png, media_type="image/png")
