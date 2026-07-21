import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ingestion.chunker import is_mostly_tabular, chunk_page_text


def test_is_mostly_tabular_detects_numeric_heavy_text():
    numeric_text = "1 50 7.38 14.76 22.15 29.53 36.91 44.29 51.67 59.06 66.44 73.82"
    assert is_mostly_tabular(numeric_text) is True


def test_is_mostly_tabular_allows_prose():
    prose = ("The minimum distance for charge for all parcels is 50 kilometers "
              "and the minimum charge is Rs. 30.00 for booking through the Railway.")
    assert is_mostly_tabular(prose) is False


def test_chunk_page_text_skips_tabular_pages():
    numeric_text = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"
    assert chunk_page_text(numeric_text) == []


def test_chunk_page_text_chunks_long_prose():
    prose = "word " * 500
    chunks = chunk_page_text(prose)
    assert len(chunks) > 1


def test_chunk_page_text_empty_input():
    assert chunk_page_text("") == []
