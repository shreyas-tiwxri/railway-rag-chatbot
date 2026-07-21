import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ingestion.table_extractor import parse_rate_table_text, looks_like_rate_table_doc

SAMPLE_TEXT = """LUGGAGE RATES
Scale-L
Distance slabs
(Kilometres)
1 \u2010 50 7.38 14.76 22.15 29.53 36.91 44.29 51.67 59.06 66.44 73.82
51 \u2010 60 7.91 15.82 23.73 31.64 39.56 47.47 55.38 63.29 71.20 79.11
"""


def test_parse_rate_table_extracts_correct_row_count():
    rows = parse_rate_table_text(SAMPLE_TEXT, page_number=1)
    assert len(rows) == 20  # 2 distance rows x 10 weight slabs each


def test_parse_rate_table_correct_values():
    rows = parse_rate_table_text(SAMPLE_TEXT, page_number=1)
    first_row = rows[0]
    assert first_row["scale"] == "Scale-L"
    assert first_row["distance_min_km"] == 1
    assert first_row["distance_max_km"] == 50
    assert first_row["weight_slab_kg"] == 10
    assert first_row["rate_rs"] == 7.38


def test_parse_rate_table_handles_scale_p_header_variant():
    text = "SCALE- P \n1 \u2010 50 4.10 8.20 12.30 16.40 20.51 24.61 28.71 32.81 36.91 41.01"
    rows = parse_rate_table_text(text, page_number=1)
    assert rows[0]["scale"] == "Scale-P"
    assert rows[0]["rate_rs"] == 4.10


def test_parse_rate_table_ignores_malformed_rows():
    text = "Scale-L\nthis is not a rate row\n1 \u2010 50 7.38 14.76"  # too few values
    rows = parse_rate_table_text(text, page_number=1)
    assert rows == []


def test_looks_like_rate_table_doc_matches_expected_filenames():
    assert looks_like_rate_table_doc("FM_21_Annexure_parcel_rate_table.pdf") is True
    assert looks_like_rate_table_doc("FMC No_ 13 of 2026.pdf") is False
