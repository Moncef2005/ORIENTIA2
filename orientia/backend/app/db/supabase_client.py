"""
Thin wrapper around the Supabase client so the rest of the app never
imports the SDK directly (makes it easy to swap/mocking in tests).
"""
from functools import lru_cache
from supabase import create_client, Client
from app.config import get_settings


@lru_cache
def get_supabase() -> Client:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        raise RuntimeError(
            "Supabase is not configured. Set SUPABASE_URL and "
            "SUPABASE_SERVICE_KEY in your .env file."
        )
    return create_client(settings.supabase_url, settings.supabase_service_key)
