import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.retrieval.query_router import classify_query, extract_lookup_params


def test_classify_table_query():
    assert classify_query("What is the Scale-L rate for 40 kg over 620 km?") == "table"


def test_classify_semantic_query():
    assert classify_query("What is the minimum charge for booking a parcel?") == "semantic"


def test_classify_partial_signal_as_both():
    # only a distance signal present -> ambiguous, should pull both retrieval paths
    result = classify_query("What happens after 500 km?")
    assert result in ("both", "semantic")


def test_extract_lookup_params():
    params = extract_lookup_params("What is the Scale-P rate for 20 kg over 100 km?")
    assert params["scale"] == "Scale-P"
    assert params["distance_km"] == 100
    assert params["weight_kg"] == 20


def test_extract_lookup_params_missing_fields():
    params = extract_lookup_params("Tell me about parcel booking rules")
    assert params["scale"] is None
    assert params["distance_km"] is None
    assert params["weight_kg"] is None
