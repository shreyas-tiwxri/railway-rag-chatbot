"""
Extracts rate tables from PDFs like FM_21_Annexure_parcel_rate_table.pdf into
long-format rows: (scale, category, distance_min, distance_max, weight_slab, rate).

Approach: these Railway tariff tables have a very regular structure once you
look at the raw text — each row is:
    "<dist_min> - <dist_max>  <rate1> <rate2> ... <rate10>"
with a header block above naming the scale ("Scale-L", "SCALE- P", etc.) and the
weight-slab columns (1-10 Kgs, 11-20 Kgs, ... 91-100 Kgs, in steps of 10).

This is intentionally a targeted parser, not a generic table-to-JSON magic box —
generic table extraction on gov-PDF tables is unreliable. Writing a parser for
each recurring table *shape* you encounter across your 20+ docs is more robust,
and it's a better story in an interview than "I called camelot and hoped."

For genuinely different table shapes in other PDFs, add a new `parse_x_table()`
function here following the same pattern, and register it in TABLE_PARSERS below.
"""
import os
import re
import pdfplumber

# Only run the rate-table parser on filenames that look like the actual rate
# table document. Running this regex parser on every PDF was causing false
# positives — unrelated circulars with number sequences occasionally matched
# the DISTANCE_ROW_RE pattern and polluted rate_table with garbage rows.
RATE_TABLE_FILENAME_HINTS = ["parcel_rate", "annexure", "rate_table"]

DISTANCE_ROW_RE = re.compile(
    r"^(\d{1,5})\s*[\-‐–]\s*(\d{1,5})\s+((?:\d+\.\d{2}\s*){10})$"
)
SCALE_HEADER_RE = re.compile(r"Scale\s*[\-‐]\s*([RPSL])\*?", re.IGNORECASE)

# Standard weight-slab upper bounds used across these tables (10..100 in steps of 10)
WEIGHT_SLABS_KG = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

CATEGORY_HINTS = {
    "L": "Luggage",
    "P": "Premier Parcel",
    "S": "Standard Parcel",
    "R": "Rajdhani/Shatabdi/Duronto Parcel",
}


def parse_rate_table_text(full_text: str, page_number: int | None = None) -> list[dict]:
    """Parses concatenated page text (or whole-doc text) into rate rows.
    Call this per page if you need accurate page_number attribution."""
    rows = []
    current_scale = None

    for raw_line in full_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        scale_match = SCALE_HEADER_RE.search(line)
        if scale_match:
            current_scale = scale_match.group(1).upper()
            continue

        row_match = DISTANCE_ROW_RE.match(line)
        if row_match and current_scale:
            dist_min, dist_max = int(row_match.group(1)), int(row_match.group(2))
            rate_values = [float(v) for v in row_match.group(3).split()]
            if len(rate_values) != len(WEIGHT_SLABS_KG):
                continue  # malformed row, skip rather than guess
            for weight_slab, rate in zip(WEIGHT_SLABS_KG, rate_values):
                rows.append({
                    "scale": f"Scale-{current_scale}",
                    "category": CATEGORY_HINTS.get(current_scale),
                    "distance_min_km": dist_min,
                    "distance_max_km": dist_max,
                    "weight_slab_kg": weight_slab,
                    "rate_rs": rate,
                    "page_number": page_number,
                })
    return rows


def looks_like_rate_table_doc(pdf_path: str) -> bool:
    fname_lower = os.path.basename(pdf_path).lower()
    return any(hint in fname_lower for hint in RATE_TABLE_FILENAME_HINTS)


def extract_rate_tables_from_pdf(pdf_path: str) -> list[dict]:
    """Runs the parser page-by-page so each row keeps correct page attribution.
    Skips documents that don't look like the rate table, to avoid false-positive
    matches from unrelated circulars."""
    if not looks_like_rate_table_doc(pdf_path):
        return []

    all_rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            all_rows.extend(parse_rate_table_text(text, page_number=i + 1))
    return all_rows


TABLE_PARSERS = {
    "parcel_rate_table": extract_rate_tables_from_pdf,
    # add more: "<other_doc_key>": <parser_fn>
}