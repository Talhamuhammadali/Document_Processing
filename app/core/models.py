"""Schemas for the upload and processing of the documents."""

from typing import Literal

from pydantic import BaseModel, Field


class BBox(BaseModel):
    """Bounding box in top-left origin, in PDF points.

    Top-left origin means the y axis grows downward, so after normalization the
    invariant is t < b. l and r are the left and right edges.
    """

    l: float  # noqa: E741  (left edge; mirrors Docling's bbox naming)
    t: float
    r: float
    b: float


class Page(BaseModel):
    """A single page's number and size in PDF points."""

    page_no: int = Field(..., description="Page number of the document. Indexed from 1.")
    width: float = Field(..., description="Width of the page in PDF points.")
    height: float = Field(..., description="Height of the page in PDF points.")


class TableData(BaseModel):
    """A table flattened to a grid of cell strings (row-major)."""

    num_rows: int = Field(..., description="Number of rows in the table.")
    num_cols: int = Field(..., description="Number of columns in the table.")
    grid: list[list[str]] = Field(..., description="Row-major grid of cell strings.")


class Chunk(BaseModel):
    """One normalized content unit: a text block, table, or picture.

    kind is the coarse three-way category and decides which optional payload
    (text or table) is populated. label is Docling's fine-grained tag (for
    example section_header or list_item) kept for frontend styling.
    content_layer distinguishes real body content from page furniture (headers
    and footers) so the frontend can dim or toggle it.
    group_id ties chunks that share a Docling structural group (a list or inline
    run) so the frontend can cluster them into one card.
    """

    id: str = Field(..., description="Unique identifier for the chunk.")
    order: int = Field(..., description="Order of the chunk in the document.")
    kind: Literal["text", "table", "picture"] = Field(..., description="Type of the chunk.")
    label: str = Field(..., description="Docling's fine-grained tag for the chunk.")
    content_layer: Literal["body", "furniture", "notes"] = Field(..., description="Content layer of the chunk.")
    group_id: str | None = Field(None, description="Id of the Docling group this chunk belongs to, if any.")
    group_label: str | None = Field(None, description="Label of the Docling group, for example list or inline.")
    page_no: int = Field(..., description="Page number where the chunk is located. Indexed from 1.")
    bbox: BBox = Field(..., description="Bounding box of the chunk in PDF points.")
    bbox_norm: BBox = Field(..., description="Normalized bounding box of the chunk in PDF points.")
    text: str | None = Field(None, description="Text content of the chunk, if applicable.")
    table: TableData | None = Field(None, description="Table content of the chunk, if applicable.")
    image_ref: str | None = Field(
        None,
        description="URL to fetch the image for this chunk. Set for picture chunks only.",
    )
    description: str | None = Field(
        None,
        description="Generated natural-language description of the chunk's image, if any.",
    )


class NormalizedDocument(BaseModel):
    """A full document normalized from Docling output."""

    id: str = Field(..., description="Unique identifier for the document.")
    filename: str = Field(..., description="Filename of the document.")
    num_pages: int = Field(..., description="Number of pages in the document.")
    pages: list[Page] = Field(..., description="List of pages in the document.")
    chunks: list[Chunk] = Field(..., description="List of chunks in the document.")


class SearchHit(BaseModel):
    """A single vector-search result, for RAG retrieval."""

    doc_id: str = Field(..., description="Document id the matching chunk belongs to.")
    chunk_id: str = Field(..., description="Id of the matching chunk.")
    score: float = Field(..., description="Similarity score; higher is more similar.")
    chunk: Chunk = Field(..., description="The matching chunk.")
