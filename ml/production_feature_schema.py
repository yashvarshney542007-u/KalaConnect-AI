from typing import Dict, Any

def build_price_features(
    ai_data: Dict[str, Any],
    artisan_data: Dict[str, Any],
    derived_data: Dict[str, Any],
) -> Dict[str, Any]:

    features = {
        # Categorical features
        "craft": ai_data.get("craft"),
        "product_type": derived_data.get("product_type"),
        "material": ai_data.get("material"),
        "technique": ai_data.get("technique"),

        "state": artisan_data.get("state"),
        "region": artisan_data.get("region"),
        "district": artisan_data.get("district"),

        "artisan_skill_level": artisan_data.get(
            "artisan_skill_level"
        ),

        "market_channel": artisan_data.get(
            "market_channel"
        ),

        # Numerical features
        "size_length_cm": artisan_data.get("size_length_cm"),
        "size_width_cm": artisan_data.get("size_width_cm"),
        "size_height_cm": artisan_data.get("size_height_cm"),

        "weight_kg": artisan_data.get("weight_kg"),

        "labor_days": artisan_data.get("labor_days"),
        "labor_hours": derived_data.get("labor_hours"),

        "complexity_score": derived_data.get(
            "complexity_score"
        ),

        "material_cost_inr": derived_data.get(
            "material_cost_inr"
        ),

        "labor_cost_inr": derived_data.get(
            "labor_cost_inr"
        ),

        "overhead_cost_inr": derived_data.get(
            "overhead_cost_inr"
        ),

        "market_demand_score": derived_data.get(
            "market_demand_score"
        ),

        "seasonality_score": derived_data.get(
            "seasonality_score"
        ),

        "production_quantity": artisan_data.get(
            "production_quantity"
        ),
    }

    return features
