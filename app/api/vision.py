import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.security import verify_api_key
from app.core.state import pipeline_state
from app.services.vision_service import analyze_image

router = APIRouter(
    prefix="/api/vision",
    tags=["Vision"]
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp"
}


@router.post("/analyze")
def analyze(
    file: UploadFile = File(...),
    _key: str = Depends(verify_api_key),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type: '{file.content_type}'. Supported formats are JPG/JPEG, PNG, WEBP."
        )

    suffix = os.path.splitext(file.filename or "")[1] or ".jpg"

    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the 10 MB limit."
        )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp:
        temp.write(content)
        temp_path = temp.name

    try:
        analysis = analyze_image(temp_path)
        pipeline_state.set_vision(analysis)

        return {
            "success": True,
            "filename": file.filename or f"image{suffix}",
            "analysis": analysis
        }

    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
