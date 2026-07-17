"""Decides whether a query should hit the structured rate_table (SQL) or the
vector store (semantic), or both. Starts with cheap heuristics — no LLM call
needed for routing, which keeps latency and cost down. Upgrade to an LLM
classifier later only if the heuristic misses too often in testing."""
import re

SCALE_RE = re.compile(r"scale\s*[\-]?\s*([rpsl])", re.IGNORECASE)
DISTANCE_RE = re.compile(r"(\d{1,5})\s*(?:km|kilometers?|kilometres?)", re.IGNORECASE)
WEIGHT_RE = re.compile(r"(\d{1,4})\s*kgs?", re.IGNORECASE)


def classify_query(query: str) -> str:
    """Returns 'table', 'semantic', or 'both'."""
    has_scale = bool(SCALE_RE.search(query))
    has_distance = bool(DISTANCE_RE.search(query))
    has_weight = bool(WEIGHT_RE.search(query))

    signals = sum([has_scale, has_distance, has_weight])

    if signals >= 2:
        return "table"
    if signals == 1:
        return "both"  # ambiguous enough to also pull semantic context
    return "semantic"


def extract_lookup_params(query: str) -> dict:
    scale_match = SCALE_RE.search(query)
    distance_match = DISTANCE_RE.search(query)
    weight_match = WEIGHT_RE.search(query)
    return {
        "scale": f"Scale-{scale_match.group(1).upper()}" if scale_match else None,
        "distance_km": int(distance_match.group(1)) if distance_match else None,
        "weight_kg": int(weight_match.group(1)) if weight_match else None,
    }
