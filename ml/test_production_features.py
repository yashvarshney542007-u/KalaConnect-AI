from production_feature_schema import build_price_features


ai_data = {
    "productName": "Blue Pottery Vase",
    "craft": "Blue Pottery",
    "material": "Ceramic",
    "technique": "Hand-painted",
    "description": "Handcrafted decorative vase"
}


artisan_data = {
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
    "market_channel": "Artisan Direct"
}


derived_data = {
    "product_type": "Vase",
    "labor_hours": 24,
    "complexity_score": 6.5,
    "material_cost_inr": 500,
    "labor_cost_inr": 900,
    "overhead_cost_inr": 200,
    "market_demand_score": 7.2,
    "seasonality_score": 5.0
}

features = build_price_features(ai_data, artisan_data, derived_data)

print("========== PRODUCTION FEATURES ==========")
for key, value in features.items():
    print(f"{key}: {value}")

print("\nTotal features:", len(features))
