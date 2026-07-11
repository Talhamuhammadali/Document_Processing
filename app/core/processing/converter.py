"""Build a Docling converter from a processing config and an OCR engine choice."""

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
    RapidOcrOptions,
    TableFormerMode,
    TableStructureOptions,
    TesseractCliOcrOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption

from app.core.processing.types import OcrEngine, ProcessingConfig

_OCR_ENGINES = {
    "tesseract": TesseractCliOcrOptions,
    "rapidocr": RapidOcrOptions,
}


def build_converter(config: ProcessingConfig, ocr: OcrEngine) -> DocumentConverter:
    """Construct a Docling PDF converter for a preset with a chosen OCR engine.

    Parameters
    ----------
    config : ProcessingConfig
        The pipeline preset to apply.
    ocr : OcrEngine
        The OCR engine to run, or "none" to disable OCR.

    Returns
    -------
    DocumentConverter
        A converter configured for the given preset and OCR choice.

    """
    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=config.num_threads, device=AcceleratorDevice.CPU
    )
    pipeline_options.generate_picture_images = True
    pipeline_options.images_scale = config.images_scale
    pipeline_options.do_table_structure = config.do_table_structure
    pipeline_options.table_structure_options = TableStructureOptions(mode=TableFormerMode(config.table_mode))
    pipeline_options.do_ocr = ocr != "none"
    if ocr != "none":
        pipeline_options.ocr_options = _OCR_ENGINES[ocr]()

    return DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)})
