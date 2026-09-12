import pandas as pd
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

market_path = BASE_DIR / "data" / "raw" / "market_data.csv"
production_path = BASE_DIR / "data" / "raw" / "artisan_data.csv"

output_path = BASE_DIR / "data" / "processed" / "merged_dataset.csv"


# Load datasets
market = pd.read_csv(market_path)
production = pd.read_csv(production_path)

# print("Market shape:", market.shape)
# print("Production shape:", production.shape)


# Check record_id exists
assert "record_id" in market.columns
assert "record_id" in production.columns


# Check uniqueness before merging
assert market["record_id"].is_unique
assert production["record_id"].is_unique


# Merge
merged = market.merge(
    production,
    on="record_id",
    how="inner",
    suffixes=("_market", "_production")
)


# print("Merged shape:", merged.shape)


# Confirm no rows were lost
assert len(merged) == 5000


# Save
output_path.parent.mkdir(parents=True, exist_ok=True)

merged.to_csv(
    output_path,
    index=False
)

# print("Merged dataset saved to:")
# print(output_path)


columns_to_check = [
    "craft",
    "material",
    "technique",
    "region",
    "size"
]

for col in columns_to_check:
    same = (
        merged[f"{col}_market"]
        ==
        merged[f"{col}_production"]
    ).all()

    # print(col, same)

# Keep one clean copy of the matching columns
merged["craft"] = merged["craft_market"]
merged["material"] = merged["material_market"]
merged["technique"] = merged["technique_market"]
merged["region"] = merged["region_market"]
merged["size"] = merged["size_market"]

# Remove duplicated market/production versions
columns_to_drop = [
    "craft_market",
    "craft_production",
    "material_market",
    "material_production",
    "technique_market",
    "technique_production",
    "region_market",
    "region_production",
    "size_market",
    "size_production"
]

merged = merged.drop(columns=columns_to_drop)

price_match = (
    merged["price"]
    ==
    merged["actual_selling_price"]
).all()

# print("Price match:", price_match)

assert price_match

merged = merged.drop(columns=["price"])

merged["direct_cost"] = (
    merged["raw_material_cost"]
    + merged["packaging_cost"]
    + merged["transport_cost"]
)

feature_output = (
    BASE_DIR
    / "data"
    / "processed"
    / "feature_base.csv"
)

merged.to_csv(
    feature_output,
    index=False
)

print("Feature base saved:")
print(feature_output)

print("Final shape:", merged.shape)
print("Missing values:", merged.isnull().sum().sum())
print("Duplicates:", merged.duplicated().sum())