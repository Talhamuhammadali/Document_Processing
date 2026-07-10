"""Embedding interface and a deterministic fake implementation."""

import hashlib
import math
from abc import ABC, abstractmethod


class Embedder(ABC):
    """Turns text into fixed-length embedding vectors."""

    dim: int

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts.

        Parameters
        ----------
        texts : list[str]
            The texts to embed.

        Returns
        -------
        list[list[float]]
            One vector of length dim per input text.

        """


class FakeEmbedder(Embedder):
    """Deterministic hash-seeded embedder that needs no model."""

    def __init__(self, dim: int = 384) -> None:
        """Initialize the embedder.

        Parameters
        ----------
        dim : int
            Length of the produced vectors.

        """
        self.dim = dim

    def _one(self, text: str) -> list[float]:
        """Produce a single deterministic unit vector for one text."""
        vals: list[float] = []
        counter = 0
        while len(vals) < self.dim:
            digest = hashlib.sha256(text.encode() + counter.to_bytes(4, "little")).digest()
            vals.extend(b / 255.0 for b in digest)
            counter += 1
        vals = vals[: self.dim]
        norm = math.sqrt(sum(v * v for v in vals)) or 1.0
        return [v / norm for v in vals]

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed each text into a deterministic unit vector."""
        return [self._one(t) for t in texts]
