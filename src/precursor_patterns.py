import pandas as pd
from collections import Counter
from analyze_report import analyze_report


DATASET_PATH = "data/dataset.csv"


def load_dataset():
    print("\nLoading safety report dataset...")

    df = pd.read_csv(DATASET_PATH)

    print(f"Dataset loaded: {len(df)} reports")

    return df


def analyze_all_reports(df):
    print("\nAnalyzing reports...")

    results = []

    for _, row in df.iterrows():

        report_id = row["report_id"]
        text = row["text"]
        sif_label = row["sif_label"]

        analysis = analyze_report(text)

        results.append({
            "report_id": report_id,
            "text": text,
            "sif_label": sif_label,
            "final_result": analysis["final_result"],

            "activity": analysis["activity"],
            "activities": "; ".join(
                analysis.get("activities", [])
            ),

            "hazard": analysis["hazard"],
            "hazards": "; ".join(
                h["hazard"]
                for h in analysis.get("hazards", [])
            ),

            "barrier": analysis["barrier"],
            "barriers": "; ".join(
                b["barrier"]
                for b in analysis.get("barriers", [])
            ),

            "lsr_rules": "; ".join(
                analysis.get("lsr_rules", [])
            ),

            "primary_evidence": analysis.get(
                "primary_evidence"
            )
        })

    print("Analysis completed.")

    return pd.DataFrame(results)


# ---------------------------------------------------------
# 1. ACTIVITY + HAZARD + BARRIER PATTERNS
# ---------------------------------------------------------

def find_precursor_patterns(results_df):

    print("\nFinding recurring patterns...")

    sif_df = results_df[
        results_df["final_result"] == "SIF Potential"
    ].copy()

    if sif_df.empty:
        print("\nNo SIF-potential reports found.")
        return pd.DataFrame()

    grouped = (
        sif_df
        .groupby(
            ["activity", "hazard", "barrier"],
            dropna=False
        )
        .size()
        .reset_index(name="occurrences")
    )

    def classify_status(count):

        if count >= 3:
            return "Recurring Pattern"

        elif count == 2:
            return "Repeated Pattern"

        else:
            return "Single Occurrence"

    grouped["status"] = grouped["occurrences"].apply(
        classify_status
    )

    grouped = grouped.sort_values(
        by=["occurrences", "activity"],
        ascending=[False, True]
    )

    return grouped


# ---------------------------------------------------------
# 2. CROSS-ACTIVITY HAZARD + BARRIER PATTERNS
# ---------------------------------------------------------

def find_cross_activity_patterns(results_df):

    print("\nFinding cross-activity precursor patterns...")

    sif_df = results_df[
        results_df["final_result"] == "SIF Potential"
    ].copy()

    if sif_df.empty:
        return pd.DataFrame()

    grouped = (
        sif_df
        .groupby(
            ["hazard", "barrier"],
            dropna=False
        )
        .agg(
            occurrences=("report_id", "count"),
            activities=("activity", lambda x: ", ".join(
                sorted(set(x))
            ))
        )
        .reset_index()
    )

    def classify_status(count):

        if count >= 3:
            return "Recurring Pattern"

        elif count == 2:
            return "Repeated Pattern"

        else:
            return "Single Occurrence"

    grouped["status"] = grouped["occurrences"].apply(
        classify_status
    )

    grouped = grouped.sort_values(
        by=["occurrences", "hazard"],
        ascending=[False, True]
    )

    return grouped


# ---------------------------------------------------------
# 3. LIFE-SAVING RULE FREQUENCY
# ---------------------------------------------------------

def find_lsr_frequency(results_df):

    sif_df = results_df[
        results_df["final_result"] == "SIF Potential"
    ]

    counter = Counter()

    for rules in sif_df["lsr_rules"]:

        if not rules:
            continue

        for rule in rules.split("; "):
            if rule:
                counter[rule] += 1

    return counter


# ---------------------------------------------------------
# 4. ACTIVITY FREQUENCY
# ---------------------------------------------------------

def find_activity_frequency(results_df):

    sif_df = results_df[
        results_df["final_result"] == "SIF Potential"
    ]

    counter = Counter()

    for activities in sif_df["activities"]:

        if not activities:
            continue

        for activity in activities.split("; "):
            if activity:
                counter[activity] += 1

    return counter


# ---------------------------------------------------------
# 5. HAZARD FREQUENCY
# ---------------------------------------------------------

def find_hazard_frequency(results_df):

    sif_df = results_df[
        results_df["final_result"] == "SIF Potential"
    ]

    counter = Counter()

    for hazards in sif_df["hazards"]:

        if not hazards:
            continue

        for hazard in hazards.split("; "):
            if hazard:
                counter[hazard] += 1

    return counter


# ---------------------------------------------------------
# 6. BARRIER FREQUENCY
# ---------------------------------------------------------

def find_barrier_frequency(results_df):

    sif_df = results_df[
        results_df["final_result"] == "SIF Potential"
    ]

    counter = Counter()

    for barriers in sif_df["barriers"]:

        if not barriers:
            continue

        for barrier in barriers.split("; "):
            if barrier:
                counter[barrier] += 1

    return counter


# ---------------------------------------------------------
# DISPLAY
# ---------------------------------------------------------

def display_analysis(
    results_df,
    precursor_patterns,
    cross_activity_patterns,
    lsr_frequency,
    activity_frequency,
    hazard_frequency,
    barrier_frequency
):

    print("\n" + "=" * 70)
    print("             PRECURSOR PATTERN ANALYSIS")
    print("=" * 70)

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    total = len(results_df)

    sif_count = len(
        results_df[
            results_df["final_result"] == "SIF Potential"
        ]
    )

    non_sif_count = len(
        results_df[
            results_df["final_result"] == "Non-SIF Potential"
        ]
    )

    review_count = len(
        results_df[
            results_df["final_result"] == "Needs Review"
        ]
    )

    print("\nSUMMARY")
    print("-" * 70)

    print(f"Total Reports      : {total}")
    print(f"SIF Potential      : {sif_count}")
    print(f"Non-SIF Potential  : {non_sif_count}")
    print(f"Needs Review       : {review_count}")

    # -----------------------------------------------------
    # ACTIVITY + HAZARD + BARRIER
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("ACTIVITY + HAZARD + BARRIER PATTERNS")
    print("=" * 70)

    if precursor_patterns.empty:

        print("\nNo precursor patterns found.")

    else:

        for index, row in precursor_patterns.iterrows():

            print(f"\nPattern {index + 1}")

            print(f"Activity   : {row['activity']}")
            print(f"Hazard     : {row['hazard']}")
            print(f"Barrier    : {row['barrier']}")
            print(f"Occurrences: {row['occurrences']}")
            print(f"Status     : {row['status']}")

    # -----------------------------------------------------
    # CROSS-ACTIVITY PATTERNS
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("CROSS-ACTIVITY PRECURSOR PATTERNS")
    print("=" * 70)

    if cross_activity_patterns.empty:

        print("\nNo cross-activity patterns found.")

    else:

        for index, row in cross_activity_patterns.iterrows():

            print(f"\nPattern {index + 1}")

            print(f"Hazard     : {row['hazard']}")
            print(f"Barrier    : {row['barrier']}")
            print(f"Occurrences: {row['occurrences']}")
            print(f"Activities : {row['activities']}")
            print(f"Status     : {row['status']}")

    # -----------------------------------------------------
    # LSR
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("LIFE-SAVING RULE FREQUENCY")
    print("=" * 70)

    for rule, count in lsr_frequency.most_common():

        print(f"{rule} -> {count} reports")

    # -----------------------------------------------------
    # ACTIVITIES
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("SIF-POTENTIAL ACTIVITY FREQUENCY")
    print("=" * 70)

    for activity, count in activity_frequency.most_common():

        print(f"{activity} -> {count} reports")

    # -----------------------------------------------------
    # HAZARDS
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("SIF-POTENTIAL HAZARD FREQUENCY")
    print("=" * 70)

    for hazard, count in hazard_frequency.most_common():

        print(f"{hazard} -> {count} reports")

    # -----------------------------------------------------
    # BARRIERS
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("SIF-POTENTIAL BARRIER FREQUENCY")
    print("=" * 70)

    for barrier, count in barrier_frequency.most_common():

        print(f"{barrier} -> {count} reports")

    print("\n" + "=" * 70)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    df = load_dataset()

    results_df = analyze_all_reports(df)

    precursor_patterns = find_precursor_patterns(
        results_df
    )

    cross_activity_patterns = find_cross_activity_patterns(
        results_df
    )

    lsr_frequency = find_lsr_frequency(
        results_df
    )

    activity_frequency = find_activity_frequency(
        results_df
    )

    hazard_frequency = find_hazard_frequency(
        results_df
    )

    barrier_frequency = find_barrier_frequency(
        results_df
    )

    display_analysis(
        results_df,
        precursor_patterns,
        cross_activity_patterns,
        lsr_frequency,
        activity_frequency,
        hazard_frequency,
        barrier_frequency
    )


if __name__ == "__main__":
    main()