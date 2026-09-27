from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd


# ============================================================
# PATHS / IMPORTS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DATASET_PATH = PROJECT_ROOT / "data" / "dataset.csv"
REVIEW_QUEUE_PATH = PROJECT_ROOT / "results" / "review_queue.csv"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analyze_report import analyze_report  # noqa: E402


IOGP_LIFE_SAVING_RULES = [
    "Bypassing Safety Controls",
    "Confined Space",
    "Driving",
    "Energy Isolation",
    "Hot Work",
    "Line of Fire",
    "Safe Mechanical Lifting",
    "Work Authorization",
    "Working at Height",
]


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _clean_text(value: Any, default: str = "Unknown") -> str:
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except Exception:
        pass
    text = str(value).strip()
    return text if text else default


def _normalise_result_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise historic/new result schemas into one frontend-friendly schema."""
    df = df.copy()

    rename_map = {}
    if "text" in df.columns and "report_text" not in df.columns:
        rename_map["text"] = "report_text"
    if "final_result" in df.columns and "ai_result" not in df.columns:
        rename_map["final_result"] = "ai_result"
    if "ml_prediction" in df.columns and "model_prediction" not in df.columns:
        rename_map["ml_prediction"] = "model_prediction"
    if "primary_evidence" in df.columns and "evidence" not in df.columns:
        rename_map["primary_evidence"] = "evidence"
    if "lsr_rules" in df.columns and "life_saving_rules" not in df.columns:
        rename_map["lsr_rules"] = "life_saving_rules"

    if rename_map:
        df = df.rename(columns=rename_map)

    defaults = {
        "report_id": "",
        "report_text": "",
        "site": "Unknown / Not Provided",
        "ai_result": "Needs Review",
        "model_prediction": "Non-SIF Potential",
        "model_score": 0.0,
        "context": "Unknown",
        "priority": "High",
        "activity": "Unknown",
        "hazard": "Unknown",
        "barrier": "Unknown",
        "barrier_condition": "Uncertain / Unspecified",
        "life_saving_rules": "[]",
        "evidence": None,
        "potential_consequence": None,
        "recommended_action": None,
        "review_reason": None,
        "review_status": "",
        "reviewer_decision": "",
        "reviewer_comment": "",
        "reviewer_name": "",
        "reviewed_at": "",
    }

    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default

    df["site"] = df["site"].apply(lambda x: _clean_text(x, "Unknown / Not Provided"))
    df["activity"] = df["activity"].apply(lambda x: _clean_text(x, "Unknown"))
    df["hazard"] = df["hazard"].apply(lambda x: _clean_text(x, "Unknown"))
    df["barrier"] = df["barrier"].apply(lambda x: _clean_text(x, "Unknown"))
    df["ai_result"] = df["ai_result"].apply(lambda x: _clean_text(x, "Needs Review"))
    df["priority"] = df["priority"].apply(lambda x: _clean_text(x, "High"))

    return df


def _parse_lsr(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]

    if isinstance(value, tuple):
        return [str(x).strip() for x in value if str(x).strip()]

    try:
        if pd.isna(value):
            return []
    except Exception:
        pass

    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "[]"}:
        return []

    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, (list, tuple)):
            return [str(x).strip() for x in parsed if str(x).strip()]
    except Exception:
        pass

    # Graceful fallback for comma/semicolon separated strings.
    separator = ";" if ";" in text else ","
    return [
        item.strip().strip("'\"[]")
        for item in text.split(separator)
        if item.strip().strip("'\"[]")
    ]


def _mode(series: pd.Series, default: str = "Unknown") -> str:
    cleaned = (
        series.dropna()
        .astype(str)
        .str.strip()
    )
    cleaned = cleaned[
        ~cleaned.str.lower().isin({"", "nan", "none", "unknown", "unknown / not provided"})
    ]
    if cleaned.empty:
        return default
    modes = cleaned.mode()
    return str(modes.iloc[0]) if not modes.empty else str(cleaned.iloc[0])


def _top_lsr_from_rows(df: pd.DataFrame, default: str = "None") -> str:
    values: List[str] = []
    if "life_saving_rules" not in df.columns:
        return default
    for item in df["life_saving_rules"]:
        values.extend(_parse_lsr(item))
    if not values:
        return default
    return pd.Series(values).mode().iloc[0]


def _status_from_count(count: int) -> str:
    if count >= 3:
        return "Recurring Pattern"
    if count == 2:
        return "Repeated Pattern"
    return "Single Occurrence"


def _load_source_reports() -> pd.DataFrame:
    """
    Prefer the generated review_queue.csv because it already contains site metadata
    plus full analysis fields. Fall back to analyzing data/dataset.csv if needed.
    """
    if REVIEW_QUEUE_PATH.exists():
        return _normalise_result_frame(pd.read_csv(REVIEW_QUEUE_PATH))

    if DATASET_PATH.exists():
        raw = pd.read_csv(DATASET_PATH)
        return analyze_batch_reports(raw)

    raise FileNotFoundError(
        "No backend data found. Expected results/review_queue.csv or data/dataset.csv."
    )


# ============================================================
# PUBLIC BACKEND ADAPTER
# ============================================================

def analyze_single_report(
    text: str,
    site: Optional[str] = None,
    report_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Analyze one free-text safety report and return a frontend-ready dictionary."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("A non-empty safety report is required.")

    analysis = analyze_report(text.strip())

    return {
        "report_id": report_id or "",
        "report_text": text.strip(),
        "site": site.strip() if isinstance(site, str) and site.strip() else "Unknown / Not Provided",
        "ai_result": analysis.get("final_result", "Needs Review"),
        "model_prediction": analysis.get("ml_prediction", "Non-SIF Potential"),
        "model_score": analysis.get("model_score", 0.0),
        "context": analysis.get("context", "Unknown"),
        "priority": analysis.get("priority", "High"),
        "activity": analysis.get("activity", "Unknown"),
        "activities": analysis.get("activities", []),
        "activity_evidence": analysis.get("activity_evidence", {}),
        "hazard": analysis.get("hazard", "Unknown"),
        "hazards": analysis.get("hazards", []),
        "hazard_evidence": analysis.get("hazard_evidence", []),
        "barrier": analysis.get("barrier", "Unknown"),
        "barriers": analysis.get("barriers", []),
        "barrier_evidence": analysis.get("barrier_evidence", []),
        "barrier_condition": analysis.get("barrier_condition", "Uncertain / Unspecified"),
        "life_saving_rules": analysis.get("lsr_rules", []),
        "lsr_evidence": analysis.get("lsr_evidence", {}),
        "evidence": analysis.get("primary_evidence"),
        "potential_consequence": analysis.get("potential_consequence"),
        "recommended_action": analysis.get("recommended_action"),
        "review_reason": analysis.get("review_reason"),
        "contradiction_detected": analysis.get("contradiction_detected", False),
        "contradiction_reason": analysis.get("contradiction_reason"),
        "review_status": "Pending" if analysis.get("final_result") == "Needs Review" else "",
        "reviewer_decision": "",
        "reviewer_comment": "",
        "reviewer_name": "",
        "reviewed_at": "",
    }


def analyze_batch_reports(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze a dataframe of safety narratives.

    Required: one of text/report_text/description/narrative.
    Optional: report_id, site/location.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("analyze_batch_reports expects a pandas DataFrame.")

    text_candidates = ["text", "report_text", "description", "narrative"]
    site_candidates = ["site", "location", "site_location"]

    text_col = next((c for c in text_candidates if c in df.columns), None)
    if text_col is None:
        raise ValueError(
            "No report text column found. Use one of: text, report_text, description, narrative."
        )

    site_col = next((c for c in site_candidates if c in df.columns), None)
    report_id_col = "report_id" if "report_id" in df.columns else None

    rows: List[Dict[str, Any]] = []

    for index, row in df.iterrows():
        report_text = _clean_text(row.get(text_col), "")
        if not report_text:
            continue

        report_id = (
            _clean_text(row.get(report_id_col), "")
            if report_id_col
            else f"B{len(rows) + 1:04d}"
        )

        site = (
            _clean_text(row.get(site_col), "Unknown / Not Provided")
            if site_col
            else "Unknown / Not Provided"
        )

        result = analyze_single_report(
            report_text,
            site=site,
            report_id=report_id,
        )
        rows.append(result)

    return _normalise_result_frame(pd.DataFrame(rows))


def get_reports() -> pd.DataFrame:
    """Return all analyzed reports in a stable schema."""
    return _load_source_reports().copy()


def get_review_queue() -> pd.DataFrame:
    """Return only reports requiring human HSE review."""
    df = get_reports()
    queue = df[df["ai_result"].eq("Needs Review")].copy()

    if "review_status" not in queue.columns:
        queue["review_status"] = "Pending"
    else:
        queue["review_status"] = queue["review_status"].fillna("").astype(str)
        queue.loc[queue["review_status"].str.strip().eq(""), "review_status"] = "Pending"

    return queue.reset_index(drop=True)


def get_life_saving_rule_summary() -> pd.DataFrame:
    """
    Count Life-Saving Rules on final SIF-potential reports only.
    Safe-control mentions are therefore not treated as rule violations.
    """
    df = get_reports()
    sif = df[df["ai_result"].eq("SIF Potential")].copy()

    counts = {rule: 0 for rule in IOGP_LIFE_SAVING_RULES}

    for value in sif["life_saving_rules"]:
        for rule in _parse_lsr(value):
            if rule in counts:
                counts[rule] += 1
            else:
                counts[rule] = counts.get(rule, 0) + 1

    out = pd.DataFrame(
        [{"life_saving_rule": rule, "sif_reports": count} for rule, count in counts.items()]
    )
    return out.sort_values(["sif_reports", "life_saving_rule"], ascending=[False, True]).reset_index(drop=True)


def get_site_density() -> pd.DataFrame:
    """
    Rank sites by final SIF-potential density.

    Density denominator includes all reports at the site, including Needs Review.
    """
    df = get_reports()
    rows: List[Dict[str, Any]] = []

    for site, group in df.groupby("site", dropna=False):
        total = len(group)
        sif = group[group["ai_result"].eq("SIF Potential")]
        non_sif = group[group["ai_result"].eq("Non-SIF Potential")]
        review = group[group["ai_result"].eq("Needs Review")]

        rows.append(
            {
                "site": _clean_text(site, "Unknown / Not Provided"),
                "total_reports": total,
                "sif_reports": len(sif),
                "non_sif_reports": len(non_sif),
                "needs_review": len(review),
                "sif_density": round((len(sif) / total * 100.0) if total else 0.0, 1),
                "top_hazard": _mode(sif["hazard"]) if not sif.empty else "None",
                "top_barrier": _mode(sif["barrier"]) if not sif.empty else "None",
                "top_activity": _mode(sif["activity"]) if not sif.empty else "None",
                "top_lsr": _top_lsr_from_rows(sif) if not sif.empty else "None",
            }
        )

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    return out.sort_values(
        ["sif_density", "sif_reports", "total_reports", "site"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def get_activity_density() -> pd.DataFrame:
    """
    Rank activities by final SIF-potential density.

    Density denominator includes SIF, Non-SIF and Needs Review reports.
    """
    df = get_reports()
    rows: List[Dict[str, Any]] = []

    for activity, group in df.groupby("activity", dropna=False):
        total = len(group)
        sif = group[group["ai_result"].eq("SIF Potential")]
        non_sif = group[group["ai_result"].eq("Non-SIF Potential")]
        review = group[group["ai_result"].eq("Needs Review")]

        rows.append(
            {
                "activity": _clean_text(activity, "Unknown"),
                "total_reports": total,
                "sif_reports": len(sif),
                "non_sif_reports": len(non_sif),
                "needs_review": len(review),
                "sif_density": round((len(sif) / total * 100.0) if total else 0.0, 1),
                "top_hazard": _mode(sif["hazard"]) if not sif.empty else "None",
                "top_barrier": _mode(sif["barrier"]) if not sif.empty else "None",
                "top_site": _mode(sif["site"], "Unknown / Not Provided") if not sif.empty else "None",
                "top_lsr": _top_lsr_from_rows(sif) if not sif.empty else "None",
            }
        )

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    return out.sort_values(
        ["sif_density", "sif_reports", "total_reports", "activity"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def get_site_activity_hotspots(limit: int = 10) -> pd.DataFrame:
    """Rank site+activity combinations by SIF precursor density."""
    df = get_reports()
    rows: List[Dict[str, Any]] = []

    grouped = df.groupby(["site", "activity"], dropna=False)

    for (site, activity), group in grouped:
        total = len(group)
        sif = group[group["ai_result"].eq("SIF Potential")]

        rows.append(
            {
                "site": _clean_text(site, "Unknown / Not Provided"),
                "activity": _clean_text(activity, "Unknown"),
                "total_reports": total,
                "sif_reports": len(sif),
                "sif_density": round((len(sif) / total * 100.0) if total else 0.0, 1),
                "top_hazard": _mode(sif["hazard"]) if not sif.empty else "None",
                "top_barrier": _mode(sif["barrier"]) if not sif.empty else "None",
            }
        )

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    out = out.sort_values(
        ["sif_density", "sif_reports", "total_reports"],
        ascending=[False, False, False],
    ).reset_index(drop=True)

    return out.head(max(int(limit), 1))


def get_precursor_patterns() -> pd.DataFrame:
    """
    Build recurring SIF precursor patterns using:
      - site + activity + hazard + barrier
      - cross-site activity + hazard + barrier
      - cross-activity site + hazard + barrier

    Patterns are based on final SIF-potential reports.
    """
    df = get_reports()
    sif = df[df["ai_result"].eq("SIF Potential")].copy()

    if sif.empty:
        return pd.DataFrame(
            columns=[
                "pattern_id",
                "pattern_type",
                "site",
                "sites",
                "activity",
                "activities",
                "hazard",
                "barrier",
                "occurrences",
                "status",
            ]
        )

    pattern_rows: List[Dict[str, Any]] = []

    # 1) Site-specific pattern
    grouped = (
        sif.groupby(["site", "activity", "hazard", "barrier"], dropna=False)
        .size()
        .reset_index(name="occurrences")
    )

    for _, row in grouped.iterrows():
        count = int(row["occurrences"])
        pattern_rows.append(
            {
                "pattern_type": "Site-specific",
                "site": _clean_text(row["site"], "Unknown / Not Provided"),
                "sites": [_clean_text(row["site"], "Unknown / Not Provided")],
                "activity": _clean_text(row["activity"], "Unknown"),
                "activities": [_clean_text(row["activity"], "Unknown")],
                "hazard": _clean_text(row["hazard"], "Unknown"),
                "barrier": _clean_text(row["barrier"], "Unknown"),
                "occurrences": count,
                "status": _status_from_count(count),
            }
        )

    # 2) Cross-site pattern
    for (activity, hazard, barrier), group in sif.groupby(
        ["activity", "hazard", "barrier"], dropna=False
    ):
        sites = sorted({_clean_text(x, "Unknown / Not Provided") for x in group["site"]})
        count = len(group)
        if count >= 2 and len(sites) >= 2:
            pattern_rows.append(
                {
                    "pattern_type": "Cross-site",
                    "site": "Multiple Sites",
                    "sites": sites,
                    "activity": _clean_text(activity, "Unknown"),
                    "activities": [_clean_text(activity, "Unknown")],
                    "hazard": _clean_text(hazard, "Unknown"),
                    "barrier": _clean_text(barrier, "Unknown"),
                    "occurrences": count,
                    "status": _status_from_count(count),
                }
            )

    # 3) Cross-activity pattern
    for (site, hazard, barrier), group in sif.groupby(
        ["site", "hazard", "barrier"], dropna=False
    ):
        activities = sorted({_clean_text(x, "Unknown") for x in group["activity"]})
        count = len(group)
        if count >= 2 and len(activities) >= 2:
            pattern_rows.append(
                {
                    "pattern_type": "Cross-activity",
                    "site": _clean_text(site, "Unknown / Not Provided"),
                    "sites": [_clean_text(site, "Unknown / Not Provided")],
                    "activity": "Multiple Activities",
                    "activities": activities,
                    "hazard": _clean_text(hazard, "Unknown"),
                    "barrier": _clean_text(barrier, "Unknown"),
                    "occurrences": count,
                    "status": _status_from_count(count),
                }
            )

    out = pd.DataFrame(pattern_rows)
    if out.empty:
        return out

    out = out.sort_values(
        ["occurrences", "pattern_type", "hazard"],
        ascending=[False, True, True],
    ).reset_index(drop=True)

    out.insert(0, "pattern_id", [f"P{i:03d}" for i in range(1, len(out) + 1)])
    return out


def get_dashboard_summary() -> Dict[str, Any]:
    """Return real backend statistics for the Streamlit dashboard."""
    df = get_reports()

    total = len(df)
    sif = df[df["ai_result"].eq("SIF Potential")]
    non_sif = df[df["ai_result"].eq("Non-SIF Potential")]
    review = df[df["ai_result"].eq("Needs Review")]
    high = df[df["priority"].eq("High")]

    site_density = get_site_density()
    activity_density = get_activity_density()
    lsr_summary = get_life_saving_rule_summary()

    highest_site = site_density.iloc[0] if not site_density.empty else None
    highest_activity = activity_density.iloc[0] if not activity_density.empty else None
    top_lsr_row = (
        lsr_summary[lsr_summary["sif_reports"] > 0].iloc[0]
        if not lsr_summary.empty and (lsr_summary["sif_reports"] > 0).any()
        else None
    )

    classified = len(sif) + len(non_sif)

    return {
        "total_reports": total,
        "sif_potential": len(sif),
        "non_sif_potential": len(non_sif),
        "needs_review": len(review),
        "high_priority": len(high),
        "binary_classified": classified,
        "classification_coverage_pct": round((classified / total * 100.0) if total else 0.0, 1),
        "abstention_rate_pct": round((len(review) / total * 100.0) if total else 0.0, 1),
        "highest_density_site": highest_site["site"] if highest_site is not None else None,
        "highest_density_site_value": float(highest_site["sif_density"]) if highest_site is not None else 0.0,
        "highest_density_activity": highest_activity["activity"] if highest_activity is not None else None,
        "highest_density_activity_value": float(highest_activity["sif_density"]) if highest_activity is not None else 0.0,
        "top_hazard": _mode(sif["hazard"], "None") if not sif.empty else "None",
        "top_barrier": _mode(sif["barrier"], "None") if not sif.empty else "None",
        "top_lsr": top_lsr_row["life_saving_rule"] if top_lsr_row is not None else "None",
    }


__all__ = [
    "analyze_single_report",
    "analyze_batch_reports",
    "get_reports",
    "get_dashboard_summary",
    "get_site_density",
    "get_activity_density",
    "get_site_activity_hotspots",
    "get_life_saving_rule_summary",
    "get_precursor_patterns",
    "get_review_queue",
]
