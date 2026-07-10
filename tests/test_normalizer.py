"""Tests for the Docling normalizer.

These lock the behavior that matters for the viewer: reading-order flattening
(groups collapsed, pictures descended into), the bottom-left to top-left bbox
flip, furniture tagging, and normalized coordinates.
"""

import json
from pathlib import Path

import pytest

from app.core.models import NormalizedDocument
from app.core.normalizer import normalize_docling

MOCK = Path("benchmark/out/03_CAT_3406C_marine_propulsion_spec.json")


@pytest.fixture
def raw() -> dict:
    """Load one real Docling mock document."""
    return json.loads(MOCK.read_text())


@pytest.fixture
def doc(raw: dict) -> NormalizedDocument:
    """Normalize the mock once per test."""
    return normalize_docling(raw, doc_id="cat3406c", filename="03_CAT_3406C.pdf")


def test_returns_normalized_document(doc: NormalizedDocument) -> None:
    """The normalizer returns our contract type with pages and chunks."""
    assert isinstance(doc, NormalizedDocument)
    assert doc.num_pages == len(doc.pages) == 2
    assert len(doc.chunks) > 0


def test_flattens_groups(doc: NormalizedDocument) -> None:
    """List items nested in groups appear as chunks; groups are not chunks."""
    ids = {c.id for c in doc.chunks}
    assert "texts-5" in ids  # a list item nested inside groups/0
    assert not any(c.id.startswith("groups") for c in doc.chunks)


def test_descends_into_pictures(doc: NormalizedDocument) -> None:
    """Text overlaid on a picture (the 3406C title) is kept as a chunk."""
    assert any((c.text or "").strip() == "3406C" for c in doc.chunks)


def test_reading_order_is_dense_and_sorted(doc: NormalizedDocument) -> None:
    """Order is a gap-free 0..n-1 sequence in reading order."""
    assert [c.order for c in doc.chunks] == list(range(len(doc.chunks)))


def test_topleft_invariant(doc: NormalizedDocument) -> None:
    """Every bbox is top-left origin after the flip: t < b."""
    for c in doc.chunks:
        assert c.bbox.t < c.bbox.b


def test_title_near_top(doc: NormalizedDocument) -> None:
    """The 3406C title sits near the top of its page (small t after flip)."""
    title = next(c for c in doc.chunks if (c.text or "").strip() == "3406C")
    assert title.bbox.t < 100


def test_footer_near_bottom(doc: NormalizedDocument) -> None:
    """The copyright footer sits near the bottom (large t after flip)."""
    footer = next(c for c in doc.chunks if "Caterpillar" in (c.text or ""))
    page_h = next(p.height for p in doc.pages if p.page_no == footer.page_no)
    assert footer.bbox.t > page_h * 0.9


def test_furniture_tagged(doc: NormalizedDocument) -> None:
    """The copyright footer is tagged as furniture, not body."""
    footer = next(c for c in doc.chunks if "Caterpillar" in (c.text or ""))
    assert footer.content_layer == "furniture"


def test_bbox_norm_in_unit_range(doc: NormalizedDocument) -> None:
    """Normalized coordinates are all within 0..1."""
    for c in doc.chunks:
        for v in (c.bbox_norm.l, c.bbox_norm.t, c.bbox_norm.r, c.bbox_norm.b):
            assert 0.0 <= v <= 1.0


def test_table_chunk_has_grid(doc: NormalizedDocument) -> None:
    """A table chunk carries a populated grid of cell strings."""
    tables = [c for c in doc.chunks if c.kind == "table"]
    assert tables
    assert any(cell == "CONFIGURATION" for t in tables for row in t.table.grid for cell in row)
