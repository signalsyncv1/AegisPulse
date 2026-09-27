import pandas as pd
from pathlib import Path

from analyze_report import analyze_report


BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "data" / "dataset.csv"


df = pd.read_csv(DATASET_PATH)


print("=" * 70)
print("REPORTS REQUIRING REVIEW")
print("=" * 70)


for _, row in df.iterrows():

    report_id = row["report_id"]

    text = row["text"]

    result = analyze_report(text)


    if result["final_result"] == "Needs Review":

        print()
        print("Report ID :", report_id)

        print()
        print("Report:")
        print(text)

        print()

        print(
            "Activity :",
            result["activity"]
        )

        print(
            "Hazard   :",
            result["hazard"]
        )

        print(
            "Barrier  :",
            result["barrier"]
        )

        print(
            "Context  :",
            result["context"]
        )

        print()

        print("-" * 70)


print()
print("Review inspection completed.")