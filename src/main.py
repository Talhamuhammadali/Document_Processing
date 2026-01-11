"""Main module for document processing."""

import torch
from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument

print("Torch version:", torch.__version__)
print("Cuda available:", torch.cuda.is_available())
print("Cuda device count:", torch.cuda.device_count())
print("Cuda Version:", torch.version.cuda)

if __name__ == "__main__":
    from pprint import pprint

    print("Exploring docling document type")
    pprint(DoclingDocument, indent=2)
    converter = DocumentConverter()
    file_path = "data/document.pdf"
    result = converter.convert(file_path)
    with open("data/processed_doc.json", "w") as f:
        f.write(result.document.model_dump_json(indent=4))
