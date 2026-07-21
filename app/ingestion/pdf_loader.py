"""Page-by-page text extraction. Kept separate from table_extractor.py because
prose (explanatory notes) and tables need completely different handling.

Includes an OCR fallback: if a page's normal text layer is empty or near-empty
(common for scanned/eOffice-generated circulars), it renders that page to an
image and runs Tesseract OCR on it instead of silently skipping the page."""
import fitz  # PyMuPDF
from app.config import settings

try:
    import pytesseract
    from PIL import Image
    import io
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

MIN_TEXT_LENGTH_BEFORE_OCR = 20  # pages with less text than this are treated as scanned


def _ocr_page(page: "fitz.Page") -> str:
    """Renders a page to an image and runs Tesseract OCR on it."""
    if not OCR_AVAILABLE:
        return ""
    try:
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(img).strip()
    except Exception as e:
        print(f"    OCR failed on page: {e}")
        return ""


def extract_pages_text(pdf_path: str) -> list[dict]:
    """Returns [{"page_number": 1, "text": "...", "ocr_used": False}, ...]"""
    pages = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            text = page.get_text("text").strip()
            ocr_used = False

            if len(text) < MIN_TEXT_LENGTH_BEFORE_OCR:
                ocr_text = _ocr_page(page)
                if len(ocr_text) > len(text):
                    text = ocr_text
                    ocr_used = True

            pages.append({"page_number": i + 1, "text": text, "ocr_used": ocr_used})
    return pages


def get_pdf_title(pdf_path: str) -> str | None:
    with fitz.open(pdf_path) as doc:
        meta_title = doc.metadata.get("title")
        if meta_title:
            return meta_title
        # fallback: first non-empty line of page 1
        first_page_text = doc[0].get_text("text").strip()
        return first_page_text.splitlines()[0] if first_page_text else None
