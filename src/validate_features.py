import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "model_dataset.csv"
)

df = pd.read_csv(DATA_PATH)

print("Shape:", df.shape)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())

print("\nRecord ID unique:", df["record_id"].is_unique)

print("\nTarget stats:")
print(df["actual_selling_price"].describe())

print("\nLabor hours stats:")
print(df["labor_hours"].describe())

print("\nDirect cost stats:")
print(df["direct_cost"].describe())

print("\nMarket reference stats:")
print(df["market_reference_price"].describe())

print("\nComparable count stats:")
print(df["market_comparable_count"].describe())

# Safety checks

assert len(df) == 5000

assert df.isnull().sum().sum() == 0

assert df.duplicated().sum() == 0

assert df["record_id"].is_unique

assert (df["labor_hours"] > 0).all()

assert (df["raw_material_cost"] >= 0).all()

assert (df["packaging_cost"] >= 0).all()

assert (df["transport_cost"] >= 0).all()

assert (df["direct_cost"] >= 0).all()

assert (df["actual_selling_price"] > 0).all()

assert (df["market_reference_price"] > 0).all()

assert (df["market_comparable_count"] > 0).all()

print("\nFINAL FEATURE VALIDATION PASSED")