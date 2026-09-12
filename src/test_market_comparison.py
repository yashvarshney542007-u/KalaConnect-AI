import pandas as pd
from pathlib import Path

from market_comparison import compare_with_market


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR
    / "reports"
    / "test_predictions.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "reports"
    / "market_comparison_results.csv"
)


df = pd.read_csv(INPUT_PATH)

print("Test products:", len(df))


required_columns = [
    "record_id",
    "craft",
    "material",
    "technique",
    "size",
    "region",
    "actual_selling_price",
    "predicted_price"
]

missing = [
    col
    for col in required_columns
    if col not in df.columns
]

if missing:
    raise ValueError(
        f"Missing columns in test_predictions.csv: {missing}"
    )


results = []


for _, row in df.iterrows():

    comparison = compare_with_market(

        craft=row["craft"],

        material=row["material"],

        technique=row["technique"],

        size=row["size"],

        region=row["region"],

        predicted_price=row["predicted_price"]
    )


    comparison["record_id"] = row["record_id"]

    comparison["actual_selling_price"] = (
        row["actual_selling_price"]
    )

    comparison["prediction_error"] = abs(
        row["predicted_price"]
        -
        row["actual_selling_price"]
    )


    results.append(
        comparison
    )


results_df = pd.DataFrame(
    results
)


results_df.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\n==============================")
print("MARKET COMPARISON VALIDATION")
print("==============================")


print(
    "Total products:",
    len(results_df)
)


print(
    "Successful comparisons:",
    results_df["success"].sum()
)


print(
    "Failed comparisons:",
    (~results_df["success"]).sum()
)


successful = results_df[
    results_df["success"] == True
]


print("\nMarket positions:")

print(
    successful[
        "market_position"
    ].value_counts()
)


print("\nRecommendations:")

print(
    successful[
        "recommendation"
    ].value_counts()
)


print("\nComparison levels:")

print(
    successful[
        "comparison_level"
    ].value_counts()
)


print(
    "\nAverage comparable products:"
)

print(
    successful[
        "comparable_count"
    ].mean()
)


print(
    "\nMedian comparable products:"
)

print(
    successful[
        "comparable_count"
    ].median()
)


print("\n==============================")
print("PHASE 7 VALIDATION COMPLETE")
print("==============================")


print("\nSaved:")

print(
    OUTPUT_PATH
)