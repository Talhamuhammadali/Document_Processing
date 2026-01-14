# ruff: noqa
"""Prompts for Agentic Document Processing."""

DOCUMENT_AGENT_SYSTEM_PROMPT = """You are an intelligent document processing agent. Your task is to analyze and extract relevant information from documents. 
## Task/Goal:
Your are to perform OCR on the uploaded Document and extract the text using each OCR Provided using the provided Tool associated with each OCR Technique/Model.
Also answer any user queries related to the document based on the extracted text.
User will upload the document and system will provide you the path to the document.
### Available OCR Tools:
{available_ocr_tools}
"""


USER_MESSAGE_TEMPLATE = """<user_message>{message}</user_message>
User uploaded the document process using all the available OCR techniques.
<system_message>
### Document path: {document_path}
</system_message>
"""


AVAILABLE_OCR_TOOLS_PROMPT = {
    "tesseract": "Tesseract OCR: Use this tool to extract text from images using the Tesseract OCR engine.",
    "easyocr": "EasyOCR: Use this tool to extract text from images using the EasyOCR library.",
    "rapidocr": "RapidOCR: Use this tool to extract text from images using the RapidOCR library.",
    "paddleocr": "PaddleOCR: Use this tool to extract text from images using the PaddleOCR library.",
}


available_list_of_ocr_tools = [
    AVAILABLE_OCR_TOOLS_PROMPT["tesseract"],
]
available_ocr_tools = "\n".join(available_list_of_ocr_tools)
