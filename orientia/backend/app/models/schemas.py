from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field


class StudentProfile(BaseModel):
    full_name: str
    filiere: str = Field(..., description="e.g. 'Bac SM', 'Prépa ECG', 'L2 Informatique'")
    average_grade: float = Field(..., ge=0, le=20)
    languages: list[str] = []
    target_intake: str = Field(..., description="e.g. '2026-09'")
    target_field: str = Field(..., description="e.g. 'Computer Science'")
    target_countries: list[str] = ["France"]
    budget_eur_per_year: Optional[float] = None
    free_text: Optional[str] = Field(
        None, description="Anything else the student wants the AI to know"
    )


class ProgramMatch(BaseModel):
    program_id: int
    university: str
    program_name: str
    city: str
    degree_level: str
    match_score: float
    reasoning: str
    application_deadline: Optional[date]
    eligible: bool
    eligibility_notes: str


class MatchRequest(BaseModel):
    profile: StudentProfile
    top_k: int = 8


class AgentChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AgentChatRequest(BaseModel):
    user_id: str
    messages: list[AgentChatMessage]
    program_id: Optional[int] = None  # optional context: which program the chat is about


class ApplicationStatus(BaseModel):
    status: Literal[
        "considering", "in_progress", "submitted", "interview", "accepted", "rejected"
    ]


class ApplicationCreate(BaseModel):
    user_id: str
    program_id: int


class TranscriptExtraction(BaseModel):
    subject: str
    grade: float
    coefficient: Optional[float] = None
    year: Optional[str] = None


class WeakSpot(BaseModel):
    subject: str
    issue: str
    suggestion: str
