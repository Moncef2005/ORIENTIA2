from fastapi import APIRouter, HTTPException
from app.models.schemas import ApplicationCreate, ApplicationStatus
from app.db.supabase_client import get_supabase

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/{user_id}")
async def list_applications(user_id: str):
    supabase = get_supabase()
    res = (
        supabase.table("applications")
        .select("*, programs(*)")
        .eq("user_id", user_id)
        .execute()
    )
    return res.data


@router.post("")
async def create_application(payload: ApplicationCreate):
    supabase = get_supabase()
    try:
        res = supabase.table("applications").insert(payload.model_dump()).execute()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return res.data[0]


@router.patch("/{application_id}/status")
async def update_status(application_id: int, payload: ApplicationStatus):
    supabase = get_supabase()
    res = (
        supabase.table("applications")
        .update({"status": payload.status})
        .eq("id", application_id)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Candidature introuvable.")
    return res.data[0]
