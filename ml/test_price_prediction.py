"""
test_price_prediction.py
========================
End-to-end smoke test for the price prediction pipeline.

Runs WITHOUT the FastAPI server – it calls `feature_extractor` and
`price_predictor` directly, so the model must already be trained and saved.

Usage (from project root, venv active):
    python ml/test_price_prediction.py
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ml.feature_extractor import extract_features
from ml.price_predictor import predict

# ---------------------------------------------------------------------------
# Sample inputs (mirrors the Blue Pottery Vase from test_production_features)
# ---------------------------------------------------------------------------
AI_DATA = {
    "productName": "Blue Pottery Vase",
    "craft": "Blue Pottery",
    "material": "Ceramic",
    "technique": "Hand-painted",
    "description": "Handcrafted decorative vase",
}

ARTISAN_DATA = {
    "state": "Rajasthan",
    "region": "Jaipur",
    "district": "Jaipur",
    "size_length_cm": 20,
    "size_width_cm": 20,
    "size_height_cm": 30,
    "weight_kg": 1.8,
    "labor_days": 3,
    "artisan_skill_level": "Skilled",
    "production_quantity": 10,
    "market_channel": "Artisan Direct",
}

DERIVED_DATA = {
    "product_type": "Vase",
    "labor_hours": 24,
    "complexity_score": 6.5,
    "material_cost_inr": 500,
    "labor_cost_inr": 900,
    "overhead_cost_inr": 200,
    "market_demand_score": 7.2,
    "seasonality_score": 5.0,
}


def run_test():
    print("=" * 55)
    print("  KalaConnect-AI  -  Price Prediction E2E Test")
    print("=" * 55)

    print("\n[1] Extracting features ...")
    features = extract_features(AI_DATA, ARTISAN_DATA, DERIVED_DATA)
    for k, v in features.items():
        print(f"    {k:<25} = {v}")

    print(f"\n    Total features : {len(features)}")

    print("\n[2] Running model inference ...")
    price = predict(features)

    print(f"\n{'=' * 55}")
    print(f"  Predicted Price : INR {price:,.2f}")
    print(f"{'=' * 55}\n")

    assert isinstance(price, float), "Expected a float price"
    assert price > 0, "Price must be positive"
    print("[OK] All assertions passed - pipeline is working correctly.\n")


if __name__ == "__main__":
    run_test()
