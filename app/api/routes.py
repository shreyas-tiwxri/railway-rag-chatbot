import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.api.schemas import QueryRequest, QueryResponse, DocumentOut, UrlIngestRequest
from app.ingestion.pipeline import ingest_pdf, ingest_folder, ingest_url, SUPPORTED_EXTENSIONS
from app.retrieval.retriever import retrieve_context
from app.llm.generator import generate_answer
from app.db.models import SessionLocal, Document

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/ingest")
async def ingest_single(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    os.makedirs(settings.raw_pdf_dir, exist_ok=True)
    dest_path = os.path.join(settings.raw_pdf_dir, file.filename)
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result = ingest_pdf(dest_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")
    return result


@router.post("/ingest/url")
def ingest_website(request: UrlIngestRequest):
    try:
        result = ingest_url(request.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL ingestion failed: {e}")
    return result


@router.post("/ingest/bulk")
def ingest_bulk():
    """Ingests every supported file (PDF, DOCX, PPTX, XLSX) already sitting
    in data/raw_pdfs/."""
    if not os.path.isdir(settings.raw_pdf_dir):
        raise HTTPException(status_code=400, detail=f"{settings.raw_pdf_dir} does not exist")
    results = ingest_folder(settings.raw_pdf_dir)
    return {"ingested": len(results), "results": results}


@router.get("/documents", response_model=list[DocumentOut])
def list_documents():
    session = SessionLocal()
    try:
        return session.query(Document).all()
    finally:
        session.close()


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        retrieval_result = retrieve_context(request.question)
        generation_result = generate_answer(request.question, retrieval_result, request.history)
        return generation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {type(e).__name__}: {e}")
