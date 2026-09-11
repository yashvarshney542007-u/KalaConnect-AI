# KalaConnect AI

AI microservice for the KalaConnect platform — Voice-to-text transcription and artisan craft image analysis.

## AI Models

| Service | Model | Details |
|---------|-------|---------|
| Voice   | faster-whisper (Whisper Small) | CPU, int8, multilingual |
| Vision  | HuggingFaceTB/SmolVLM-256M-Instruct | CPU / CUDA, lazy-loaded |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/` | Service status |
| GET  | `/health` | Health check |
| POST | `/api/voice/transcribe` | Transcribe audio (WAV, MP3, OGG, WEBM, MP4) |
| POST | `/api/vision/analyze` | Analyze craft image (JPG, PNG, WEBP, max 10 MB) |

See [`docs/AI_API.md`](docs/AI_API.md) for full request/response documentation.

## Running Locally

```bash
# 1. Activate the virtual environment
.\venv\Scripts\Activate.ps1          # Windows
source venv/bin/activate             # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the service
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Swagger UI: http://127.0.0.1:8000/docs

## Running Tests

```bash
pytest -q
```

## Vision Evaluation

See [`evaluation/README.md`](evaluation/README.md) for instructions on adding evaluation images and running the evaluation script.

```bash
python evaluation/evaluate_vision.py
```

## Project Structure

```
app/
├── api/
│   ├── voice.py          # POST /api/voice/transcribe
│   └── vision.py         # POST /api/vision/analyze
├── models/
│   ├── stt_model.py      # faster-whisper singleton
│   └── vision_model.py   # SmolVLM singleton (lazy-loaded)
├── services/
│   ├── voice_service.py
│   └── vision_service.py
└── main.py               # FastAPI app

tests/
├── test_health.py
├── voice/
│   └── test_voice_api.py
└── vision/
    └── test_vision_api.py

evaluation/
├── images/               # Add craft images here (not committed)
├── results/              # Auto-generated (not committed)
├── metadata.csv          # Ground-truth labels
└── evaluate_vision.py    # Evaluation script

docs/
└── AI_API.md             # Full API documentation
```

## Notes

- Model weights are downloaded automatically on first use and cached locally.
- Model weights are excluded from Git (see `.gitignore`).
- Do NOT commit model weights, audio files, or evaluation images to this repository.
- The frontend / backend must communicate with this service via HTTP only.
