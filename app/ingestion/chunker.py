"""Chunk prose pages for embedding. Pages that are >70% numeric (i.e. rate
tables already handled by table_extractor) are skipped here to avoid polluting
the vector store with garbage table fragments."""
import re

CHUNK_SIZE_CHARS = 1500       # ~300-400 tokens
CHUNK_OVERLAP_CHARS = 200


def is_mostly_tabular(text: str, numeric_ratio_threshold: float = 0.35) -> bool:
    if not text.strip():
        return True
    tokens = text.split()
    if not tokens:
        return True
    numeric_tokens = sum(1 for t in tokens if re.match(r"^\d+[\.\d]*$", t))
    return (numeric_tokens / len(tokens)) > numeric_ratio_threshold


def chunk_page_text(page_text: str) -> list[str]:
    if is_mostly_tabular(page_text):
        return []

    text = re.sub(r"\s+", " ", page_text).strip()
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE_CHARS, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - CHUNK_OVERLAP_CHARS
    return chunks


def chunk_document(pages: list[dict]) -> list[dict]:
    """pages: [{"page_number": int, "text": str}, ...]
    returns: [{"page_number": int, "chunk_index": int, "text": str}, ...]"""
    all_chunks = []
    for page in pages:
        page_chunks = chunk_page_text(page["text"])
        for idx, chunk_text in enumerate(page_chunks):
            all_chunks.append({
                "page_number": page["page_number"],
                "chunk_index": idx,
                "text": chunk_text,
            })
    return all_chunks
