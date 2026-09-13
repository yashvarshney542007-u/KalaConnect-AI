from pathlib import Path

import pandas as pd
from catboost import CatBoostRegressor

from src.feature_engineering import get_market_reference_features


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# ML FILE PATHS
# ============================================================

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "catboost_price_model_final.cbm"
)

REFERENCE_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "feature_base.csv"
)


# ============================================================
# EXACT FEATURE ORDER USED DURING MODEL TRAINING
# ============================================================

FEATURES = [
    "product",
    "category",
    "subcategory",
    "craft",
    "material",
    "technique",
    "state",
    "region",
    "size",
    "complexity",
    "customization",
    "labor_hours",
    "raw_material_cost",
    "packaging_cost",
    "transport_cost",
    "direct_cost",
    "market_reference_price",
    "market_price_min",
    "market_price_max",
    "market_comparable_count",
]


# ============================================================
# PRICING SERVICE
# ============================================================

class PricingService:
    """
    Handles KalaConnect ML price prediction.
    """

    def __init__(self):
        # Load trained CatBoost model
        self.model = CatBoostRegressor()
        self.model.load_model(str(MODEL_PATH))

        # Load reference market data
        self.market_df = pd.read_csv(
            REFERENCE_PATH
        ).rename(
            columns={
                "actual_selling_price": "price"
            }
        )

    def predict(self, input_data):
        """
        Generate a price prediction.

        input_data contains the 16 user-supplied
        features.

        The service generates the 4 market-derived
        features automatically.
        """

        # ----------------------------------------------------
        # 1. Generate market-derived features
        # ----------------------------------------------------

        market_features = get_market_reference_features(
            input_data,
            self.market_df,
        )

        # ----------------------------------------------------
        # 2. Combine user input + market features
        # ----------------------------------------------------

        model_data = {
            **input_data,
            **market_features,
        }

        # ----------------------------------------------------
        # 3. Create DataFrame using EXACT training order
        # ----------------------------------------------------

        model_input = pd.DataFrame(
            [model_data],
            columns=FEATURES,
        )

        # ----------------------------------------------------
        # 4. Generate CatBoost prediction
        # ----------------------------------------------------

        predicted_price = float(
            self.model.predict(model_input)[0]
        )

        # ----------------------------------------------------
        # 5. Return prediction + market information
        # ----------------------------------------------------

        return {
            "predicted_price": round(
                predicted_price,
                2,
            ),
            "market_features": market_features,
        }


# ============================================================
# SINGLE REUSABLE SERVICE INSTANCE
# ============================================================

pricing_service = PricingService()


# ============================================================
# PUBLIC FUNCTION USED BY DJANGO
# ============================================================

def predict(input_data):
    """
    Public interface used by Django.

    Django can simply call:

        pricing_service.predict(data)

    because config.views imports the module.
    """

    return pricing_service.predict(input_data)