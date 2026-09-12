from typing import Dict, Any


def derive_features(
    ai_data: Dict[str, Any],
    artisan_data: Dict[str, Any]
) -> Dict[str, Any]:

    labor_days = artisan_data.get("labor_days", 0)

    # Temporary calculation:
    # 1 working day = 8 working hours
    labor_hours = labor_days * 8

    # These will be replaced with proper
    # reference/data-driven logic in the next step.
    complexity_score = None
    material_cost_inr = None
    labor_cost_inr = None
    overhead_cost_inr = None
    market_demand_score = None
    seasonality_score = None

    return {
        "product_type": None,
        "labor_hours": labor_hours,
        "complexity_score": complexity_score,
        "material_cost_inr": material_cost_inr,
        "labor_cost_inr": labor_cost_inr,
        "overhead_cost_inr": overhead_cost_inr,
        "market_demand_score": market_demand_score,
        "seasonality_score": seasonality_score,
    }