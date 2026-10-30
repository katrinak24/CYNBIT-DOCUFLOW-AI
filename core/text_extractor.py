from pathlib import Path
import fitz
from PIL import Image
import pytesseract
import io

def extract_text(filename: str, file_bytes: bytes) -> tuple[str, str]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = [page.get_text("text") for page in doc]
        text = "\n".join(pages).strip()
        if text:
            return text, "pdf_text"
        # Scanned PDF fallback: render pages and OCR them.
        ocr_parts = []
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_parts.append(pytesseract.image_to_string(image))
        return "\n".join(ocr_parts).strip(), "pdf_ocr"
    image = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(image).strip(), "image_ocr"
