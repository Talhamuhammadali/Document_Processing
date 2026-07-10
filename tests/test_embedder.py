"""Tests for the fake embedder."""

import math

from app.core.embedder import FakeEmbedder


def test_dim() -> None:
    """Each embedding has the configured dimension."""
    out = FakeEmbedder(dim=384).embed(["hello"])
    assert len(out) == 1
    assert len(out[0]) == 384


def test_deterministic() -> None:
    """The same text always embeds to the same vector."""
    emb = FakeEmbedder()
    assert emb.embed(["same text"]) == emb.embed(["same text"])


def test_different_text_differs() -> None:
    """Different texts embed to different vectors."""
    emb = FakeEmbedder()
    assert emb.embed(["a"])[0] != emb.embed(["b"])[0]


def test_unit_norm() -> None:
    """Vectors are unit-normalized."""
    vec = FakeEmbedder(dim=16).embed(["x"])[0]
    assert abs(math.sqrt(sum(c * c for c in vec)) - 1.0) < 1e-9
