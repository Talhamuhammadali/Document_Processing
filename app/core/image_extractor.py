"""Extract embedded picture images from a Docling document."""

import io

from docling_core.types.doc import DoclingDocument
from docling_core.types.doc.document import PictureItem


def picture_png_bytes(item: PictureItem, doc: DoclingDocument) -> bytes | None:
    """Return a picture's embedded image encoded as PNG bytes, or None if absent.

    Parameters
    ----------
    item : PictureItem
        The Docling picture item.
    doc : DoclingDocument
        The document the item belongs to (get_image resolves the image against it).

    Returns
    -------
    bytes | None
        PNG-encoded image bytes, or None when the picture has no embedded image.

    """
    pil = item.get_image(doc)
    if pil is None:
        return None
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return buf.getvalue()
