# KalaConnect AI — API Documentation

This document describes all HTTP endpoints provided by the KalaConnect AI service.

## Overview

The KalaConnect AI service runs as a standalone FastAPI application and provides:

- **Voice-to-text transcription** (faster-whisper, Whisper Small)
- **Visual craft analysis** (HuggingFaceTB/SmolVLM-256M-Instruct)

### Architecture

```
KalaConnect Frontend / Backend
        │  HTTP
        ▼
KalaConnect AI Service  (FastAPI, port 8000)
        │
        ├── Voice: faster-whisper (Whisper Small, CPU, int8)
        └── Vision: SmolVLM-256M-Instruct (CPU / CUDA)
```

> **Important:** The frontend and backend communicate with the AI service
> through **HTTP only**. Do NOT import Python AI modules directly into a
> JavaScript/TypeScript or non-Python service. Model weights must not be
> committed to the repository.

---

## Base URL

```
http://127.0.0.1:8000
```

---

## Endpoints

---

### GET /health

Returns the health status of the AI service.

**Request**

```http
GET /health HTTP/1.1
Host: 127.0.0.1:8000
```

**Example cURL**

```bash
curl http://127.0.0.1:8000/health
```

**Example Response (200 OK)**

```json
{
  "status": "ok",
  "service": "kalaconnect-ai"
}
```

---

### GET /

Returns a confirmation that the service is running.

**Example Response (200 OK)**

```json
{
  "message": "KalaConnect AI service is running"
}
```

---

### POST /api/voice/transcribe

Transcribes an audio file to text using faster-whisper (Whisper Small).

**Request**

| Property        | Value                     |
|-----------------|---------------------------|
| Method          | `POST`                    |
| URL             | `/api/voice/transcribe`   |
| Content-Type    | `multipart/form-data`     |
| Field           | `file` (audio file)       |

**Supported audio formats**

| Format  | MIME type           |
|---------|---------------------|
| WAV     | `audio/wav`         |
| MP3     | `audio/mpeg`        |
| MP3     | `audio/mp3`         |
| WAV     | `audio/x-wav`       |
| WebM    | `audio/webm`        |
| MP4     | `audio/mp4`         |
| OGG     | `audio/ogg`         |

**Example cURL**

```bash
curl -X POST http://127.0.0.1:8000/api/voice/transcribe \
  -H "accept: application/json" \
  -F "file=@recording.wav"
```

**Example Python**

```python
import requests

with open("recording.wav", "rb") as f:
    response = requests.post(
        "http://127.0.0.1:8000/api/voice/transcribe",
        files={"file": ("recording.wav", f, "audio/wav")},
    )
print(response.json())
```

**Example Response (200 OK)**

```json
{
  "success": true,
  "text": "नमस्ते, मेरा नाम राज है।",
  "language": "hi",
  "language_probability": 0.97
}
```

**Error Responses**

| Status | Condition                        | Detail                                    |
|--------|----------------------------------|-------------------------------------------|
| 400    | Unsupported file type uploaded   | `"Unsupported audio type: image/jpeg"`    |

---

### POST /api/vision/analyze

Analyzes a craft or artisan product image using SmolVLM-256M-Instruct.

**Request**

| Property        | Value                       |
|-----------------|-----------------------------|
| Method          | `POST`                      |
| URL             | `/api/vision/analyze`       |
| Content-Type    | `multipart/form-data`       |
| Field           | `file` (image file)         |
| Max file size   | 10 MB                       |

**Supported image formats**

| Format  | MIME type       |
|---------|-----------------|
| JPEG    | `image/jpeg`    |
| JPEG    | `image/jpg`     |
| PNG     | `image/png`     |
| WebP    | `image/webp`    |

**Example cURL**

```bash
curl -X POST http://127.0.0.1:8000/api/vision/analyze \
  -H "accept: application/json" \
  -F "file=@pottery.jpg"
```

**Example Python**

```python
import requests

with open("pottery.jpg", "rb") as f:
    response = requests.post(
        "http://127.0.0.1:8000/api/vision/analyze",
        files={"file": ("pottery.jpg", f, "image/jpeg")},
    )
print(response.json())
```

**Example Response (200 OK)**

```json
{
  "success": true,
  "filename": "pottery.jpg",
  "analysis": {
    "craft": "pottery",
    "material": "terracotta clay",
    "product_type": "earthen pot",
    "visual_description": "Handcrafted terracotta pot with traditional geometric motifs in ochre and brown tones.",
    "colors": ["brown", "ochre", "red"],
    "design_features": ["etched geometric patterns", "incised lines"],
    "craftsmanship_features": ["wheel-thrown pottery", "hand-etched decoration"],
    "possible_region": "Rajasthan",
    "confidence": 0.85
  }
}
```

**Field descriptions**

| Field                    | Type     | Description                                                                 |
|--------------------------|----------|-----------------------------------------------------------------------------|
| `success`                | boolean  | `true` if the image was analyzed                                            |
| `filename`               | string   | Name of the uploaded file                                                   |
| `analysis.craft`         | string   | Likely craft category or `"unknown"`                                        |
| `analysis.material`      | string   | Visually identifiable material or `"unknown"`                               |
| `analysis.product_type`  | string   | What the object appears to be or `"unknown"`                                |
| `analysis.visual_description` | string | Concise description for an artisan catalogue                           |
| `analysis.colors`        | array    | Dominant visible colors                                                     |
| `analysis.design_features` | array  | Visible motifs, patterns, or decorative elements                            |
| `analysis.craftsmanship_features` | array | Visible handmade/artisan characteristics                         |
| `analysis.possible_region` | string | Geographic association (only if visually justified) or `"unknown"`        |
| `analysis.confidence`    | float    | Model-estimated confidence between 0.0 and 1.0                             |

> **Note on confidence:** The confidence value is self-reported by the model.
> It is NOT a calibrated scientific probability.

**What the model will NOT claim:**

- Exact artisan identity
- Exact geographic location
- Exact material composition when not visually determinable
- Exact age or historical claims
- Authenticity
- Price

When these cannot be determined, the model returns `"unknown"`.

**Error Responses**

| Status | Condition                     | Detail                                          |
|--------|-------------------------------|--------------------------------------------------|
| 400    | Unsupported file type         | `"Unsupported image type: 'application/pdf'..."`|
| 400    | File exceeds 10 MB            | `"File size exceeds the 10 MB limit."`          |

---

## Running the AI Service Locally

```bash
# 1. Navigate to the project directory
cd KalaConnect-AI

# 2. Activate the virtual environment
.\venv\Scripts\Activate.ps1        # Windows
source venv/bin/activate           # macOS / Linux

# 3. Start the service
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Model Notes

### Voice — faster-whisper

- **Library:** [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- **Model:** Whisper Small
- **Device:** CPU (int8 quantized)
- **Languages:** Multilingual; optimized for Hindi

### Vision — SmolVLM-256M-Instruct

- **Model:** [HuggingFaceTB/SmolVLM-256M-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct)
- **Device:** CUDA if available, otherwise CPU
- **Loading:** Lazy-loaded on first request (server starts immediately)
- **Weights:** Downloaded automatically on first use; cached locally
- **Weights not committed:** Model weights are excluded by `.gitignore`
