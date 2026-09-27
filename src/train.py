import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# -----------------------------------
# 1. Find project folder
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------
# 2. Paths
# -----------------------------------

DATASET_PATH = BASE_DIR / "data" / "dataset.csv"
MODEL_PATH = BASE_DIR / "models" / "sif_classifier.pkl"

# -----------------------------------
# 3. Load dataset
# -----------------------------------

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully!")
print("Total reports:", len(df))
print()

# -----------------------------------
# 4. Input and target
# -----------------------------------

X = df["text"]
y = df["sif_label"]

# -----------------------------------
# 5. Train-test split
# -----------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training reports:", len(X_train))
print("Testing reports:", len(X_test))
print()

# -----------------------------------
# 6. Create ML pipeline
# -----------------------------------

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2)
        )
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        )
    )
])

# -----------------------------------
# 7. Train model
# -----------------------------------

print("Training SIF classifier...")
print()

model.fit(X_train, y_train)

print("Model training completed!")
print()

# -----------------------------------
# 8. Save model
# -----------------------------------

joblib.dump(model, MODEL_PATH)

print("Model saved successfully!")
print()
print("Model location:")
print(MODEL_PATH)