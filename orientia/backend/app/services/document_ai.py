"""
Document AI pipeline for uploaded transcripts (relevés de notes):

1. Extract raw text from the PDF (pdfplumber — works for text-based PDFs;
   falls back to a clear error for scanned/image PDFs rather than silently
   returning garbage — OCR can be added later via pytesseract if needed).
2. Ask the LLM to parse grades into structured rows. We ask for JSON with a
   strict schema rather than regex, because French transcripts vary a lot
   between lycées/facultés (columns, coefficients, semester layout).
3. Ask the LLM to flag weak spots (grades that would concern an admissions
   committee) and suggest how to reframe them in the motivation letter —
   this is intentionally a separate call from extraction so a parsing
   mistake can't silently corrupt the advice.
"""
import json
import pdfplumber
from app.services.agent import get_llm_client, LLM_MODEL

EXTRACTION_PROMPT = """Tu extrais les notes d'un relevé de notes marocain/français. \
Réponds UNIQUEMENT avec un tableau JSON, sans texte autour, au format: \
[{"subject": str, "grade": float, "coefficient": float|null, "year": str|null}]. \
Ignore les lignes qui ne sont pas des matières notées (en-têtes, totaux, moyennes \
générales déjà agrégées)."""

WEAKSPOT_PROMPT = """Tu es conseiller d'admission. Voici des notes extraites d'un \
relevé. Identifie les 2-4 points faibles les plus susceptibles d'inquiéter un jury \
d'admission français (matière clé avec note basse, baisse entre deux années, etc.), \
et pour chacun propose une phrase concrète à intégrer dans une lettre de motivation \
pour recontextualiser ce point (ex: redressement, projet extra-scolaire compensant \
la matière, contexte particulier). Réponds UNIQUEMENT en JSON: \
[{"subject": str, "issue": str, "suggestion": str}]"""


def extract_pdf_text(file_path: str) -> str:
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    full_text = "\n".join(text_parts).strip()
    if len(full_text) < 30:
        raise ValueError(
            "Impossible d'extraire du texte de ce PDF — il s'agit probablement "
            "d'un scan image plutôt que d'un PDF texte. L'OCR n'est pas encore "
            "activé dans cette version."
        )
    return full_text


async def extract_grades(raw_text: str) -> list[dict]:
    client = get_llm_client()
    completion = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": raw_text[:8000]},  # guard against huge PDFs
        ],
        temperature=0,
    )
    raw = completion.choices[0].message.content.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


async def flag_weak_spots(grades: list[dict]) -> list[dict]:
    client = get_llm_client()
    completion = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": WEAKSPOT_PROMPT},
            {"role": "user", "content": json.dumps(grades, ensure_ascii=False)},
        ],
        temperature=0.3,
    )
    raw = completion.choices[0].message.content.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


async def process_transcript(file_path: str) -> dict:
    raw_text = extract_pdf_text(file_path)
    grades = await extract_grades(raw_text)
    weak_spots = await flag_weak_spots(grades) if grades else []
    return {"raw_text": raw_text, "grades": grades, "weak_spots": weak_spots}
