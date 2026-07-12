from fastapi import APIRouter, HTTPException
from app.models.schemas import MatchRequest, ProgramMatch
from app.services.rag import match_programs

router = APIRouter(prefix="/programs", tags=["programs"])


@router.post("/match", response_model=list[ProgramMatch])
async def match(request: MatchRequest):
    try:
        return await match_programs(request.profile, request.top_k)
    except Exception as exc:  # noqa: BLE001 — surfaced to client deliberately
        raise HTTPException(status_code=500, detail=str(exc)) from exc
