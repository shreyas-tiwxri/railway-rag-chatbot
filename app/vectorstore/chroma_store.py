import chromadb
from app.config import settings
from app.embeddings.embedder import embed_texts

_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
_collection = _client.get_or_create_collection(name="railway_docs")


def add_chunks(document_id: int, filename: str, chunks: list[dict]):
    """chunks: [{"page_number": int, "chunk_index": int, "text": str}, ...]"""
    if not chunks:
        return
    ids = [f"{document_id}-{c['page_number']}-{c['chunk_index']}" for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [
        {"document_id": document_id, "filename": filename, "page_number": c["page_number"]}
        for c in chunks
    ]
    embeddings = embed_texts(texts)
    _collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)


def semantic_search(query: str, top_k: int = 8) -> list[dict]:
    query_embedding = embed_texts([query])[0]
    # over-fetch, then dedupe by text so repeated ingestions don't produce
    # repetitive/duplicated context for the LLM
    results = _collection.query(query_embeddings=[query_embedding], n_results=top_k * 3)

    seen_texts = set()
    hits = []
    for i in range(len(results["ids"][0])):
        text = results["documents"][0][i]
        normalized = " ".join(text.split())[:300]  # dedupe key: normalized text prefix
        if normalized in seen_texts:
            continue
        seen_texts.add(normalized)
        hits.append({
            "text": text,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
        if len(hits) >= top_k:
            break
    return hits
