"""
price_predictor.py
==================
Loads the trained CatBoost model once at import time and exposes a
`predict(features: dict) -> float` helper used by the FastAPI price endpoint.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path when this module is imported directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
from catboost import CatBoostRegressor

from ml.feature_schema import CATEGORICAL_FEATURES, FEATURE_COLUMNS

# ---------------------------------------------------------------------------
# Default model path (relative to project root)
# ---------------------------------------------------------------------------
_DEFAULT_MODEL_PATH = project_root / "models" / "catboost_handicraft_model.cbm"


def load_model(model_path: str | Path = _DEFAULT_MODEL_PATH) -> CatBoostRegressor:
    """Load a CatBoost model from disk."""
    model = CatBoostRegressor()
    model.load_model(str(model_path))
    return model


# Singleton – loaded once when the module is first imported
_model: CatBoostRegressor | None = None


def _get_model() -> CatBoostRegressor:
    global _model
    if _model is None:
        _model = load_model()
    return _model


def predict(features: dict) -> float:
    """Return a price prediction (INR) given a feature dictionary.

    Parameters
    ----------
    features:
        Dict whose keys match ``FEATURE_COLUMNS`` (categorical + numerical).
        Missing keys are filled with sensible defaults (empty string for
        categoricals, 0.0 for numericals).

    Returns
    -------
    float
        Predicted price in INR.
    """
    model = _get_model()

    # Build a single-row DataFrame in the exact column order expected by the model
    row: dict = {}
    for col in FEATURE_COLUMNS:
        value = features.get(col)
        if value is None:
            value = "" if col in CATEGORICAL_FEATURES else 0.0
        row[col] = value

    df = pd.DataFrame([row])

    # Ensure categorical columns are strings (CatBoost requirement)
    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].astype(str)

    prediction = model.predict(df)[0]
    return float(prediction)
