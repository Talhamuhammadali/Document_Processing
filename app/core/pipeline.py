"""Assemble a stored document from a raw Docling mock."""

from docling_core.types.doc import ContentLayer, DoclingDocument
from docling_core.types.doc.document import PictureItem

from app.core.describer import Describer, FakeDescriber
from app.core.embedder import Embedder, FakeEmbedder
from app.core.image_extractor import picture_png_bytes
from app.core.models import NormalizedDocument, TableData
from app.core.normalizer import normalize_docling, to_chunk_id

_LAYERS = {ContentLayer.BODY, ContentLayer.FURNITURE}


def image_url(doc_id: str, chunk_id: str) -> str:
    """Return the API URL that serves a chunk's image.

    Parameters
    ----------
    doc_id : str
        The document id.
    chunk_id : str
        The chunk id.

    Returns
    -------
    str
        The relative URL for the chunk image endpoint.

    """
    return f"/documents/{doc_id}/chunks/{chunk_id}/image"


def table_to_markdown(table: TableData) -> str:
    """Render a table's grid as a simple pipe-delimited markdown string.

    Parameters
    ----------
    table : TableData
        The table to render.

    Returns
    -------
    str
        A markdown-ish representation of the table.

    """
    return "\n".join("| " + " | ".join(row) + " |" for row in table.grid)


def process_document(
    raw: dict,
    doc_id: str,
    filename: str,
    embedder: Embedder | None = None,
    describer: Describer | None = None,
) -> tuple[NormalizedDocument, dict[str, list[float]], dict[str, bytes]]:
    """Normalize, embed, extract picture images, and describe a document.

    Parameters
    ----------
    raw : dict
        The raw Docling document JSON.
    doc_id : str
        Stable identifier for the document.
    filename : str
        Original filename.
    embedder : Embedder | None
        Embedder to use; defaults to FakeEmbedder.
    describer : Describer | None
        Describer to use; defaults to FakeDescriber.

    Returns
    -------
    tuple[NormalizedDocument, dict[str, list[float]], dict[str, bytes]]
        The document (with image_ref and description populated), a chunk-id to
        embedding map, and a chunk-id to PNG image map.

    """
    embedder = embedder or FakeEmbedder()
    describer = describer or FakeDescriber()

    document = normalize_docling(raw, doc_id, filename)
    docling_doc = DoclingDocument.model_validate(raw)
    picture_items = {
        to_chunk_id(item.self_ref): item
        for item, _level in docling_doc.iterate_items(included_content_layers=_LAYERS, traverse_pictures=True)
        if isinstance(item, PictureItem)
    }

    embeddings: dict[str, list[float]] = {}
    images: dict[str, bytes] = {}
    for chunk in document.chunks:
        if chunk.kind == "picture":
            item = picture_items.get(chunk.id)
            png = picture_png_bytes(item, docling_doc) if item is not None else None
            if png is not None:
                images[chunk.id] = png
                chunk.image_ref = image_url(doc_id, chunk.id)
                chunk.description = describer.describe_image(png)
        elif chunk.kind == "table" and chunk.table is not None:
            chunk.description = describer.describe_table(table_to_markdown(chunk.table))

        searchable = chunk.text or chunk.description or ""
        embeddings[chunk.id] = embedder.embed([searchable])[0]

    return document, embeddings, images
