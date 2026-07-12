import tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.config import get_settings
from app.db.supabase_client import get_supabase
from app.services.document_ai import process_transcript

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()


@router.post("/transcript")
async def upload_transcript(user_id: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés.")

    contents = await file.read()
    if len(contents) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400, detail=f"Fichier trop volumineux (max {settings.max_upload_mb} Mo)."
        )

    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(contents)
        tmp.flush()
        try:
            result = await process_transcript(tmp.name)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    supabase = get_supabase()
    inserted = (
        supabase.table("transcripts")
        .insert(
            {
                "user_id": user_id,
                "file_name": file.filename,
                "extracted_grades": result["grades"],
                "flagged_weak_spots": result["weak_spots"],
                "raw_text": result["raw_text"],
            }
        )
        .execute()
    )

    return {
        "transcript_id": inserted.data[0]["id"],
        "grades": result["grades"],
        "weak_spots": result["weak_spots"],
    }
