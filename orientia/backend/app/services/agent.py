"""
The OrientIA agent: a genuine multi-step tool-calling loop, not a single
prompt-and-response chatbot. It can check deadlines, calculate eligibility,
draft a motivation letter, and flag missing documents by calling real
functions against the database — then reason over the results before
replying, looping until it has nothing left to do.

Uses the OpenAI-compatible chat.completions API so it works unchanged
against either Groq or OpenAI (both implement the same function-calling
shape) — see config.llm_provider.
"""
import json
from datetime import date
from functools import lru_cache
from openai import AsyncOpenAI
from app.config import get_settings
from app.db.supabase_client import get_supabase

_settings = get_settings()

LLM_MODEL = "llama-3.3-70b-versatile" if _settings.llm_provider == "groq" else "gpt-4o-mini"

SYSTEM_PROMPT = """Tu es OrientIA, l'assistant IA qui aide les étudiants marocains à \
postuler dans des programmes français et internationaux. Tu es un agent, pas un \
simple chatbot : utilise les outils à ta disposition pour vérifier des faits réels \
(dates limites, éligibilité, documents manquants) avant de répondre, plutôt que de \
deviner. Rédige toujours en français sauf si l'étudiant écrit en anglais ou en \
arabe. Sois concret, chaleureux mais direct, et signale clairement les urgences \
(dates limites proches)."""


@lru_cache
def get_llm_client() -> AsyncOpenAI:
    if _settings.llm_provider == "groq":
        return AsyncOpenAI(api_key=_settings.groq_api_key, base_url="https://api.groq.com/openai/v1")
    return AsyncOpenAI(api_key=_settings.openai_api_key)


# ---------------------------------------------------------------------------
# Tool implementations — these hit the real database, no hardcoded answers.
# ---------------------------------------------------------------------------

async def tool_check_deadline(program_id: int) -> dict:
    supabase = get_supabase()
    res = supabase.table("programs").select("program_name,university,application_deadline").eq(
        "id", program_id
    ).single().execute()
    if not res.data:
        return {"error": "programme introuvable"}
    deadline = res.data["application_deadline"]
    days_left = None
    if deadline:
        days_left = (date.fromisoformat(deadline) - date.today()).days
    return {**res.data, "days_left": days_left}


async def tool_calculate_eligibility(program_id: int, average_grade: float) -> dict:
    supabase = get_supabase()
    res = supabase.table("programs").select(
        "program_name,min_average_required,requirements_summary"
    ).eq("id", program_id).single().execute()
    if not res.data:
        return {"error": "programme introuvable"}
    min_avg = res.data.get("min_average_required")
    eligible = min_avg is None or average_grade >= float(min_avg)
    return {
        "program_name": res.data["program_name"],
        "min_average_required": min_avg,
        "student_average": average_grade,
        "eligible": eligible,
        "gap": None if eligible or min_avg is None else round(float(min_avg) - average_grade, 2),
    }


async def tool_flag_missing_documents(user_id: str, program_id: int) -> dict:
    supabase = get_supabase()
    app_res = (
        supabase.table("applications")
        .select("missing_documents")
        .eq("user_id", user_id)
        .eq("program_id", program_id)
        .execute()
    )
    standard_docs = [
        "Relevé de notes (2 dernières années)",
        "Lettre de motivation",
        "CV",
        "Passeport en cours de validité",
        "Justificatif de niveau de langue (TCF/DELF/IELTS)",
        "Lettres de recommandation",
    ]
    already_flagged = app_res.data[0]["missing_documents"] if app_res.data else []
    provided = already_flagged if already_flagged else []
    missing = [d for d in standard_docs if d not in provided]
    return {"missing_documents": missing, "total_required": len(standard_docs)}


async def tool_draft_motivation_letter(
    program_name: str, university: str, student_strengths: str, student_field: str
) -> dict:
    """This tool itself calls the LLM (a sub-completion) to draft a first-pass
    lettre de motivation — the outer agent then presents/edits it."""
    client = get_llm_client()
    completion = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu rédiges une lettre de motivation académique en français, "
                    "registre soutenu, 300-400 mots, structure classique "
                    "(accroche, parcours, motivation précise pour ce programme, "
                    "projet professionnel, formule de politesse)."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Programme: {program_name} à {university}. Domaine: {student_field}. "
                    f"Points forts de l'étudiant: {student_strengths}."
                ),
            },
        ],
        temperature=0.6,
    )
    return {"draft": completion.choices[0].message.content}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_deadline",
            "description": "Vérifie la date limite de candidature réelle d'un programme.",
            "parameters": {
                "type": "object",
                "properties": {"program_id": {"type": "integer"}},
                "required": ["program_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_eligibility",
            "description": "Calcule si la moyenne de l'étudiant satisfait le seuil du programme.",
            "parameters": {
                "type": "object",
                "properties": {
                    "program_id": {"type": "integer"},
                    "average_grade": {"type": "number"},
                },
                "required": ["program_id", "average_grade"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "flag_missing_documents",
            "description": "Liste les documents encore manquants pour une candidature donnée.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "program_id": {"type": "integer"},
                },
                "required": ["user_id", "program_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draft_motivation_letter",
            "description": "Rédige un premier brouillon de lettre de motivation pour un programme.",
            "parameters": {
                "type": "object",
                "properties": {
                    "program_name": {"type": "string"},
                    "university": {"type": "string"},
                    "student_strengths": {"type": "string"},
                    "student_field": {"type": "string"},
                },
                "required": ["program_name", "university", "student_strengths", "student_field"],
            },
        },
    },
]

TOOL_DISPATCH = {
    "check_deadline": tool_check_deadline,
    "calculate_eligibility": tool_calculate_eligibility,
    "flag_missing_documents": tool_flag_missing_documents,
    "draft_motivation_letter": tool_draft_motivation_letter,
}


async def run_agent(messages: list[dict], max_steps: int = 6) -> list[dict]:
    """Runs the agentic loop until the model stops calling tools or max_steps
    is hit. Returns the full updated message list (including tool calls/
    results) so the frontend can render the agent's reasoning trail."""
    client = get_llm_client()
    conversation = [{"role": "system", "content": SYSTEM_PROMPT}, *messages]

    for _ in range(max_steps):
        completion = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=conversation,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.4,
        )
        message = completion.choices[0].message
        conversation.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            break  # agent produced a final answer, stop looping

        for tool_call in message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments or "{}")
            handler = TOOL_DISPATCH.get(fn_name)
            result = await handler(**fn_args) if handler else {"error": "outil inconnu"}
            conversation.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                }
            )

    return conversation
