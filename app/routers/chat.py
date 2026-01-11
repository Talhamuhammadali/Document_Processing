"""Chat with document endpoints (SSE)."""

from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/chat", tags=["chat"])


async def event_stream(document_id: str, query: str) -> AsyncGenerator[str]:
    """Generate SSE events for chat responses."""
    # TODO: Implement chat logic with AsyncIO background tasks
    # Example SSE format:
    # yield f"data: {json.dumps({'message': 'chunk'})}\n\n"
    yield "data: Chat endpoint not implemented yet\n\n"


@router.get("/stream/{document_id}")
async def chat_stream(document_id: str, query: str) -> StreamingResponse:
    """Chat with a document using SSE."""
    return StreamingResponse(
        event_stream(document_id, query),
        media_type="text/event-stream",
    )
