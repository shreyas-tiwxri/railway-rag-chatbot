"""Free, local embeddings using fastembed (ONNX-based, no PyTorch) — no API
key, no cost, and low memory footprint (important for free-tier deploys with
512MB RAM limits, where PyTorch-based sentence-transformers would OOM)."""
from fastembed import TextEmbedding

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = _get_model()
    return [emb.tolist() for emb in model.embed(texts)]
