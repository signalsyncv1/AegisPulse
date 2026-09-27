import pandas as pd
from pathlib import Path

# Find the main project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset location
DATASET_PATH = BASE_DIR / "data" / "dataset.csv"

print("Looking for dataset at:")
print(DATASET_PATH)
print()

# Load dataset
df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully!")
print()

print("Number of reports:", len(df))
print()

print("Columns:")
print(df.columns.tolist())
print()

print("SIF label distribution:")
print(df["sif_label"].value_counts())
print()

print("First 5 reports:")
print(df.head())