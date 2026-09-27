import joblib
from pathlib import Path

# -----------------------------------
# 1. Find project folder
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------
# 2. Model path
# -----------------------------------

MODEL_PATH = BASE_DIR / "models" / "sif_classifier.pkl"

# -----------------------------------
# 3. Load trained model
# -----------------------------------

model = joblib.load(MODEL_PATH)

print("======================================")
print("       SIF PRECURSOR DETECTOR")
print("======================================")
print()

# -----------------------------------
# 4. Get report from user
# -----------------------------------

report = input("Enter safety report:\n")

print()
print("Analyzing report...")
print()

# -----------------------------------
# 5. Predict
# -----------------------------------

prediction = model.predict([report])[0]

# -----------------------------------
# 6. Get model score
# -----------------------------------

probabilities = model.predict_proba([report])[0]

# Probability/score corresponding to class 1
sif_score = probabilities[1]

# -----------------------------------
# 7. Display result
# -----------------------------------

if prediction == 1:
    result = "SIF Potential"
else:
    result = "Non-SIF Potential"

print("======================================")
print("RESULT")
print("======================================")

print("SIF Classification :", result)
print("Model Score        :", round(sif_score, 2))

print()
print("Note: Model score is not a probability")
print("of injury or fatality.")