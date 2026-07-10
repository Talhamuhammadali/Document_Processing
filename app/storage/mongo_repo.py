"""Mongo repository placeholder (not implemented this phase)."""

from app.core.models import NormalizedDocument, SearchHit
from app.storage.base import DocumentRepository

_MSG = "Mongo backend is a placeholder for this phase."


class MongoDocumentRepository(DocumentRepository):
    """Structural placeholder for a future Mongo backend."""

    def save(self, doc: NormalizedDocument, embeddings: dict[str, list[float]], images: dict[str, bytes]) -> None:
        """Not implemented."""
        raise NotImplementedError(_MSG)

    def get(self, doc_id: str) -> NormalizedDocument | None:
        """Not implemented."""
        raise NotImplementedError(_MSG)

    def exists(self, doc_id: str) -> bool:
        """Not implemented."""
        raise NotImplementedError(_MSG)

    def list_ids(self) -> list[str]:
        """Not implemented."""
        raise NotImplementedError(_MSG)

    def get_image(self, doc_id: str, chunk_id: str) -> bytes | None:
        """Not implemented."""
        raise NotImplementedError(_MSG)

    def search(self, query_vector: list[float], top_k: int = 5, doc_id: str | None = None) -> list[SearchHit]:
        """Not implemented."""
        raise NotImplementedError(_MSG)
