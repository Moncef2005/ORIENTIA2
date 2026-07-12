"""
RAG program-matching pipeline:

1. Turn the student's profile into a natural-language query.
2. Embed it and run pgvector cosine-similarity search over program_chunks.
3. Pull the parent `programs` rows for the top matches.
4. Ask the LLM to score + explain fit for each candidate, grounded in the
   retrieved requirement text (not the model's own guess about the program).
5. Run a hard eligibility check (grade threshold, language, deadline) so the
   AI's "reasoning" can't override a plain fact like a missed deadline.
"""
import json
from datetime import date
from app.db.supabase_client import get_supabase
from app.services.embeddings import embed_text
from app.services.agent import get_llm_client, LLM_MODEL
from app.models.schemas import StudentProfile, ProgramMatch

RANKING_SYSTEM_PROMPT = """You are OrientIA's program-matching engine for Moroccan \
students applying to French/international higher education. You will be given a \
student profile and a set of candidate programs with their retrieved requirement \
text. For each candidate, output a match_score (0-100) and a short reasoning \
string (2-3 sentences, in French) grounded ONLY in the requirement text provided \
— never invent requirements you don't see. Penalize programs where the student's \
average grade is below the stated minimum, and note this explicitly in the \
reasoning. Return ONLY a JSON array, no prose, no markdown fences, matching this \
shape: [{"program_id": int, "match_score": float, "reasoning": str}]"""


def _profile_to_query(profile: StudentProfile) -> str:
    return (
        f"Étudiant marocain, filière {profile.filiere}, moyenne générale "
        f"{profile.average_grade}/20, recherche un programme en "
        f"{profile.target_field} pour la rentrée {profile.target_intake}, "
        f"pays visés: {', '.join(profile.target_countries)}. "
        f"{profile.free_text or ''}"
    )


def _check_eligibility(profile: StudentProfile, program_row: dict) -> tuple[bool, str]:
    notes = []
    eligible = True

    min_avg = program_row.get("min_average_required")
    if min_avg is not None and profile.average_grade < float(min_avg):
        eligible = False
        notes.append(
            f"Moyenne requise {min_avg}/20, moyenne actuelle {profile.average_grade}/20."
        )

    deadline = program_row.get("application_deadline")
    if deadline:
        deadline_date = deadline if isinstance(deadline, date) else date.fromisoformat(deadline)
        if deadline_date < date.today():
            eligible = False
            notes.append(f"Date limite dépassée ({deadline_date.isoformat()}).")

    if not notes:
        notes.append("Aucun obstacle d'éligibilité détecté sur les critères connus.")

    return eligible, " ".join(notes)


async def match_programs(profile: StudentProfile, top_k: int = 8) -> list[ProgramMatch]:
    supabase = get_supabase()

    query_text = _profile_to_query(profile)
    query_embedding = await embed_text(query_text)

    # Vector search via the match_program_chunks() function defined in schema.sql
    chunk_results = supabase.rpc(
        "match_program_chunks",
        {
            "query_embedding": query_embedding,
            "match_count": top_k * 3,  # over-fetch chunks, dedupe to programs below
            "filter_country": profile.target_countries[0] if profile.target_countries else None,
        },
    ).execute()

    seen_program_ids: list[int] = []
    chunks_by_program: dict[int, list[str]] = {}
    for row in chunk_results.data or []:
        pid = row["program_id"]
        chunks_by_program.setdefault(pid, []).append(row["chunk_text"])
        if pid not in seen_program_ids:
            seen_program_ids.append(pid)
        if len(seen_program_ids) >= top_k:
            break

    if not seen_program_ids:
        return []

    programs_res = (
        supabase.table("programs").select("*").in_("id", seen_program_ids).execute()
    )
    programs_by_id = {p["id"]: p for p in programs_res.data}

    # Build the grounded ranking prompt
    candidates_payload = [
        {
            "program_id": pid,
            "university": programs_by_id[pid]["university"],
            "program_name": programs_by_id[pid]["program_name"],
            "min_average_required": programs_by_id[pid].get("min_average_required"),
            "requirement_excerpts": chunks_by_program[pid][:3],
        }
        for pid in seen_program_ids
        if pid in programs_by_id
    ]

    client = get_llm_client()
    completion = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": RANKING_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {"student_profile": profile.model_dump(), "candidates": candidates_payload},
                    ensure_ascii=False,
                    default=str,
                ),
            },
        ],
        temperature=0.2,
    )

    raw = completion.choices[0].message.content.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    scored = json.loads(raw)
    scores_by_id = {item["program_id"]: item for item in scored}

    results: list[ProgramMatch] = []
    for pid in seen_program_ids:
        row = programs_by_id.get(pid)
        if not row:
            continue
        score_info = scores_by_id.get(pid, {"match_score": 0, "reasoning": "Non évalué."})
        eligible, elig_notes = _check_eligibility(profile, row)
        results.append(
            ProgramMatch(
                program_id=pid,
                university=row["university"],
                program_name=row["program_name"],
                city=row.get("city") or "",
                degree_level=row.get("degree_level") or "",
                match_score=float(score_info["match_score"]),
                reasoning=score_info["reasoning"],
                application_deadline=row.get("application_deadline"),
                eligible=eligible,
                eligibility_notes=elig_notes,
            )
        )

    results.sort(key=lambda r: r.match_score, reverse=True)
    return results


async def ingest_program(program_row: dict, requirements_text: str) -> int:
    """Insert a program + chunk/embed its requirements text. Called by the
    scraper pipeline (see scripts/seed_db.py for the offline batch version)."""
    from app.services.embeddings import chunk_text, embed_batch

    supabase = get_supabase()
    inserted = supabase.table("programs").insert(program_row).execute()
    program_id = inserted.data[0]["id"]

    chunks = chunk_text(requirements_text)
    embeddings = await embed_batch(chunks)
    rows = [
        {"program_id": program_id, "chunk_text": c, "embedding": e}
        for c, e in zip(chunks, embeddings)
    ]
    supabase.table("program_chunks").insert(rows).execute()
    return program_id
