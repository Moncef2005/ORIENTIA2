"""
Actual sign-in/sign-up happens client-side against Supabase Auth (the
frontend calls supabase.auth.signUp / signInWithPassword directly — see
frontend/lib/supabase.ts). This router only manages the `profiles` row that
extends auth.users with OrientIA-specific fields.
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import StudentProfile
from app.db.supabase_client import get_supabase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.put("/profile/{user_id}")
async def upsert_profile(user_id: str, profile: StudentProfile):
    supabase = get_supabase()
    row = {"id": user_id, **profile.model_dump(exclude={"target_field", "target_countries", "budget_eur_per_year", "free_text"})}
    res = supabase.table("profiles").upsert(row).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Échec de la mise à jour du profil.")
    return res.data[0]


@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    supabase = get_supabase()
    res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Profil introuvable.")
    return res.data
