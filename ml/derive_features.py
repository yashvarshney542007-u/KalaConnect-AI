"""
ml/derive_features.py
=====================
Derives computed features (costs, scores, product type) from raw
ai_data + artisan_data inputs.

These derived values feed directly into `ml/production_feature_schema.py`
as `derived_data`.
"""

from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------

_COMPLEXITY_BY_TECHNIQUE: Dict[str, float] = {
    "hand-painted":       7.0,
    "hand painted":       7.0,
    "hand embroidered":   8.0,
    "hand woven":         7.5,
    "block print":        5.0,
    "carved":             8.5,
    "filigree":           9.0,
    "lacquer":            6.0,
    "dhokra":             8.0,
    "crochet":            6.5,
    "zardozi":            9.5,
    "machine made":       2.0,
}

_MATERIAL_COST_PER_KG: Dict[str, float] = {
    "ceramic":       300.0,
    "brass":         600.0,
    "silver":       6000.0,
    "cotton":        200.0,
    "silk":         1200.0,
    "wood":          250.0,
    "bamboo":        120.0,
    "marble":        800.0,
    "jute":          100.0,
    "leather":       500.0,
    "terracotta":    180.0,
    "stone":         400.0,
}

_PRODUCT_TYPE_MAP: Dict[str, str] = {
    "vase":          "Vase",
    "pot":           "Pot",
    "bowl":          "Bowl",
    "plate":         "Plate",
    "idol":          "Idol",
    "statue":        "Statue",
    "wall hanging":  "Wall Hanging",
    "painting":      "Painting",
    "saree":         "Saree",
    "dupatta":       "Dupatta",
    "kurta":         "Kurta",
    "bag":           "Bag",
    "jewellery":     "Jewellery",
    "jewelry":       "Jewellery",
    "necklace":      "Necklace",
    "bracelet":      "Bracelet",
    "earring":       "Earring",
    "box":           "Box",
    "tray":          "Tray",
    "lamp":          "Lamp",
    "cushion":       "Cushion",
    "rug":           "Rug",
    "carpet":        "Carpet",
    "basket":        "Basket",
    "toy":           "Toy",
    "doll":          "Doll",
}

_LABOUR_RATE_INR_PER_HOUR: float = 50.0   # baseline artisan wage
_OVERHEAD_RATE: float = 0.15               # 15 % of (material + labour)
_MARKET_DEMAND_DEFAULT: float = 5.0
_SEASONALITY_DEFAULT: float = 5.0


def _infer_product_type(product_name: Optional[str]) -> Optional[str]:
    """Best-effort product type from the product name string."""
    if not product_name:
        return None
    lower = product_name.lower()
    for keyword, ptype in _PRODUCT_TYPE_MAP.items():
        if keyword in lower:
            return ptype
    return None


def _infer_complexity(technique: Optional[str]) -> float:
    """Map technique string to a 1–10 complexity score."""
    if not technique:
        return 5.0
    return _COMPLEXITY_BY_TECHNIQUE.get(technique.lower().strip(), 5.0)


def _estimate_material_cost(
    material: Optional[str],
    weight_kg: Optional[float],
) -> float:
    """Estimate material cost in INR from material name and weight."""
    if not material or weight_kg is None or weight_kg <= 0:
        return 0.0
    rate = _MATERIAL_COST_PER_KG.get(material.lower().strip(), 300.0)
    return round(rate * weight_kg, 2)


def derive_features(
    ai_data: Dict[str, Any],
    artisan_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Derive computed fields from Vision-AI output + artisan input.

    Parameters
    ----------
    ai_data:
        Dict from Vision AI (keys: craft, material, technique, productName, …).
    artisan_data:
        Dict from artisan (keys: labor_days, weight_kg, market_channel, …).

    Returns
    -------
    dict
        ``derived_data`` dict ready for ``build_price_features()``.
    """
    # ---- labour -----------------------------------------------------------
    labor_days: float = float(artisan_data.get("labor_days") or 0)
    labor_hours: float = labor_days * 8           # 1 day = 8 working hours

    # ---- product type -----------------------------------------------------
    product_name: Optional[str] = (
        ai_data.get("productName") or ai_data.get("product_name")
    )
    product_type: Optional[str] = _infer_product_type(product_name)

    # ---- costs ------------------------------------------------------------
    material: Optional[str] = ai_data.get("material")
    weight_kg: Optional[float] = artisan_data.get("weight_kg")

    material_cost_inr: float = _estimate_material_cost(material, weight_kg)
    labor_cost_inr: float = round(labor_hours * _LABOUR_RATE_INR_PER_HOUR, 2)
    overhead_cost_inr: float = round(
        (material_cost_inr + labor_cost_inr) * _OVERHEAD_RATE, 2
    )

    # ---- scores -----------------------------------------------------------
    technique: Optional[str] = ai_data.get("technique")
    complexity_score: float = _infer_complexity(technique)
    market_demand_score: float = _MARKET_DEMAND_DEFAULT
    seasonality_score: float = _SEASONALITY_DEFAULT

    return {
        "product_type":        product_type,
        "labor_hours":         labor_hours,
        "complexity_score":    complexity_score,
        "material_cost_inr":   material_cost_inr,
        "labor_cost_inr":      labor_cost_inr,
        "overhead_cost_inr":   overhead_cost_inr,
        "market_demand_score": market_demand_score,
        "seasonality_score":   seasonality_score,
    }
