import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from backend_adapter import (
    analyze_batch_reports,
    analyze_single_report,
    get_activity_density,
    get_dashboard_summary,
    get_life_saving_rule_summary,
    get_precursor_patterns,
    get_review_queue,
    get_reports,
    get_site_activity_hotspots,
    get_site_density,
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


print("=" * 72)
print("BACKEND ADAPTER SMOKE TEST")
print("=" * 72)

reports = get_reports()
require(len(reports) > 0, "No analyzed reports were loaded.")
print(f"[PASS] Loaded reports: {len(reports)}")

summary = get_dashboard_summary()
require(summary["total_reports"] == len(reports), "Dashboard total does not match reports.")
print("[PASS] Dashboard summary")
print(summary)

site_density = get_site_density()
require(
    {"site", "total_reports", "sif_reports", "sif_density"}.issubset(site_density.columns),
    "Site density schema is incomplete.",
)
print(f"[PASS] Site density rows: {len(site_density)}")
print(site_density.head(5).to_string(index=False))

activity_density = get_activity_density()
require(
    {"activity", "total_reports", "sif_reports", "sif_density"}.issubset(activity_density.columns),
    "Activity density schema is incomplete.",
)
print(f"[PASS] Activity density rows: {len(activity_density)}")
print(activity_density.head(5).to_string(index=False))

lsr = get_life_saving_rule_summary()
require(len(lsr) >= 9, "Life-Saving Rule summary is incomplete.")
print("[PASS] Life-Saving Rule summary")

patterns = get_precursor_patterns()
print(f"[PASS] Precursor pattern rows: {len(patterns)}")
if not patterns.empty:
    print(patterns.head(8).to_string(index=False))

review = get_review_queue()
print(f"[PASS] Review queue rows: {len(review)}")

hotspots = get_site_activity_hotspots()
print(f"[PASS] Site/activity hotspot rows: {len(hotspots)}")

single = analyze_single_report(
    "Electrical isolation was not completed before maintenance started.",
    site="Demo Site",
    report_id="DEMO-1",
)
require(single["ai_result"] == "SIF Potential", "Dangerous single-report case failed.")
print("[PASS] Single report analysis")

batch = pd.DataFrame(
    [
        {
            "report_id": "B001",
            "site": "Demo Site A",
            "text": "Electrical isolation was not completed before maintenance started.",
        },
        {
            "report_id": "B002",
            "site": "Demo Site A",
            "text": "Electrical isolation was completed and verified before maintenance.",
        },
        {
            "report_id": "B003",
            "site": "Demo Site B",
            "text": "An unsafe condition was observed near equipment during maintenance.",
        },
    ]
)

batch_result = analyze_batch_reports(batch)
require(len(batch_result) == 3, "Batch analysis did not return all three reports.")

expected = ["SIF Potential", "Non-SIF Potential", "Needs Review"]
actual = batch_result["ai_result"].tolist()
require(actual == expected, f"Unexpected batch decisions: {actual}")

print("[PASS] Batch analysis")
print(batch_result[["report_id", "site", "ai_result", "hazard", "barrier"]].to_string(index=False))

print("=" * 72)
print("ALL BACKEND ADAPTER TESTS PASSED")
print("=" * 72)
