"""Page-by-page text extraction. Kept separate from table_extractor.py because
prose (explanatory notes) and tables need completely different handling."""
import fitz  # PyMuPDF


def extract_pages_text(pdf_path: str) -> list[dict]:
    """Returns [{"page_number": 1, "text": "..."}, ...]"""
    pages = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            text = page.get_text("text").strip()
            pages.append({"page_number": i + 1, "text": text})
    return pages


def get_pdf_title(pdf_path: str) -> str | None:
    with fitz.open(pdf_path) as doc:
        meta_title = doc.metadata.get("title")
        if meta_title:
            return meta_title
        # fallback: first non-empty line of page 1
        first_page_text = doc[0].get_text("text").strip()
        return first_page_text.splitlines()[0] if first_page_text else None
