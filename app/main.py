from fastapi import FastAPI

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
