"""Tests for the picture image extractor.

Uses a synthetic DoclingDocument with an embedded image (via ImageRef.from_pil)
so the tests are self-contained and do not depend on regenerated benchmark
samples or any model download.
"""

from docling_core.types.doc import DoclingDocument
from docling_core.types.doc.document import ImageRef
from PIL import Image

from app.core.image_extractor import picture_png_bytes

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _doc_with_picture(image: Image.Image | None) -> tuple[DoclingDocument, object]:
    """Build a synthetic doc holding one picture, with or without an embedded image."""
    doc = DoclingDocument(name="synthetic")
    ref = ImageRef.from_pil(image, dpi=144) if image is not None else None
    pic = doc.add_picture(image=ref)
    return doc, pic


def test_picture_png_bytes_returns_png() -> None:
    """A picture with an embedded image yields valid PNG bytes."""
    doc, pic = _doc_with_picture(Image.new("RGB", (20, 10), (255, 0, 0)))
    out = picture_png_bytes(pic, doc)
    assert out is not None
    assert out[:8] == _PNG_MAGIC


def test_picture_without_image_returns_none() -> None:
    """A picture with no embedded image returns None (nothing to store)."""
    doc, pic = _doc_with_picture(None)
    assert picture_png_bytes(pic, doc) is None
