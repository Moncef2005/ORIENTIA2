"""
Central configuration. All secrets come from environment variables —
see .env.example for the full list. Never hardcode keys here.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Supabase ---
    supabase_url: str = ""
    supabase_service_key: str = ""  # server-side only, never expose to frontend
    supabase_anon_key: str = ""

    # --- LLM provider ---
    # OrientIA is provider-agnostic: swap between Groq (fast/free-tier) and
    # OpenAI by changing llm_provider. Both use OpenAI-compatible function-calling.
    llm_provider: str = "groq"  # "groq" | "openai"
    groq_api_key: str = ""
    openai_api_key: str = ""  # only needed if llm_provider="openai"

    # --- Embeddings (used for RAG / pgvector) ---
    # Runs locally via sentence-transformers — free, no API key, no per-call cost.
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dims: int = 384

    # --- App ---
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:3000"]
    max_upload_mb: int = 15

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
