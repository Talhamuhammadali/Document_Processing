"""Document processing endpoints."""

from typing import Any

from fastapi import APIRouter, File, UploadFile

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict[str, str]:
    """Upload and process a document."""
    # TODO: Implement document processing logic
    return {"filename": file.filename, "status": "processing"}


@router.get("/chunks/{document_id}")
async def get_chunks(document_id: str) -> dict[str, Any]:
    """Get processed chunks for a document (optional endpoint)."""
    # TODO: Implement chunk retrieval logic
    return {"document_id": document_id, "chunks": []}
