import os
from app.ingestion.pdf_loader import extract_pages_text, get_pdf_title
from app.ingestion.table_extractor import extract_rate_tables_from_pdf
from app.ingestion.chunker import chunk_document
from app.vectorstore.chroma_store import add_chunks
from app.db.models import SessionLocal, Document, RateTableRow


def ingest_pdf(pdf_path: str, source_url: str | None = None) -> dict:
    session = SessionLocal()
    filename = os.path.basename(pdf_path)

    doc_record = Document(filename=filename, source_url=source_url, status="processing")
    session.add(doc_record)
    session.commit()
    session.refresh(doc_record)

    try:
        pages = extract_pages_text(pdf_path)
        doc_record.title = get_pdf_title(pdf_path)
        doc_record.num_pages = len(pages)
        ocr_pages = sum(1 for p in pages if p.get("ocr_used"))

        # 1. Prose -> chunks -> embeddings -> vector store
        chunks = chunk_document(pages)
        add_chunks(doc_record.id, filename, chunks)

        # 2. Tables -> structured rows -> SQL
        table_rows = extract_rate_tables_from_pdf(pdf_path)
        for row in table_rows:
            session.add(RateTableRow(document_id=doc_record.id, **row))

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
    except Exception as e:
        doc_record.status = "failed"
        session.commit()
        raise
    finally:
        session.close()


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


def ingest_folder(folder_path: str) -> list[dict]:
    """Bulk ingest — point this at data/raw_pdfs/ after manually downloading
    the 20+ PDFs from the Railway Board page (site disallows automated scraping).
    Skips files that were already successfully ingested, so re-running this after
    adding a few new PDFs doesn't re-embed everything and create duplicate chunks."""
    results = []
    pdf_files = sorted(f for f in os.listdir(folder_path) if f.lower().endswith(".pdf"))
    total = len(pdf_files)
    print(f"\n=== Starting bulk ingest of {total} PDFs ===")

    for i, fname in enumerate(pdf_files, 1):
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
