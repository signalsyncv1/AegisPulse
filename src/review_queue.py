import datetime
from pathlib import Path
import pandas as pd

from analyze_report import analyze_report

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "data" / "dataset.csv"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)
OUTPUT_PATH = RESULTS_DIR / "review_queue.csv"

OIL_INDIA_SITES = [
    "Duliajan Central Asset",
    "Digboi Refinery Area 3",
    "Moran Gas Gathering Station",
    "Naharkatiya Production Unit",
    "Jorhat Pumping Station",
    "Dibrugarh Terminal",
]


def generate_review_queue():
    """Generate or refresh review_queue.csv from data/dataset.csv."""
    if not DATASET_PATH.exists():
        empty_df = pd.DataFrame(columns=[
            "report_id", "report_text", "site", "ai_result", "model_prediction",
            "model_score", "context", "priority", "activity", "hazard", "hazards",
            "hazard_evidence", "barrier", "barriers", "barrier_evidence",
            "barrier_condition", "life_saving_rules", "evidence",
            "potential_consequence", "recommended_action", "review_reason",
            "review_status", "reviewer_decision", "reviewer_comment",
            "reviewer_name", "reviewed_at"
        ])
        empty_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
        return empty_df

    df = pd.read_csv(DATASET_PATH)
    review_records = []

    for idx, row in df.iterrows():
        report_id = str(row.get("report_id", f"R{idx+1:03d}"))
        report_text = str(row.get("text", ""))
        site = OIL_INDIA_SITES[idx % len(OIL_INDIA_SITES)]

        result = analyze_report(report_text)

        # LSR text
        lsr_rules = result.get("lsr_rules", [])
        lsr_text = "; ".join(lsr_rules) if lsr_rules else "None"

        # Activity text
        activities = result.get("activities", [])
        activity_text = "; ".join(activities) if activities else result.get("activity", "Unknown")

        # Hazards text
        hazards = result.get("hazards", [])
        hazard_names = []
        hazard_evidence_parts = []
        for item in hazards:
            h_name = item.get("hazard", "Unknown")
            if h_name not in hazard_names:
                hazard_names.append(h_name)
            ev = item.get("evidence", [])
            if ev:
                ev_str = ", ".join(ev) if isinstance(ev, list) else str(ev)
                hazard_evidence_parts.append(f"{h_name}: {ev_str}")
        hazard_text = "; ".join(hazard_names) if hazard_names else result.get("hazard", "Unknown")
        hazard_evidence_text = " | ".join(hazard_evidence_parts)

        # Barriers text
        barriers = result.get("barriers", [])
        barrier_names = []
        barrier_evidence_parts = []
        for item in barriers:
            b_name = item.get("barrier", "Unknown")
            if b_name not in barrier_names:
                barrier_names.append(b_name)
            ev = item.get("evidence", [])
            if ev:
                ev_str = ", ".join(ev) if isinstance(ev, list) else str(ev)
                barrier_evidence_parts.append(f"{b_name}: {ev_str}")
        barrier_text = "; ".join(barrier_names) if barrier_names else result.get("barrier", "Unknown")
        barrier_evidence_text = " | ".join(barrier_evidence_parts)

        # Review status & priority
        final_res = result.get("final_result", "Needs Review")
        if final_res == "Needs Review":
            review_status = "Pending Review"
            priority = "High"
        elif final_res == "SIF Potential":
            review_status = "Pending Review"
            priority = "High"
        else:
            review_status = "Not Yet Reviewed"
            priority = "Low"

        review_records.append({
            "report_id": report_id,
            "report_text": report_text,
            "site": site,
            "ai_result": final_res,
            "model_prediction": result.get("ml_prediction", "Non-SIF Potential"),
            "model_score": result.get("model_score", 0.5),
            "context": result.get("context", "Unknown"),
            "priority": priority,
            "activity": activity_text,
            "hazard": result.get("hazard", "Unknown"),
            "hazards": hazard_text,
            "hazard_evidence": hazard_evidence_text,
            "barrier": result.get("barrier", "Unknown"),
            "barriers": barrier_text,
            "barrier_evidence": barrier_evidence_text,
            "barrier_condition": result.get("barrier_condition", "Uncertain / Unspecified"),
            "life_saving_rules": lsr_text,
            "evidence": result.get("primary_evidence", ""),
            "potential_consequence": result.get("potential_consequence", ""),
            "recommended_action": result.get("recommended_action", ""),
            "review_reason": result.get("review_reason", ""),
            "review_status": review_status,
            "reviewer_decision": "",
            "reviewer_comment": "",
            "reviewer_name": "",
            "reviewed_at": ""
        })

    review_df = pd.DataFrame(review_records)
    review_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    return review_df


def load_review_queue():
    """Load review_queue.csv safely, generating it if absent."""
    if not OUTPUT_PATH.exists():
        return generate_review_queue()
    try:
        df = pd.read_csv(OUTPUT_PATH)
        # Ensure critical columns exist
        if "site" not in df.columns:
            df["site"] = [OIL_INDIA_SITES[i % len(OIL_INDIA_SITES)] for i in range(len(df))]
            df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
        text_cols = ["reviewer_decision", "reviewer_comment", "reviewer_name", "review_status", "reviewed_at"]
        for c in text_cols:
            if c in df.columns:
                df[c] = df[c].fillna("").astype(str)
        return df
    except Exception:
        return generate_review_queue()


def update_review_record(report_id, human_label, reviewer_note="", reviewer="HSE Officer", status="Confirmed"):
    """
    Persist reviewer feedback for SIF and uncertain reports.
    Structure records so that future ML retraining can use:
    - AI prediction
    - Human final label
    - Reviewer
    - Review timestamp
    - Reviewer comment
    """
    df = load_review_queue()
    if df.empty or "report_id" not in df.columns:
        return False

    mask = df["report_id"].astype(str) == str(report_id)
    if not mask.any():
        return False

    # Ensure columns can accept string assignments
    for col in ["reviewer_decision", "reviewer_comment", "reviewer_name", "review_status", "reviewed_at"]:
        if col in df.columns:
            df[col] = df[col].astype(object)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.loc[mask, "reviewer_decision"] = str(human_label)
    df.loc[mask, "reviewer_comment"] = str(reviewer_note)
    df.loc[mask, "reviewer_name"] = str(reviewer)
    df.loc[mask, "review_status"] = str(status)
    df.loc[mask, "reviewed_at"] = now_str

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    return True


def add_new_report(report_id, narrative, site="Duliajan Central Asset", activity=None):
    """
    Analyze and append a new report narrative to the queue.
    """
    result = analyze_report(narrative)
    df = load_review_queue()

    lsr_rules = result.get("lsr_rules", [])
    lsr_text = "; ".join(lsr_rules) if lsr_rules else "None"
    act_text = activity or result.get("activity", "Unknown")

    final_res = result.get("final_result", "Needs Review")
    priority = "High" if final_res in ["SIF Potential", "Needs Review"] else "Low"
    status = "Pending Review" if final_res in ["SIF Potential", "Needs Review"] else "Not Yet Reviewed"

    new_row = {
        "report_id": str(report_id),
        "report_text": str(narrative),
        "site": str(site),
        "ai_result": final_res,
        "model_prediction": result.get("ml_prediction", "Non-SIF Potential"),
        "model_score": result.get("model_score", 0.5),
        "context": result.get("context", "Unknown"),
        "priority": priority,
        "activity": act_text,
        "hazard": result.get("hazard", "Unknown"),
        "hazards": result.get("hazard", "Unknown"),
        "hazard_evidence": result.get("hazard_evidence", ""),
        "barrier": result.get("barrier", "Unknown"),
        "barriers": result.get("barrier", "Unknown"),
        "barrier_evidence": result.get("barrier_evidence", ""),
        "barrier_condition": result.get("barrier_condition", "Uncertain / Unspecified"),
        "life_saving_rules": lsr_text,
        "evidence": result.get("primary_evidence", ""),
        "potential_consequence": result.get("potential_consequence", ""),
        "recommended_action": result.get("recommended_action", ""),
        "review_reason": result.get("review_reason", ""),
        "review_status": status,
        "reviewer_decision": "",
        "reviewer_comment": "",
        "reviewer_name": "",
        "reviewed_at": ""
    }

    df = pd.concat([pd.DataFrame([new_row]), df], ignore_index=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    return new_row


if __name__ == "__main__":
    print()
    print("=" * 70)
    print("              HSE REVIEW QUEUE GENERATOR")
    print("=" * 70)
    q_df = generate_review_queue()
    print(f"Total Reports: {len(q_df)}")
    print(f"SIF Potential: {(q_df['ai_result'] == 'SIF Potential').sum()}")
    print(f"Non-SIF Potential: {(q_df['ai_result'] == 'Non-SIF Potential').sum()}")
    print(f"Needs Review: {(q_df['ai_result'] == 'Needs Review').sum()}")
    print(f"High Priority: {(q_df['priority'] == 'High').sum()}")
    print("=" * 70)