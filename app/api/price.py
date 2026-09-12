"""
app/api/price.py
================
FastAPI router for the price prediction endpoints.

POST /api/price/predict              - JSON structured prediction
POST /api/price/predict-with-media   - Form + file upload (manual fields)
POST /api/price/predict-smart        - Fully automatic: Image -> Vision AI,
                                       Audio -> Voice AI, auto-derive costs
"""

import os
import sys
import tempfile
from pathlib import Path

# Ensure project root is on sys.path so ml.* imports resolve when running
# via `uvicorn app.main:app` from any working directory.
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Optional
from fastapi import APIRouter, HTTPException, File, Form, UploadFile

from app.schemas.price import PricePredictRequest, PricePredictResponse
from ml.feature_extractor import extract_features
from ml.price_predictor import predict

router = APIRouter(
    prefix="/api/price",
    tags=["Price Prediction"],
)

# ---------------------------------------------------------------------------
# Complexity score lookup by craft type (used in predict-smart auto-derive)
# ---------------------------------------------------------------------------
CRAFT_COMPLEXITY = {
    "blue pottery": 7.0,
    "pashmina": 9.5,
    "pashmina weaving": 9.5,
    "dhokra": 8.0,
    "dhokra metal craft": 8.0,
    "wood carving": 7.5,
    "zardozi": 9.0,
    "block printing": 5.0,
    "weaving": 6.5,
    "embroidery": 8.5,
    "pottery": 5.5,
    "terracotta": 5.0,
    "metalwork": 7.0,
    "jewelry": 8.0,
    "painting": 7.0,
    "leather": 5.5,
}


@router.post("/predict", response_model=PricePredictResponse)
def predict_price(body: PricePredictRequest):
    """Predict the fair market price (INR) for a handicraft item.

    Accepts structured data from the Vision AI, the artisan, and
    derived/computed fields. Returns the CatBoost model's prediction.
    """
    try:
        features = extract_features(
            ai_data=body.ai_data.model_dump(),
            artisan_data=body.artisan_data.model_dump(),
            derived_data=body.derived_data.model_dump(),
        )
        price = predict(features)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return PricePredictResponse(
        success=True,
        predicted_price_inr=round(price, 2),
        features_used=features,
    )


@router.post("/predict-with-media", response_model=PricePredictResponse)
async def predict_price_with_media(
    image: Optional[UploadFile] = File(None, description="Optional product photograph (JPG/PNG)"),
    audio: Optional[UploadFile] = File(None, description="Optional voice recording (WAV/MP3)"),
    product_name: str = Form("Blue Pottery Vase", description="Product Name"),
    craft: str = Form("Blue Pottery", description="Craft form (e.g. Blue Pottery, Pashmina, Wood Carving)"),
    material: str = Form("Ceramic", description="Material (e.g. Ceramic, Silk, Brass, Teak Wood)"),
    technique: str = Form("Hand-painted", description="Technique used"),
    state: str = Form("Rajasthan", description="Artisan State"),
    district: str = Form("Jaipur", description="District / Region"),
    artisan_skill_level: str = Form("Skilled", description="Skill Level: Skilled, Master, Semi-Skilled"),
    market_channel: str = Form("Artisan Direct", description="Market Channel"),
    size_length_cm: float = Form(20.0, description="Length in cm"),
    size_width_cm: float = Form(20.0, description="Width in cm"),
    size_height_cm: float = Form(30.0, description="Height in cm"),
    weight_kg: float = Form(1.8, description="Weight in kg"),
    labor_days: float = Form(3.0, description="Days of labor"),
    material_cost_inr: float = Form(500.0, description="Cost of raw materials in INR"),
    labor_cost_inr: float = Form(900.0, description="Cost of labor in INR"),
    complexity_score: float = Form(6.5, description="Craft complexity score (1 - 10)"),
):
    """Predict fair market price with direct Image & Voice file upload via Swagger Docs.

    You can attach your actual handicraft photo and voice recording right here in `/docs`!
    """
    ai_data = {
        "productName": product_name,
        "craft": craft,
        "material": material,
        "technique": technique,
        "description": f"Uploaded product with image: {image.filename if image else 'None'}, audio: {audio.filename if audio else 'None'}"
    }
    artisan_data = {
        "state": state,
        "region": district,
        "district": district,
        "size_length_cm": size_length_cm,
        "size_width_cm": size_width_cm,
        "size_height_cm": size_height_cm,
        "weight_kg": weight_kg,
        "labor_days": labor_days,
        "artisan_skill_level": artisan_skill_level,
        "production_quantity": 10,
        "market_channel": market_channel,
    }
    derived_data = {
        "product_type": craft,
        "labor_hours": labor_days * 8.0,
        "complexity_score": complexity_score,
        "material_cost_inr": material_cost_inr,
        "labor_cost_inr": labor_cost_inr,
        "overhead_cost_inr": round(material_cost_inr * 0.25, 2),
        "market_demand_score": 7.2,
        "seasonality_score": 5.0,
    }

    try:
        features = extract_features(
            ai_data=ai_data,
            artisan_data=artisan_data,
            derived_data=derived_data,
        )
        price = predict(features)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return PricePredictResponse(
        success=True,
        predicted_price_inr=round(price, 2),
        features_used=features,
    )


@router.post(
    "/predict-smart",
    response_model=PricePredictResponse,
    summary="[SMART] Predict Price via Image + Voice (AI auto-fills craft/material/description)",
)
async def predict_price_smart(
    # ── Media inputs ────────────────────────────────────────────────────────
    image: Optional[UploadFile] = File(
        None,
        description=(
            "📸 Product photograph (JPG/PNG/WEBP). "
            "Vision AI will READ the image and auto-fill: craft, material, technique, product_type, description."
        ),
    ),
    audio: Optional[UploadFile] = File(
        None,
        description=(
            "🎙️ Artisan voice note (WAV/MP3/OGG). "
            "Whisper will TRANSCRIBE this and use it as productName + description."
        ),
    ),
    # ── Artisan data — you only fill this part ──────────────────────────────
    state: str = Form("Rajasthan", description="Artisan state (e.g. Rajasthan, West Bengal, Jammu & Kashmir)"),
    district: str = Form("Jaipur", description="Artisan district / city"),
    artisan_skill_level: str = Form("Skilled", description="Skilled | Master | Semi-Skilled | Beginner"),
    market_channel: str = Form("Artisan Direct", description="Artisan Direct | Fair Trade | Exhibition | E-Commerce"),
    size_length_cm: float = Form(20.0, description="Product length in cm"),
    size_width_cm: float = Form(20.0, description="Product width in cm"),
    size_height_cm: float = Form(30.0, description="Product height in cm"),
    weight_kg: float = Form(1.8, description="Product weight in kg"),
    labor_days: float = Form(3.0, description="Days of artisan labour"),
    material_cost_inr: float = Form(500.0, description="Raw material cost in INR"),
    production_quantity: int = Form(10, description="Batch production quantity"),
    # ── Optional manual overrides ───────────────────────────────────────────
    override_craft: str = Form("", description="(Optional) Override the craft type detected by Vision AI"),
    override_product_name: str = Form("", description="(Optional) Override the product name from Voice transcript"),
):
    """
    ## 🤖 Smart Multimodal Price Prediction

    Upload an **image** + **voice recording** and fill only the artisan
    physical details — the AI handles the rest automatically.

    ### What the AI does automatically:

    | Data Group | Source | Fields auto-filled |
    |---|---|---|
    | `ai_data.craft` | 📸 Vision AI reads image | craft type (Blue Pottery, Pashmina…) |
    | `ai_data.material` | 📸 Vision AI reads image | material (Ceramic, Silk, Wood…) |
    | `ai_data.technique` | 📸 Vision AI reads image | technique (Hand-painted, Woven…) |
    | `ai_data.description` | 📸 Vision AI / 🎙️ Voice transcript | product description |
    | `ai_data.productName` | 🎙️ Voice transcript | what the artisan said |
    | `derived_data.complexity_score` | ⚙️ Auto from craft type | 1–10 complexity |
    | `derived_data.labor_cost_inr` | ⚙️ labor_days × ₹350 | estimated labour cost |
    | `derived_data.overhead_cost_inr` | ⚙️ material_cost × 25% | overhead |
    | `derived_data.market_demand_score` | ⚙️ From craft complexity | demand estimate |

    ### What YOU fill (artisan_data):
    State, district, skill level, market channel, size, weight, labor days, material cost.

    ---
    No need to manually build the full JSON request — upload media and let the AI do it!
    """
    image_path = None
    audio_path = None
    transcript = ""
    vision_result = {}

    try:
        # ── Step 1: Vision AI → auto-fill ai_data ───────────────────────
        if image is not None:
            suffix = os.path.splitext(image.filename or "")[1] or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(await image.read())
                image_path = tmp.name
            try:
                from app.services.vision_service import analyze_image
                vision_result = analyze_image(image_path)
            except Exception as e:
                vision_result = {
                    "craft": "Handicraft",
                    "material": "Mixed",
                    "product_type": "Artisan Product",
                    "visual_description": f"Vision analysis failed: {str(e)[:60]}",
                    "technique": "Traditional",
                }

        craft = override_craft or vision_result.get("craft") or "Handicraft"
        material = vision_result.get("material") or "Mixed"
        technique = vision_result.get("technique") or "Traditional"
        product_type = vision_result.get("product_type") or craft
        visual_description = (
            vision_result.get("visual_description")
            or f"Handcrafted {craft} made from {material}"
        )

        # ── Step 2: Voice AI → auto-fill productName & description ───────
        if audio is not None:
            suffix = os.path.splitext(audio.filename or "")[1] or ".wav"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(await audio.read())
                audio_path = tmp.name
            try:
                from app.services.voice_service import transcribe_audio
                stt = transcribe_audio(audio_path)
                transcript = stt.get("text", "").strip()
            except Exception:
                transcript = ""

        product_name = override_product_name or transcript or f"{craft} {product_type}".strip()
        description = transcript if transcript else visual_description

        # ── Step 3: Structured ai_data (fully from AI) ───────────────────
        ai_data = {
            "productName": product_name,
            "craft": craft,
            "material": material,
            "technique": technique,
            "description": description,
        }

        # ── Step 4: artisan_data (artisan provides these) ─────────────────
        artisan_data = {
            "state": state,
            "region": district,
            "district": district,
            "size_length_cm": size_length_cm,
            "size_width_cm": size_width_cm,
            "size_height_cm": size_height_cm,
            "weight_kg": weight_kg,
            "labor_days": labor_days,
            "artisan_skill_level": artisan_skill_level,
            "production_quantity": production_quantity,
            "market_channel": market_channel,
        }

        # ── Step 5: Auto-derive derived_data ─────────────────────────────
        complexity = CRAFT_COMPLEXITY.get(craft.lower().strip(), 6.0)
        auto_labor_cost = round(labor_days * 350.0, 2)
        auto_overhead = round(material_cost_inr * 0.25, 2)
        auto_demand = round(min(10.0, complexity * 0.9 + 1.0), 2)

        derived_data = {
            "product_type": product_type,
            "material_cost_inr": material_cost_inr,
            "labor_hours": labor_days * 8.0,
            "complexity_score": complexity,
            "labor_cost_inr": auto_labor_cost,
            "overhead_cost_inr": auto_overhead,
            "market_demand_score": auto_demand,
            "seasonality_score": 5.0,
        }

        # ── Step 6: CatBoost price prediction ────────────────────────────
        features = extract_features(ai_data=ai_data, artisan_data=artisan_data, derived_data=derived_data)
        price = predict(features)

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    finally:
        for path in [image_path, audio_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    return PricePredictResponse(
        success=True,
        predicted_price_inr=round(price, 2),
        features_used={
            **features,
            "_pipeline_summary": {
                "image_uploaded": image is not None,
                "audio_uploaded": audio is not None,
                "voice_transcript": transcript or "(no audio uploaded)",
                "vision_detected_craft": vision_result.get("craft"),
                "vision_detected_material": vision_result.get("material"),
                "vision_detected_product_type": vision_result.get("product_type"),
                "vision_confidence": vision_result.get("confidence"),
                "auto_complexity_score": complexity,
                "auto_labor_cost_inr": auto_labor_cost,
                "auto_overhead_cost_inr": auto_overhead,
                "auto_market_demand_score": auto_demand,
            },
        },
    )
