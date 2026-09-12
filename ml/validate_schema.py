import pandas as pd
import sys
from pathlib import Path
# Ensure project root is in sys.path for package imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import feature schema from the ml package
from ml.feature_schema import (
    TARGET_COLUMN,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    FEATURE_COLUMNS,
)

DATASET_PATH = "data/processed/indian_handicraft_price_dataset.csv"


def validate_schema(df: pd.DataFrame):
    required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    print("[OK] All required columns exist")

    # Check categorical columns
    for column in CATEGORICAL_FEATURES:
        if not pd.api.types.is_object_dtype(df[column]):
            print(f"WARNING: {column} is not object/string type: {df[column].dtype}")

    # Check numerical columns
    for column in NUMERICAL_FEATURES:
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(f"{column} must be numeric, got {df[column].dtype}")

    # Check target column dtype
    if not pd.api.types.is_numeric_dtype(df[TARGET_COLUMN]):
        raise ValueError(f"{TARGET_COLUMN} must be numeric")

    # Missing values check
    missing_vals = df[required_columns].isnull().sum()
    if missing_vals.sum() > 0:
        print("\nMissing values:")
        print(missing_vals[missing_vals > 0])
        raise ValueError("Dataset contains missing values")

    # Target positivity check
    if (df[TARGET_COLUMN] <= 0).any():
        raise ValueError("price_inr contains zero/negative values")

    print("[OK] No missing values")
    print("[OK] Target values are positive")
    print("[OK] Schema validation successful")
    print("\nFeatures:")
    for f in FEATURE_COLUMNS:
        print(f"  - {f}")
    print(f"\nTarget: {TARGET_COLUMN}")


if __name__ == "__main__":
    df = pd.read_csv(DATASET_PATH)
    print(f"Dataset shape: {df.shape}\n")
    validate_schema(df)
