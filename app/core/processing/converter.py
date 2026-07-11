"""Build a Docling converter from a processing config and OCR toggle."""

from typing import Literal

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    EasyOcrOptions,
    PdfPipelineOptions,
    RapidOcrOptions,
    TableFormerMode,
    TableStructureOptions,
    TesseractCliOcrOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from pydantic import BaseModel

_OCR_ENGINES = {
    "tesseract": TesseractCliOcrOptions,
    "rapidocr": RapidOcrOptions,
    "easyocr": EasyOcrOptions,
}


class ProcessingConfig(BaseModel):
    """A named Docling pipeline preset shared by the worker and the benchmark.

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
    ocr_engine : Literal["tesseract", "rapidocr", "easyocr"]
        OCR engine used when OCR is enabled for a job.

    """

    table_mode: Literal["fast", "accurate"]
    do_table_structure: bool
    images_scale: float
    num_threads: int
    ocr_engine: Literal["tesseract", "rapidocr", "easyocr"]


def build_converter(config: ProcessingConfig, ocr: bool) -> DocumentConverter:
    """Construct a Docling PDF converter for a preset with OCR on or off.

    Parameters
    ----------
    config : ProcessingConfig
        The pipeline preset to apply.
    ocr : bool
        Whether to enable OCR; the engine is taken from config.ocr_engine.

    Returns
    -------
    DocumentConverter
        A converter configured for the given preset.

    """
    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=config.num_threads, device=AcceleratorDevice.CPU
    )
    pipeline_options.generate_picture_images = True
    pipeline_options.images_scale = config.images_scale
    pipeline_options.do_table_structure = config.do_table_structure
    pipeline_options.table_structure_options = TableStructureOptions(mode=TableFormerMode(config.table_mode))
    pipeline_options.do_ocr = ocr
    if ocr:
        pipeline_options.ocr_options = _OCR_ENGINES[config.ocr_engine]()

    return DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)})
