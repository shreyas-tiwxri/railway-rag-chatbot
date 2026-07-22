import os
from app.ingestion.pdf_loader import extract_pages_text, get_pdf_title
from app.ingestion.office_loader import (
    extract_docx_pages, extract_pptx_pages, extract_xlsx_pages, extract_url_page,
)
from app.ingestion.table_extractor import extract_rate_tables_from_pdf
from app.ingestion.chunker import chunk_document
from app.vectorstore.chroma_store import add_chunks
from app.db.models import SessionLocal, Document, RateTableRow

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx"}


def _extract_pages(file_path: str) -> list[dict]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_pages_text(file_path)
    elif ext == ".docx":
        return extract_docx_pages(file_path)
    elif ext == ".pptx":
        return extract_pptx_pages(file_path)
    elif ext == ".xlsx":
        return extract_xlsx_pages(file_path)
    raise ValueError(f"Unsupported file type: {ext}")


def already_ingested(filename: str) -> bool:
    session = SessionLocal()
    try:
        existing = (
            session.query(Document)
            .filter(Document.filename == filename, Document.status == "done")
            .first()
        )
        return existing is not None
    finally:
        session.close()


def ingest_pdf(file_path: str, source_url: str | None = None) -> dict:
    """Handles any supported file type (PDF, Word, PowerPoint, Excel) - the
    name is kept as ingest_pdf for backward compatibility with existing
    callers, but dispatch happens in _extract_pages() based on extension."""
    session = SessionLocal()
    filename = os.path.basename(file_path)
    ext = os.path.splitext(file_path)[1].lower()

    doc_record = Document(filename=filename, source_url=source_url, status="processing")
    session.add(doc_record)
    session.commit()
    session.refresh(doc_record)

    try:
        pages = _extract_pages(file_path)
        doc_record.title = get_pdf_title(file_path) if ext == ".pdf" else filename
        doc_record.num_pages = len(pages)
        ocr_pages = sum(1 for p in pages if p.get("ocr_used"))

        chunks = chunk_document(pages)
        add_chunks(doc_record.id, filename, chunks)

        # Rate-table regex extraction only applies to the PDF rate-table format
        table_rows = extract_rate_tables_from_pdf(file_path) if ext == ".pdf" else []
        for row in table_rows:
            session.add(RateTableRow(document_id=doc_record.id, filename=filename, **row))

        doc_record.status = "done"
        session.commit()

        return {
            "document_id": doc_record.id,
            "filename": filename,
            "pages": len(pages),
            "ocr_pages_used": ocr_pages,
            "prose_chunks_indexed": len(chunks),
            "table_rows_extracted": len(table_rows),
            "status": "done",
        }
    except Exception:
        doc_record.status = "failed"
        session.commit()
        raise
    finally:
        session.close()


def ingest_url(url: str) -> dict:
    """Ingests a web page's visible text as a one-page 'document'."""
    session = SessionLocal()
    filename = url  # use the URL itself as the identifier

    doc_record = Document(filename=filename, source_url=url, status="processing")
    session.add(doc_record)
    session.commit()
    session.refresh(doc_record)

    try:
        pages = extract_url_page(url)
        doc_record.title = url
        doc_record.num_pages = len(pages)

        chunks = chunk_document(pages)
        add_chunks(doc_record.id, filename, chunks)

        doc_record.status = "done"
        session.commit()

        return {
            "document_id": doc_record.id,
            "filename": filename,
            "pages": len(pages),
            "prose_chunks_indexed": len(chunks),
            "table_rows_extracted": 0,
            "status": "done",
        }
    except Exception:
        doc_record.status = "failed"
        session.commit()
        raise
    finally:
        session.close()


def ingest_folder(folder_path: str) -> list[dict]:
    """Bulk ingest - processes every supported file (PDF, DOCX, PPTX, XLSX)
    already sitting in data/raw_pdfs/. Skips files already successfully
    ingested, so re-running this after adding new files doesn't re-embed
    everything and create duplicate chunks."""
    results = []
    all_files = sorted(
        f for f in os.listdir(folder_path)
        if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
    )
    total = len(all_files)
    print(f"\n=== Starting bulk ingest of {total} files ===")

    for i, fname in enumerate(all_files, 1):
        if already_ingested(fname):
            print(f"[{i}/{total}] Skipping (already ingested): {fname}")
            results.append({"filename": fname, "status": "already_ingested"})
            continue

        full_path = os.path.join(folder_path, fname)
        print(f"[{i}/{total}] Processing: {fname}")
        try:
            result = ingest_pdf(full_path)
            print(f"    -> done: {result['prose_chunks_indexed']} chunks, "
                  f"{result['table_rows_extracted']} table rows"
                  + (f", {result['ocr_pages_used']} page(s) OCR'd" if result.get('ocr_pages_used') else ""))
            results.append(result)
        except Exception as e:
            print(f"    -> FAILED: {e}")
            results.append({"filename": fname, "status": "failed", "error": str(e)})

    print(f"=== Bulk ingest complete: {total} files processed ===\n")
    return results
