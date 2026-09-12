import sys
from pathlib import Path

# Ensure project root is in sys.path so direct execution (e.g. IDE Run button) works
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables from .env (no-op if file does not exist)
load_dotenv()

import uvicorn
from fastapi import FastAPI

from app.api.price import router as price_router
from app.api.voice import router as voice_router
from app.api.vision import router as vision_router


app = FastAPI(
    title="KalaConnect AI",
    description="AI services for KalaConnect - Image, Voice and Speech AI",
    version="1.0.0",
)


from fastapi.responses import HTMLResponse

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


@app.get("/", response_class=HTMLResponse)
@app.get("/ui", response_class=HTMLResponse)
def root():
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>KalaConnect AI service is running</h1>")


@app.get("/api/info")
def api_info():
    return {
        "message": "KalaConnect AI service is running",
        "docs": "/docs",
        "health": "/health",
        "ui": "/ui"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "kalaconnect-ai"
    }


app.include_router(price_router)
app.include_router(voice_router)
app.include_router(vision_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)