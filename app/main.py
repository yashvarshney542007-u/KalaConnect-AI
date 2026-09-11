from fastapi import FastAPI

from app.api.voice import router as voice_router


app = FastAPI(
    title="KalaConnect AI",
    description="AI services for KalaConnect - Image, Voice and Speech AI",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "KalaConnect AI service is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "kalaconnect-ai"
    }


app.include_router(voice_router)