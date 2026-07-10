"""Provide the active document repository."""

from functools import lru_cache

from app.storage.base import DocumentRepository
from app.storage.redis_repo import RedisDocumentRepository


@lru_cache(maxsize=1)
def get_repository() -> DocumentRepository:
    """Return the process-wide document repository (Redis Stack).

    Returns
    -------
    DocumentRepository
        The Redis-backed repository. Mongo remains a placeholder and is not
        wired in this phase.
    """
    return RedisDocumentRepository()
