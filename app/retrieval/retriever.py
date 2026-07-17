import math
from sqlalchemy import and_
from app.db.models import SessionLocal, RateTableRow
from app.vectorstore.chroma_store import semantic_search
from app.retrieval.query_router import classify_query, extract_lookup_params


def lookup_rate(scale: str | None, distance_km: int | None, weight_kg: int | None, limit: int = 5):
    session = SessionLocal()
    try:
        query = session.query(RateTableRow)
        if scale:
            query = query.filter(RateTableRow.scale == scale)
        if distance_km is not None:
            query = query.filter(
                and_(RateTableRow.distance_min_km <= distance_km,
                     RateTableRow.distance_max_km >= distance_km)
            )
        if weight_kg is not None:
            # weight_slab_kg is the upper bound of a 10kg bracket; find the smallest
            # slab that covers the requested weight
            target_slab = math.ceil(weight_kg / 10) * 10
            query = query.filter(RateTableRow.weight_slab_kg == target_slab)
        return query.limit(limit).all()
    finally:
        session.close()


def retrieve_context(user_query: str) -> dict:
    """Returns {"mode": ..., "table_rows": [...], "semantic_chunks": [...]}"""
    mode = classify_query(user_query)
    result = {"mode": mode, "table_rows": [], "semantic_chunks": []}

    if mode in ("table", "both"):
        params = extract_lookup_params(user_query)
        rows = lookup_rate(**params)
        result["table_rows"] = [
            {
                "scale": r.scale,
                "category": r.category,
                "distance_range_km": f"{r.distance_min_km}-{r.distance_max_km}",
                "weight_slab_kg": r.weight_slab_kg,
                "rate_rs": r.rate_rs,
                "page_number": r.page_number,
            }
            for r in rows
        ]

    if mode in ("semantic", "both"):
        result["semantic_chunks"] = semantic_search(user_query, top_k=8)

    return result
