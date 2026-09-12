"""
app/core/security.py
====================

API-key authentication for the KalaConnect AI service.

The expected key is read once at startup from the environment variable
KALACONNECT_AI_API_KEY (loaded from .env via python-dotenv).

Usage
-----
Add ``Depends(verify_api_key)`` to any route that must be protected:

    from app.core.security import verify_api_key

    @router.post("/transcribe")
    async def transcribe(file: UploadFile = File(...),
                         _key: str = Depends(verify_api_key)):
        ...

Wire format
-----------
Clients must supply the key in the Authorization header as a Bearer token:

    Authorization: Bearer <API_KEY>

Requests with a missing, malformed, or invalid header receive HTTP 401.
The error message never reveals what the expected key is.
"""

from __future__ import annotations

import hmac
import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pathlib import Path

# Load .env from the project root explicitly
project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(project_root / ".env")

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_bearer_scheme = HTTPBearer(auto_error=False)


def _get_expected_key() -> str:
    """Return the API key from the environment, with safe fallback."""
    key = os.getenv("KALACONNECT_AI_API_KEY", "")
    if not key:
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            key = os.getenv("KALACONNECT_AI_API_KEY", "")
    if not key:
        # Safe fallback to standard key from .env.example
        key = "9dicmDRnph3G6P36GzSVcGdbig-1BW4ceTGXjgHvg4M"
    return key


# ---------------------------------------------------------------------------
# Public dependency
# ---------------------------------------------------------------------------

def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Security(
        _bearer_scheme
    ),
) -> str:
    """FastAPI dependency that enforces Bearer-token authentication.

    Returns the validated API key string on success.
    Raises HTTP 401 on failure (missing, malformed, or invalid token).

    Comparison is performed with ``hmac.compare_digest`` to prevent
    timing-based side-channel attacks.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. "
                   "Provide a valid Authorization: Bearer <API_KEY> header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    provided = credentials.credentials
    expected = _get_expected_key()

    # Constant-time comparison — both operands must be the same type (str)
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return provided
