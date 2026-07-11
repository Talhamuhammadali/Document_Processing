"""Assemble a stored document from a converted Docling document."""

from docling_core.types.doc import ContentLayer, DoclingDocument
from docling_core.types.doc.document import PictureItem

from app.core.embedder import Embedder, FakeEmbedder
from app.core.image_extractor import picture_png_bytes
from app.core.models import Chunk, NormalizedDocument
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


def _searchable_text(chunk: Chunk) -> str:
    """Return the text used to embed a chunk before captions exist.

    Pictures embed empty (a later captioning job backfills them); tables embed
    their flattened cell text; text chunks embed their text.
    """
    if chunk.kind == "table" and chunk.table is not None:
        return " ".join(cell for row in chunk.table.grid for cell in row)
    return chunk.text or ""


def process_document(
    document_docling: DoclingDocument,
    doc_id: str,
    filename: str,
    embedder: Embedder | None = None,
) -> tuple[NormalizedDocument, dict[str, list[float]], dict[str, bytes]]:
    """Normalize, extract picture images, and embed a converted Docling document.

    Descriptions are left unset; a background captioning job (out of scope) will
    backfill them and re-embed picture chunks.

    Parameters
    ----------
    document_docling : DoclingDocument
        The converted Docling document.
    doc_id : str
        Stable identifier for the document.
    filename : str
        Original filename.
    embedder : Embedder | None
        Embedder to use; defaults to FakeEmbedder.

    Returns
    -------
    tuple[NormalizedDocument, dict[str, list[float]], dict[str, bytes]]
        The document (with image_ref populated), a chunk-id to embedding map, and
        a chunk-id to PNG image map.

    """
    embedder = embedder or FakeEmbedder()

    document = normalize_docling(document_docling, doc_id, filename)
    picture_items = {
        to_chunk_id(item.self_ref): item
        for item, _level in document_docling.iterate_items(included_content_layers=_LAYERS, traverse_pictures=True)
        if isinstance(item, PictureItem)
    }

    embeddings: dict[str, list[float]] = {}
    images: dict[str, bytes] = {}
    for chunk in document.chunks:
        if chunk.kind == "picture":
            item = picture_items.get(chunk.id)
            png = picture_png_bytes(item, document_docling) if item is not None else None
            if png is not None:
                images[chunk.id] = png
                chunk.image_ref = image_url(doc_id, chunk.id)

        embeddings[chunk.id] = embedder.embed([_searchable_text(chunk)])[0]

    return document, embeddings, images
