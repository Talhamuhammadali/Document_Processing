"""Transform a Docling document into our NormalizedDocument contract."""

from typing import Literal, cast

from docling_core.types.doc import ContentLayer, DoclingDocument
from docling_core.types.doc.document import NodeItem, PictureItem, TableItem, TextItem

from app.core.models import BBox, Chunk, NormalizedDocument, Page, TableData

_LAYERS = {ContentLayer.BODY, ContentLayer.FURNITURE, ContentLayer.NOTES}


def clean_prefix(s: str, prefix: str) -> str:
    """Remove a prefix from a string, if present.

    Parameters
    ----------
    s : str
        The string to clean.
    prefix : str
        The prefix to remove.

    Returns
    -------
    str
        The string with the prefix removed, or the original string if the
        prefix was not present.

    """
    return s.removeprefix(prefix)


def get_chunk_kind(item: NodeItem) -> Literal["text", "table", "picture"]:
    """Determine the kind of a Docling item.

    Parameters
    ----------
    item : NodeItem
        The Docling item to classify.

    Returns
    -------
    str
        The kind of the item: text, table, or picture.

    Raises
    ------
    ValueError
        If the item is not a text, table, or picture item.

    """
    if isinstance(item, TextItem):
        return "text"
    if isinstance(item, TableItem):
        return "table"
    if isinstance(item, PictureItem):
        return "picture"
    raise ValueError(f"Unknown item type: {type(item)}")


def normalize_docling(raw: dict, doc_id: str, filename: str) -> NormalizedDocument:
    """Normalize a raw Docling document dict into a NormalizedDocument.

    Parameters
    ----------
    raw : dict
        The Docling document JSON (as loaded from a mock or a real run).
    doc_id : str
        Stable identifier to assign to the resulting document.
    filename : str
        Original filename, carried through for display.

    Returns
    -------
    NormalizedDocument
        A flat, reading-ordered document with top-left, normalized bboxes.

    """
    document = DoclingDocument.model_validate(raw)

    pages: list[Page] = []
    page_size_lookup: dict[int, tuple[float, float]] = {}
    for page_item in document.pages.values():
        page = Page(
            page_no=page_item.page_no,
            width=page_item.size.width,
            height=page_item.size.height,
        )
        pages.append(page)
        page_size_lookup[page.page_no] = (page.width, page.height)

    chunks: list[Chunk] = []
    order = 0
    for item, _level in document.iterate_items(included_content_layers=_LAYERS, traverse_pictures=True):
        # Only text, table, and picture items become chunks; skip anything else
        # so the reading order stays gap-free.
        if not isinstance(item, (TextItem, TableItem, PictureItem)):
            continue

        prov = item.prov[0]
        width, height = page_size_lookup[prov.page_no]
        tl = prov.bbox.to_top_left_origin(page_height=height)

        chunks.append(
            Chunk(
                id=clean_prefix(item.self_ref, "#/").replace("/", "-"),
                order=order,
                kind=get_chunk_kind(item),
                label=str(item.label),
                content_layer=cast(Literal["body", "furniture", "notes"], item.content_layer.value),
                page_no=prov.page_no,
                bbox=BBox(l=tl.l, t=tl.t, r=tl.r, b=tl.b),
                bbox_norm=BBox(
                    l=tl.l / width,
                    t=tl.t / height,
                    r=tl.r / width,
                    b=tl.b / height,
                ),
                text=item.text if isinstance(item, TextItem) else None,
                table=(
                    TableData(
                        num_rows=item.data.num_rows,
                        num_cols=item.data.num_cols,
                        grid=[[cell.text for cell in row] for row in item.data.grid],
                    )
                    if isinstance(item, TableItem)
                    else None
                ),
            )
        )
        order += 1

    return NormalizedDocument(
        id=doc_id,
        filename=filename,
        num_pages=len(pages),
        pages=pages,
        chunks=chunks,
    )
