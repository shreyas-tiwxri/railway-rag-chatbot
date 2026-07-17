# Railway Document RAG Chatbot — 8-Day Build Plan

## The pitch (for resume/interview)
"Built a hybrid Retrieval-Augmented Generation system that answers natural-language
queries over 20+ Indian Railways policy/tariff PDFs, combining structured SQL lookups
for tabular rate data with vector semantic search for policy text — because naive
RAG fails on numeric tables (embeddings can't do exact lookups like '500km, 40kg,
Scale-S rate')."

This "hybrid retrieval" angle is your differentiator. Every bootcamp grad has built
a "chat with PDF" app with LangChain + Chroma. Almost none of them handle tables
correctly. That's the interesting engineering problem here.

## Why hybrid, not pure vector RAG
Documents like the parcel rate PDF have two very different content types:
1. **Explanatory notes** (prose: "minimum distance for charge is 50 km...") →
   good fit for embeddings + vector similarity search.
2. **Rate tables** (Scale-R/P/S/L × distance-slab × weight-slab grids) → terrible
   fit for embeddings. A query like "40kg parcel over 620km on Scale-P" needs an
   exact row/column lookup, not "find chunks that sound similar."

So the pipeline extracts tables separately, structures them into a queryable SQL
table (scale, distance_min, distance_max, weight_slab, rate), and routes numeric/
tabular-sounding queries there, while prose queries go through the vector store.
A query classifier (cheap LLM call or regex/keyword heuristic) decides the route.

## Day-by-day

**Day 1 — Ingestion skeleton + text extraction**
- FastAPI project scaffold (done below)
- `pdf_loader.py`: extract raw text page-by-page (PyMuPDF/fitz)
- Store PDF metadata (title, source URL, date added) in SQLite

**Day 2 — Table extraction**
- `table_extractor.py`: use `pdfplumber` (or `camelot` for cleaner grid tables)
  to pull rate tables into pandas DataFrames
- Normalize into a single long-format table: `(doc_id, scale, distance_slab_min,
  distance_slab_max, weight_slab, rate_rs)`
- Load into SQLite `rate_table` — this is what powers exact lookups

**Day 3 — Chunking + embeddings for prose**
- `chunker.py`: chunk explanatory/prose text (~300-500 tokens, overlap ~50)
  skip pages that are pure tables (already structured in Day 2)
- `embedder.py`: call embedding API, batch-embed chunks
- `chroma_store.py`: persist to local ChromaDB with metadata (doc_id, page,
  source_url, section)

**Day 4 — Retrieval + query router**
- `query_router.py`: classify incoming query as TABLE_LOOKUP vs SEMANTIC vs BOTH
  (start with keyword heuristics: numbers + "km"/"kg"/"scale" → table; else semantic)
- `retriever.py`: for TABLE_LOOKUP, parse query params (distance, weight, scale)
  and run SQL query; for SEMANTIC, run vector similarity search

**Day 5 — LLM answer generation**
- `generator.py`: construct prompt with retrieved context (table row(s) or text
  chunks), ask LLM to answer in plain language, always cite source doc + page
- Handle "not found in documents" gracefully — don't let the LLM hallucinate a rate

**Day 6 — API endpoints + bulk ingestion**
- `POST /ingest` — upload a PDF, runs full pipeline async
- `POST /ingest/bulk` — point at a folder of PDFs, process all (for your 20+ docs)
- `POST /query` — ask a question, get answer + sources
- `GET /documents` — list ingested docs
- `GET /health`

**Day 7 — Testing + edge cases**
- Postman collection (included) covering: exact table lookups, prose questions,
  questions spanning multiple docs, out-of-scope questions (should refuse, not hallucinate)
- Add basic logging + error handling

**Day 8 — Polish + deploy**
- Dockerfile, docker-compose (API + persistent Chroma volume)
- Deploy to Render/Railway free tier
- README with architecture diagram description + example curl/Postman calls

## Stack
- FastAPI (async)
- pdfplumber + PyMuPDF (extraction)
- ChromaDB (local vector store, no infra cost — good for a portfolio project)
- SQLite (structured rate tables + doc metadata) — swap to Postgres later if needed
- OpenAI API (embeddings: text-embedding-3-small, generation: gpt-4o-mini) — same
  provider you're already using in the Interview Coach project, one API key to manage

## Legal/practical note on the source site
indianrailways.gov.in disallows automated scraping (robots.txt). So `/ingest/bulk`
should point at a local folder — you manually download the PDFs from the Railway
Board page and drop them in `data/raw_pdfs/`. This is normal for gov-document RAG
projects and worth mentioning in your README as a deliberate design choice, not
a limitation you missed.
