"""Redis Stack repository: RedisJSON documents, image blobs, and vector search."""

import struct
from typing import cast

import redis
from redis.commands.search.field import TagField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from app.core.config import settings
from app.core.models import Chunk, NormalizedDocument, SearchHit
from app.storage.base import DocumentRepository

_VEC_DIM = 384
_INDEX = "chunk_idx"
_VEC_PREFIX = "vec:"


class RedisDocumentRepository(DocumentRepository):
    """Stores normalized documents, chunk embeddings, and images in Redis Stack."""

    def __init__(self) -> None:
        """Create Redis clients; the vector index is created lazily on first save."""
        self._r = self._client(decode_responses=True)
        self._rb = self._client(decode_responses=False)
        self._index_ready = False

    @staticmethod
    def _client(decode_responses: bool) -> redis.Redis:
        """Build a Redis client from settings credentials."""
        return redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db,
            decode_responses=decode_responses,
        )

    def _ensure_index(self) -> None:
        """Create the RediSearch vector index once (idempotent)."""
        if self._index_ready:
            return
        try:
            self._r.ft(_INDEX).create_index(
                fields=[
                    TagField("doc_id"),
                    VectorField(
                        "vector",
                        "FLAT",
                        {"TYPE": "FLOAT32", "DIM": _VEC_DIM, "DISTANCE_METRIC": "COSINE"},
                    ),
                ],
                definition=IndexDefinition(prefix=[_VEC_PREFIX], index_type=IndexType.HASH),
            )
        except redis.ResponseError:
            pass  # index already exists
        self._index_ready = True

    def save(
        self,
        doc: NormalizedDocument,
        embeddings: dict[str, list[float]],
        images: dict[str, bytes],
    ) -> None:
        """Persist the document JSON, chunk vectors, and chunk images."""
        self._ensure_index()
        self._r.json().set(f"doc:{doc.id}", "$", doc.model_dump())
        for chunk_id, vector in embeddings.items():
            self._rb.hset(
                f"{_VEC_PREFIX}{doc.id}:{chunk_id}",
                mapping={"doc_id": doc.id, "vector": struct.pack(f"{len(vector)}f", *vector)},
            )
        for chunk_id, png in images.items():
            self._rb.set(f"img:{doc.id}:{chunk_id}", png)

    def get(self, doc_id: str) -> NormalizedDocument | None:
        """Return the stored document, or None."""
        raw = self._r.json().get(f"doc:{doc_id}")
        return NormalizedDocument.model_validate(raw) if raw else None

    def exists(self, doc_id: str) -> bool:
        """Return whether the document is stored."""
        return bool(self._r.exists(f"doc:{doc_id}"))

    def list_ids(self) -> list[str]:
        """Return all stored document ids."""
        keys = cast("list[str]", self._r.keys("doc:*"))
        return [key.split(":", 1)[1] for key in keys]

    def get_image(self, doc_id: str, chunk_id: str) -> bytes | None:
        """Return a stored chunk image, or None."""
        return cast("bytes | None", self._rb.get(f"img:{doc_id}:{chunk_id}"))

    def search(self, query_vector: list[float], top_k: int = 5, doc_id: str | None = None) -> list[SearchHit]:
        """Run a KNN vector search, optionally scoped to one document."""
        self._ensure_index()
        vec = struct.pack(f"{len(query_vector)}f", *query_vector)
        prefilter = f"@doc_id:{{{doc_id}}}" if doc_id else "*"
        query = (
            Query(f"({prefilter})=>[KNN {top_k} @vector $vec AS score]")
            .sort_by("score")
            .return_fields("score")
            .dialect(2)
        )
        result = self._r.ft(_INDEX).search(query, query_params={"vec": vec})

        hits: list[SearchHit] = []
        doc_cache: dict[str, NormalizedDocument | None] = {}
        for row in result.docs:
            _, hit_doc_id, chunk_id = row.id.split(":", 2)
            document = doc_cache.setdefault(hit_doc_id, self.get(hit_doc_id))
            chunk = _find_chunk(document, chunk_id)
            if chunk is None:
                continue
            hits.append(
                SearchHit(doc_id=hit_doc_id, chunk_id=chunk_id, score=1.0 - float(row.score), chunk=chunk)
            )
        return hits


def _find_chunk(document: NormalizedDocument | None, chunk_id: str) -> Chunk | None:
    """Return the chunk with the given id from a document, or None."""
    if document is None:
        return None
    return next((c for c in document.chunks if c.id == chunk_id), None)
