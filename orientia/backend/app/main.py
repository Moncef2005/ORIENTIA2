from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth, programs, agent, documents, applications

settings = get_settings()

app = FastAPI(
    title="OrientIA API",
    description="AI platform helping Moroccan students find and apply to French/international university programs.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(programs.router)
app.include_router(agent.router)
app.include_router(documents.router)
app.include_router(applications.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
