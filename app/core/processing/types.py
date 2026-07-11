"""Lightweight processing-config types shared by the API and the worker (no Docling import)."""

from typing import Literal

from pydantic import BaseModel

OcrEngine = Literal["none", "tesseract", "rapidocr"]


class ProcessingConfig(BaseModel):
    """A named Docling pipeline preset shared by the worker and the benchmark.

    OCR is orthogonal to the preset: the engine is chosen per job, not per mode.

    Attributes
    ----------
    table_mode : Literal["fast", "accurate"]
        TableFormer structure-model mode.
    do_table_structure : bool
        Whether to run the table-structure model at all.
    images_scale : float
        Resolution multiplier for generated picture images.
    num_threads : int
        Accelerator thread budget.

    """

    table_mode: Literal["fast", "accurate"]
    do_table_structure: bool
    images_scale: float
    num_threads: int
