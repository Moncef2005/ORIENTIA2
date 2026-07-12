"""
Run once after applying schema.sql to populate the catalog with sample
programs (standing in for a full Campus France / Parcoursup scrape — see
app/scraper notes in the README for how to plug in a real crawler).

Usage:
    cd backend
    python -m scripts.seed_db
"""
import asyncio
import json
from pathlib import Path
from app.services.rag import ingest_program

DATA_PATH = Path(__file__).parent.parent / "app" / "data" / "seed_programs.json"


async def main():
    programs = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    for p in programs:
        requirements_text = p.pop("requirements_raw")
        p["requirements_raw"] = requirements_text
        program_id = await ingest_program(p, requirements_text)
        print(f"Ingested [{program_id}] {p['university']} — {p['program_name']}")


if __name__ == "__main__":
    asyncio.run(main())
