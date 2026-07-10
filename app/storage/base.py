"""Repository interface for normalized documents."""

from abc import ABC, abstractmethod

from app.core.models import NormalizedDocument, SearchHit


class DocumentRepository(ABC):
    """Persists and retrieves normalized documents, chunk embeddings, and images."""

    @abstractmethod
    def save(
        self,
        doc: NormalizedDocument,
        embeddings: dict[str, list[float]],
        images: dict[str, bytes],
    ) -> None:
        """Store a document with its chunk embeddings and images.

        Parameters
        ----------
        doc : NormalizedDocument
            The normalized document to store.
        embeddings : dict[str, list[float]]
            Mapping of chunk id to embedding vector.
        images : dict[str, bytes]
            Mapping of chunk id to PNG image bytes (picture chunks only).

        """

    @abstractmethod
    def get(self, doc_id: str) -> NormalizedDocument | None:
        """Return a stored document, or None if absent.

        Parameters
        ----------
        doc_id : str
            The document id.

        Returns
        -------
        NormalizedDocument | None
            The document, or None.

        """

    @abstractmethod
    def exists(self, doc_id: str) -> bool:
        """Return whether a document id is stored.

        Parameters
        ----------
        doc_id : str
            The document id.

        Returns
        -------
        bool
            True if stored.

        """

    @abstractmethod
    def list_ids(self) -> list[str]:
        """Return all stored document ids.

        Returns
        -------
        list[str]
            The stored document ids.

        """

    @abstractmethod
    def get_image(self, doc_id: str, chunk_id: str) -> bytes | None:
        """Return a stored chunk image, or None if absent.

        Parameters
        ----------
        doc_id : str
            The document id.
        chunk_id : str
            The chunk id.

        Returns
        -------
        bytes | None
            PNG image bytes, or None.

        """

    @abstractmethod
    def search(self, query_vector: list[float], top_k: int = 5, doc_id: str | None = None) -> list[SearchHit]:
        """Find the chunks whose embeddings are most similar to a query vector.

        Parameters
        ----------
        query_vector : list[float]
            The query embedding.
        top_k : int
            Maximum number of hits to return.
        doc_id : str | None
            If given, restrict the search to this document; otherwise search all.

        Returns
        -------
        list[SearchHit]
            Ranked hits, most similar first.

        """
