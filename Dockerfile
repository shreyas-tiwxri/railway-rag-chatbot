FROM python:3.11-slim

WORKDIR /app

# System deps for pdfplumber/pymupdf, plus Tesseract for OCR fallback on scanned PDFs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-warm the sentence-transformers model into the image so the first
# request isn't slow downloading it, and so it works even if the deploy
# environment has restricted outbound internet after build.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='BAAI/bge-small-en-v1.5')"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
