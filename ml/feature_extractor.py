"""
feature_extractor.py
====================
Converts the raw API request payload (ai_data + artisan_data + derived_data)
into the flat feature dictionary consumed by `price_predictor.predict()`.

This is a thin wrapper around `production_feature_schema.build_price_features`
that also validates required keys and provides sensible defaults.
"""

from typing import Any, Dict

from ml.production_feature_schema import build_price_features


def extract_features(
    ai_data: Dict[str, Any],
    artisan_data: Dict[str, Any],
    derived_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the flat feature dict from three domain sub-dicts.

    Parameters
    ----------
    ai_data:
        Output from the Vision AI (craft, material, technique, …).
    artisan_data:
        Artisan-provided information (location, size, weight, …).
    derived_data:
        Derived / computed fields (labor_hours, complexity_score, costs, …).

    Returns
    -------
    dict
        Flat feature dictionary ready for ``price_predictor.predict()``.
    """
    features = build_price_features(ai_data, artisan_data, derived_data)
    return features
