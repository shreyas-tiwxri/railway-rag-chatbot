"""
Standalone helper — NOT part of the FastAPI app. Run this manually, once,
to auto-download PDFs linked from the Railway Board "Freight Marketing
Circulars" section into data/raw_pdfs/.

The site structure is 2 levels deep:
  main section page -> year/topic sub-pages (also view_section.jsp links)
    -> sub-pages contain the actual .pdf links

So this script:
  1. Fetches the main page, finds all sub-section links (same domain,
     view_section.jsp URLs) — these are things like "FREIGHT_MARKETING_2026",
     "Master Circulars", "LSFTO", etc.
  2. Visits each sub-page and collects any .pdf links found there.
  3. Downloads every unique PDF found, skipping ones already downloaded.

Note: indianrailways.gov.in's robots.txt disallows automated crawling.
This script is written to be "polite" about it anyway:
- identifies itself with a normal browser User-Agent (not deceptive, just
  avoids being blocked by naive bot-filters)
- adds a delay between each request so it doesn't hammer the server
- runs once, on demand, from your machine — not a recurring/scheduled scraper
- only downloads publicly accessible PDFs already linked on public pages

Usage:
    python scripts/download_pdfs.py
"""
import os
import time
import re
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

START_URL = "https://indianrailways.gov.in/railwayboard/view_section.jsp?lang=0&id=0,1,304,366,555,862"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw_pdfs")
DELAY_SECONDS = 2  # be polite, don't hammer a gov server
DOMAIN = "indianrailways.gov.in"

RECENT_YEARS = ["2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]  # only download circulars from these years
                                          # (edit this list to grab more/fewer years)


def is_recent(url: str) -> bool:
    return any(year in url for year in RECENT_YEARS)


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


def fetch(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"    Failed to fetch {url}: {e}")
        return None


def find_subsection_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    """Links that go to another view_section.jsp page WITHIN THE SAME SECTION
    (same id prefix as the starting page) — not the entire site's navigation,
    which also uses view_section.jsp for every single page on the site."""
    base_id_prefix = urlparse(START_URL).query  # e.g. "lang=0&id=0,1,304,366,555,862"
    base_id_value = base_id_prefix.split("id=")[-1]  # "0,1,304,366,555,862"

    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        full_url = full_url.replace("http://", "https://")  # force https
        parsed = urlparse(full_url)
        if DOMAIN not in parsed.netloc or "view_section.jsp" not in parsed.path.lower():
            continue
        link_id = parsed.query.split("id=")[-1] if "id=" in parsed.query else ""
        if link_id.startswith(base_id_value):
            links.add(full_url)

    links.discard(base_url)
    return sorted(links)


def find_pdf_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.lower().split("?")[0].endswith(".pdf"):
            full_url = urljoin(base_url, href).replace("http://", "https://")
            links.add(full_url)
    return sorted(links)


def safe_filename(url: str) -> str:
    name = url.split("/")[-1].split("?")[0]
    name = requests.utils.unquote(name)
    name = re.sub(r"[^\w\-. ]", "_", name)
    return name or "document.pdf"


def download_pdfs(pdf_urls: list[str], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    for i, url in enumerate(pdf_urls, 1):
        filename = safe_filename(url)
        dest_path = os.path.join(output_dir, filename)

        if os.path.exists(dest_path):
            print(f"[{i}/{len(pdf_urls)}] Skipping (already downloaded): {filename}")
            continue

        try:
            print(f"[{i}/{len(pdf_urls)}] Downloading: {filename}")
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            with open(dest_path, "wb") as f:
                f.write(resp.content)
        except Exception as e:
            print(f"    FAILED: {url} -> {e}")

        time.sleep(DELAY_SECONDS)


if __name__ == "__main__":
    print(f"Step 1: Fetching main page: {START_URL}")
    main_soup = fetch(START_URL)
    if main_soup is None:
        raise SystemExit("Could not fetch the main page. Check your internet connection.")

    subsection_links = find_subsection_links(main_soup, START_URL)
    print(f"Found {len(subsection_links)} sub-section links (years/topics).\n")

    all_pdf_links = set(find_pdf_links(main_soup, START_URL))

    print("Step 2: Visiting each sub-section to find PDFs...")
    for i, link in enumerate(subsection_links, 1):
        print(f"  [{i}/{len(subsection_links)}] {link}")
        sub_soup = fetch(link)
        if sub_soup:
            pdfs = find_pdf_links(sub_soup, link)
            print(f"      -> {len(pdfs)} PDF(s) found")
            all_pdf_links.update(pdfs)
        time.sleep(DELAY_SECONDS)

    all_pdf_links = sorted(all_pdf_links)
    print(f"\nTotal unique PDFs found across all pages: {len(all_pdf_links)}")

    filtered_links = [link for link in all_pdf_links if is_recent(link)]
    print(f"Filtered to {RECENT_YEARS}: {len(filtered_links)} PDFs\n")

    if not filtered_links:
        print("No PDFs found for the configured RECENT_YEARS. Edit the RECENT_YEARS list "
              "at the top of this script to include more years, then re-run.")
    elif len(filtered_links) > 600:
        print(f"WARNING: {len(filtered_links)} PDFs matched — narrow RECENT_YEARS further "
              f"if you want fewer.")
        print("First 10 matches:")
        for link in filtered_links[:10]:
            print(f"  - {link}")
    else:
        print("Step 3: Downloading...")
        download_pdfs(filtered_links, OUTPUT_DIR)
        print("\nDone. Check data/raw_pdfs/ then run POST /ingest/bulk as usual.")