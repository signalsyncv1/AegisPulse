import pandas as pd
from pathlib import Path

from analyze_report import analyze_report


# ==========================================
# PATH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "data" / "dataset.csv"


# ==========================================
# LOAD DATASET
# ==========================================

df = pd.read_csv(DATASET_PATH)


print("=" * 70)
print("REPORTS WITH UNKNOWN ACTIVITY")
print("=" * 70)


# ==========================================
# ANALYZE REPORTS
# ==========================================

for _, row in df.iterrows():

    report_id = row["report_id"]

    text = row["text"]

    result = analyze_report(text)


    # --------------------------------------
    # Show SIF reports with Unknown activity
    # --------------------------------------

    if (
        result["final_result"] == "SIF Potential"
        and result["activity"] == "Unknown"
    ):

        print()

        print("Report ID:")
        print(report_id)

        print()

        print("Report:")
        print(text)

        print()

        print(
            "SIF Result:",
            result["final_result"]
        )

        print(
            "Hazard:",
            result["hazard"]
        )

        print(
            "Barrier:",
            result["barrier"]
        )

        print(
            "LSR:",
            result["lsr_rules"]
        )

        print()

        print("-" * 70)


print()
print("Inspection completed.")