from pathlib import Path
import sys
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    fbeta_score,
    confusion_matrix,
    classification_report
)

# ------------------------------------------------------------
# Add src folder to Python path
# ------------------------------------------------------------

SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

from analyze_report import analyze_report


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

BASE_DIR = SRC_DIR.parent
DATASET_PATH = BASE_DIR / "data" / "dataset.csv"


# ------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully!")
print(f"Total reports: {len(df)}")


# ------------------------------------------------------------
# Convert labels
# ------------------------------------------------------------
#
# Dataset:
# 1 = SIF Potential
# 0 = Non-SIF Potential
#
# Important:
# Needs Review is handled by the hybrid system.
#
# ------------------------------------------------------------

actual_labels = []
predicted_labels = []

needs_review_count = 0


# ------------------------------------------------------------
# Evaluate every report
# ------------------------------------------------------------

print("\n========== HYBRID SYSTEM EVALUATION ==========")

for _, row in df.iterrows():

    report_id = row["report_id"]
    text = row["text"]
    actual = int(row["sif_label"])

    result = analyze_report(text)

    final_result = result["final_result"]

    # --------------------------------------------------------
    # Convert final hybrid result to binary label
    # --------------------------------------------------------
    #
    # SIF Potential     -> 1
    # Non-SIF Potential -> 0
    # Needs Review      -> handled separately
    #
    # --------------------------------------------------------

    if final_result == "SIF Potential":

        predicted = 1

    elif final_result == "Non-SIF Potential":

        predicted = 0

    else:

        # Needs Review
        needs_review_count += 1

        # For binary metrics we don't silently call it SIF
        # or Non-SIF. It is excluded from the binary metric
        # calculation below.

        predicted = None


    # --------------------------------------------------------
    # Store only classified reports for binary metrics
    # --------------------------------------------------------

    if predicted is not None:

        actual_labels.append(actual)
        predicted_labels.append(predicted)


# ------------------------------------------------------------
# Metrics
# ------------------------------------------------------------

accuracy = accuracy_score(
    actual_labels,
    predicted_labels
)

precision = precision_score(
    actual_labels,
    predicted_labels,
    zero_division=0
)

recall = recall_score(
    actual_labels,
    predicted_labels,
    zero_division=0
)

f1 = f1_score(
    actual_labels,
    predicted_labels,
    zero_division=0
)

f2 = fbeta_score(
    actual_labels,
    predicted_labels,
    beta=2,
    zero_division=0
)


# ------------------------------------------------------------
# Print metrics
# ------------------------------------------------------------

print("\n========== HYBRID PERFORMANCE ==========")

print(f"Classified Reports : {len(actual_labels)}")
print(f"Needs Review       : {needs_review_count}")

print(f"\nAccuracy  : {accuracy:.2f}")
print(f"Precision : {precision:.2f}")
print(f"Recall    : {recall:.2f}")
print(f"F1 Score  : {f1:.2f}")
print(f"F2 Score  : {f2:.2f}")


# ------------------------------------------------------------
# Classification report
# ------------------------------------------------------------

print("\n========== CLASSIFICATION REPORT ==========")

print(
    classification_report(
        actual_labels,
        predicted_labels,
        target_names=[
            "Non-SIF Potential",
            "SIF Potential"
        ],
        zero_division=0
    )
)


# ------------------------------------------------------------
# Confusion Matrix
# ------------------------------------------------------------

cm = confusion_matrix(
    actual_labels,
    predicted_labels
)

print("========== CONFUSION MATRIX ==========")

print(cm)


# ------------------------------------------------------------
# Detailed missed-case analysis
# ------------------------------------------------------------

print("\n========== POTENTIAL FALSE NEGATIVES ==========")

false_negative_count = 0

for _, row in df.iterrows():

    actual = int(row["sif_label"])

    if actual != 1:
        continue

    result = analyze_report(row["text"])

    if result["final_result"] != "SIF Potential":

        false_negative_count += 1

        print("\n----------------------------------------")

        print(f"Report ID : {row['report_id']}")

        print(f"Report    : {row['text']}")

        print(
            f"Final Result : "
            f"{result['final_result']}"
        )

        print(
            f"ML Prediction : "
            f"{result['ml_prediction']}"
        )

        print(
            f"Context : "
            f"{result['context']}"
        )

        print(
            f"Hazard : "
            f"{result['hazard']}"
        )

        print(
            f"Barrier : "
            f"{result['barrier']}"
        )

        print(
            f"LSR : "
            f"{result['lsr_rules']}"
        )

        print(
            f"Evidence : "
            f"{result['primary_evidence']}"
        )


print("\n----------------------------------------")

print(
    f"Potential false negatives: "
    f"{false_negative_count}"
)


# ------------------------------------------------------------
# Needs Review cases
# ------------------------------------------------------------

print("\n========== NEEDS REVIEW CASES ==========")

review_count = 0

for _, row in df.iterrows():

    result = analyze_report(row["text"])

    if result["final_result"] == "Needs Review":

        review_count += 1

        print("\n----------------------------------------")

        print(
            f"Report ID : "
            f"{row['report_id']}"
        )

        print(
            f"Report    : "
            f"{row['text']}"
        )

        print(
            f"Context   : "
            f"{result['context']}"
        )

        print(
            f"Reason    : "
            f"{result.get('contradiction_reason')}"
        )


print("\n----------------------------------------")

print(
    f"Total Needs Review: "
    f"{review_count}"
)


print("\n========== EVALUATION COMPLETE ==========")