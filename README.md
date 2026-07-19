# Railway Documents RAG Chatbot

**Live demo:** https://railway-rag-chatbot.onrender.com/chat/
(Free-tier hosting — first request after inactivity may take 30-50s to wake up.)

Hybrid Retrieval-Augmented Generation API over Indian Railways parcel/luggage/
freight tariff and policy PDFs. Combines **structured SQL lookups** for tabular
rate data with **vector semantic search** for prose/policy text, routed by a
lightweight query classifier — because pure vector RAG gives wrong or vague
answers on numeric table lookups.

Fully free stack: local ONNX-based embeddings (fastembed, no API key, low
memory footprint for free-tier hosting) + Groq's free-tier LLM API for answer
generation (no credit card required).

See `ROADMAP.md` for the full architecture rationale and day-by-day build plan.

## Setup

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # then add your OPENAI_API_KEY
```

## Run

```bash
uvicorn app.main:app --reload
```

API docs (Swagger UI) at http://localhost:8000/docs

## Ingesting documents

1. Manually download the PDFs you want from the Railway Board page (the site's
   robots.txt disallows automated scraping — see ROADMAP.md) and drop them into
   `data/raw_pdfs/`.
2. Either:
   - `POST /ingest` with a single file (multipart form), or
   - `POST /ingest/bulk` to process every PDF already in `data/raw_pdfs/`

## Querying

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the Scale-L rate for 40 kg over 620 km?"}'
```

Import `postman_collection.json` into Postman for a ready-made set of test
requests covering table lookups, semantic queries, and out-of-scope questions.

## Project structure

```
app/
  ingestion/       # PDF text extraction, table parsing, chunking
  embeddings/       # OpenAI embedding calls
  vectorstore/       # ChromaDB wrapper
  retrieval/       # query router + hybrid retriever
  llm/              # answer generation
  db/              # SQLite models (documents, structured rate_table)
  api/              # FastAPI routes + schemas
data/
  raw_pdfs/         # drop downloaded PDFs here before bulk ingest
  chroma/           # vector store persistence (auto-created)
```

## Known limitations / next steps
- `table_extractor.py` uses a regex parser tuned to the recurring table shape
  in these Railway tariff PDFs (distance-slab rows x weight-slab columns). New
  table shapes from other documents will need their own parser function.
- Query routing is heuristic-based (regex signals), not an LLM classifier —
  fast and cheap, but revisit if you see it misrouting during testing.
- No auth/rate-limiting yet — fine for a portfolio demo, add before any public deploy.
