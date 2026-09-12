import pandas as pd

DATASET_PATH = "data/processed/indian_handicraft_price_dataset.csv"


df = pd.read_csv(DATASET_PATH)

print("\n========== DATASET SHAPE ==========")
print(df.shape)

print("\n========== COLUMNS ==========")
for column in df.columns:
    print(column)

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== FIRST 5 ROWS ==========")
print(df.head())

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== DUPLICATES ==========")
print(df.duplicated().sum())

if "price_inr" in df.columns:
    print("\n========== PRICE STATISTICS ==========")
    print(df["price_inr"].describe())

print("\n========== UNIQUE VALUES ==========")

for column in df.select_dtypes(include="object").columns:
    print(f"\n{column}:")
    print(df[column].nunique())
    print(df[column].dropna().unique()[:20])