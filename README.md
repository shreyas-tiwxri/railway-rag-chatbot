# Railway Documents RAG Chatbot

[![CI](https://github.com/shreyas-tiwxri/railway-rag-chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/shreyas-tiwxri/railway-rag-chatbot/actions/workflows/ci.yml)

**Live demo:** https://railway-rag-chatbot.onrender.com/chat/
(Free-tier hosting — first request after inactivity may take 30-50s to wake up.)

**Measured accuracy:** see [`eval/results.md`](eval/results.md) — evaluated against
a 16-question test set spanning exact table lookups, policy/semantic questions,
and out-of-scope refusals.

Hybrid Retrieval-Augmented Generation API over Indian Railways parcel/luggage/
freight tariff and policy PDFs. Combines **structured SQL lookups** for tabular
rate data with **vector semantic search** for prose/policy text, routed by a
lightweight query classifier — because pure vector RAG gives wrong or vague
answers on numeric table lookups.

Fully free stack: local ONNX-based embeddings (fastembed, no API key, low
memory footprint for free-tier hosting) + Groq's free-tier LLM API for answer
generation (no credit card required).

## Screenshots

_Add screenshots of the `/chat/` UI here — e.g. a table-lookup query and a
semantic query side by side. Drop image files into a `docs/` folder and
reference them: `![Chat UI](docs/screenshot-1.png)`_

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| API | FastAPI | async, auto-generated OpenAPI docs |
| Vector store | ChromaDB | local, zero-infra, persists to disk |
| Structured data | SQLite + SQLAlchemy | exact rate lookups, no vector search needed |
| Embeddings | fastembed (ONNX) | no PyTorch — fits free-tier 512MB RAM limits |
| LLM | Groq (Llama 3.3 70B) | free tier, fast inference |
| OCR fallback | Tesseract via pytesseract | recovers text from scanned circulars |
| Frontend | Vanilla HTML/CSS/JS | no build step, served directly by FastAPI |
| Deployment | Docker on Render | free tier, pre-baked knowledge base in the image |
| CI | GitHub Actions | runs pytest on every push |

See `ROADMAP.md` for the full architecture rationale and day-by-day build plan.

## Setup

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # then add your free GROQ_API_KEY (console.groq.com/keys)
```

## Run

```bash
uvicorn app.main:app --reload
```

API docs (Swagger UI) at http://localhost:8000/docs
Chat UI at http://localhost:8000/chat/

## Tests

```bash
pytest tests/ -v
```

Covers the table-extraction regex parser, the query router's classification
logic, and the chunker's tabular-page detection. Runs automatically on every
push via GitHub Actions (see badge above).

## Evaluation

```bash
python eval/run_eval.py                                      # tests localhost
python eval/run_eval.py --url https://railway-rag-chatbot.onrender.com  # tests live deploy
```

Runs a 16-question test set (table lookups, semantic/policy questions, and an
out-of-scope refusal check) and writes a pass/fail report with accuracy per
category to `eval/results.md`.

## Ingesting documents

1. Manually download the PDFs you want from the Railway Board page (the site's
   robots.txt disallows automated scraping — see ROADMAP.md), or run
   `python scripts/download_pdfs.py` which crawls the Freight Marketing
   Circulars section and downloads PDFs into `data/raw_pdfs/` automatically.
2. Either:
   - `POST /ingest` with a single file (multipart form), or
   - `POST /ingest/bulk` to process every PDF already in `data/raw_pdfs/`

## Querying

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the Scale-L rate for 40 kg over 620 km?"}'
```

The `/query` endpoint also accepts an optional `history` array of
`{"question": ..., "answer": ...}` pairs from earlier turns, so the chat UI
can ask follow-up questions ("what about for 50kg instead?") that resolve
pronouns/references against the conversation so far.

Import `postman_collection.json` into Postman for a ready-made set of test
requests covering table lookups, semantic queries, and out-of-scope questions.

## Project structure

```
app/
  ingestion/       # PDF text extraction (+ OCR fallback), table parsing, chunking
  embeddings/       # local fastembed embedding calls
  vectorstore/       # ChromaDB wrapper
  retrieval/       # query router + hybrid retriever
  llm/              # answer generation (Groq API), conversation history support
  db/              # SQLite models (documents, structured rate_table)
  api/              # FastAPI routes + schemas
static/
  chat.html         # chat UI, served at /chat/
scripts/
  download_pdfs.py  # optional auto-crawler for the Railway Board source pages
  trim_pdfs.py      # trims a large PDF set down to a manageable subset by year
eval/
  questions.json    # test set with verified ground-truth answers
  run_eval.py       # evaluation harness
tests/
  test_*.py         # unit tests, run via pytest
data/
  raw_pdfs/         # drop downloaded PDFs here before bulk ingest
  chroma/           # vector store persistence (committed — see .gitignore notes)
```

## Known limitations / next steps
- `table_extractor.py` uses a regex parser tuned to the recurring table shape
  in these Railway tariff PDFs (distance-slab rows x weight-slab columns), and
  only runs on filenames that look like a rate-table document (to avoid false
  positives from unrelated circulars). New table shapes need their own parser.
- Query routing is heuristic-based (regex signals), not an LLM classifier —
  fast and cheap, but revisit if you see it misrouting during testing.
- **Semantic retrieval can surface the wrong document when several documents
  discuss a similar concept** (e.g. two different circulars both mentioning
  "minimum distance" with different values for different contexts). Measured
  in `eval/results.md`. Mitigations tried: increasing top-k recall. Further
  mitigation would need re-ranking or a stronger embedding model.
- Conversation history is passed to the LLM for follow-up question phrasing,
  but retrieval itself is still based only on the current question — a
  follow-up that depends heavily on prior context for *retrieval* (not just
  phrasing) may not find the right chunks.
- No auth/rate-limiting yet — fine for a portfolio demo, add before any public deploy.

## What to say about this in an interview
- **Why hybrid retrieval, not pure vector RAG**: numeric table lookups (e.g.
  "rate for 40kg over 620km") need exact matching, not similarity search —
  embeddings are bad at exact numeric comparison. Structured SQL handles that
  deterministically; vector search handles prose/policy questions.
- **Why the LLM is bypassed for table lookups**: smaller/free models tend to
  second-guess correct numeric matches ("I cannot confirm the rate is in
  range X" even when it clearly is). Removing the LLM from the critical path
  for deterministic lookups eliminates a whole class of hallucination risk.
- **The OCR fallback** is a good example of noticing a silent failure mode
  (scanned PDFs producing empty text) and fixing the root cause instead of
  just working around it.
- **The measured eval numbers** are a stronger claim than "it works" — and
  the process of building the eval set caught a bug in my own test data
  (a misread table value), which is itself a good story about why you
  verify ground truth carefully before trusting a pass/fail number.

