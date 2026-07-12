"""
Real ingestion pipeline sketch for scraping program requirements from
university admissions pages (Parcoursup fiches, Campus France pages,
université "modalités d'admission" pages).

NOT run automatically — target sites vary wildly in structure, have terms
of service around scraping, and change layout often, so this is meant as a
starting point you adapt per source rather than a generic crawler.

For the demo, backend/app/data/seed_programs.json + scripts/seed_db.py
populate the catalog with realistic sample data so the RAG pipeline can be
exercised end-to-end without needing live scraping.

Recommended real approach:
1. Start with an allow-list of specific program URLs you've manually
   identified (rather than crawling), since Campus France/Parcoursup pages
   need to be attributed to specific programs, not just generic pages.
2. Respect robots.txt and each site's terms of use; prefer official data
   exports/APIs where they exist over scraping HTML.
3. Use BeautifulSoup for structured extraction, falling back to readability
   -style text extraction for messy pages.
4. Re-run periodically (e.g. weekly during application season) since
   deadlines and thresholds change.
"""
import httpx
from bs4 import BeautifulSoup


async def fetch_page_text(url: str, timeout: float = 15.0) -> str:
    """Fetch a page and return its main visible text — a simple starting
    point; swap in trafilatura or readability-lxml for messier pages."""
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        resp = await client.get(url, headers={"User-Agent": "OrientIA-research/0.1"})
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ").split())


# Example of how you'd wire a fetched page into the RAG ingestion pipeline:
#
#   from app.services.rag import ingest_program
#
#   text = await fetch_page_text("https://www.univ-example.fr/admission-l3-info")
#   await ingest_program(
#       {
#           "source": "university",
#           "source_url": "https://www.univ-example.fr/admission-l3-info",
#           "university": "Université Example",
#           "program_name": "Licence Informatique",
#           "degree_level": "L3",
#           "field": "Computer Science",
#           "city": "Example City",
#           "min_average_required": 13.0,
#           "application_deadline": "2027-03-01",
#       },
#       requirements_text=text,
#   )
