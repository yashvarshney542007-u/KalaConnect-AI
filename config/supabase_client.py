import os

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip()
SUPABASE_PUBLISHABLE_KEY = (os.getenv("SUPABASE_PUBLISHABLE_KEY") or "").strip()
SUPABASE_SECRET_KEY = (os.getenv("SUPABASE_SECRET_KEY") or "").strip()


class MissingSupabaseClient:
    """Graceful stub used when Supabase env vars are not configured."""

    def __getattr__(self, _name):
        raise RuntimeError(
            "Supabase is not configured. Set SUPABASE_URL, "
            "SUPABASE_PUBLISHABLE_KEY, and SUPABASE_SECRET_KEY in the environment."
        )

    def __bool__(self):
        return False


def _build_client(url: str, key: str) -> Client | MissingSupabaseClient:
    if not url or not key:
        return MissingSupabaseClient()

    try:
        return create_client(url, key)
    except Exception:
        return MissingSupabaseClient()


supabase: Client | MissingSupabaseClient = _build_client(
    SUPABASE_URL,
    SUPABASE_PUBLISHABLE_KEY,
)

supabase_admin: Client | MissingSupabaseClient = _build_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)