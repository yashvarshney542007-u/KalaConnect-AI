import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.security import verify_api_key
from app.services.voice_service import transcribe_audio


router = APIRouter(
    prefix="/api/voice",
    tags=["Voice"]
)


@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    _key: str = Depends(verify_api_key),
):

    allowed_types = {
        "audio/wav",
        "audio/mpeg",
        "audio/mp3",
        "audio/x-wav",
        "audio/webm",
        "audio/mp4",
        "audio/ogg"
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio type: {file.content_type}"
        )

    suffix = os.path.splitext(file.filename or "")[1] or ".wav"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp:
        content = await file.read()
        temp.write(content)
        temp_path = temp.name

    try:
        result = transcribe_audio(temp_path)

        return {
            "success": True,
            **result
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)