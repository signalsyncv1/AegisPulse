import joblib
from pathlib import Path

from safety_rules import analyze_safety_context
from hazard_barrier import detect_hazards, detect_barriers
from life_saving_rules import detect_life_saving_rules
from activity_detection import detect_activity


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "sif_classifier.pkl"


# ============================================================
# LOAD ML MODEL SAFELY
# ============================================================

def get_model():
    if MODEL_PATH.exists():
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            pass
    dataset_path = BASE_DIR / "data" / "dataset.csv"
    if dataset_path.exists():
        try:
            import pandas as pd
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import Pipeline
            df = pd.read_csv(dataset_path)
            pipeline = Pipeline([
                ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2))),
                ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced"))
            ])
            pipeline.fit(df["text"], df["sif_label"])
            MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(pipeline, MODEL_PATH)
            return pipeline
        except Exception:
            pass
    return None

model = get_model()


# ============================================================
# CONTRADICTION DETECTION
# ============================================================

def detect_contradictions(report):

    report_lower = report.lower()

    contradiction_detected = False
    contradiction_reason = None

    # --------------------------------------------------------
    # Isolation contradiction
    # --------------------------------------------------------

    safe_isolation_phrases = [
        "isolation was completed",
        "isolation was completed and verified",
        "isolation was completed but",
        "electrical isolation was completed",
        "energy isolation was completed",
        "equipment was isolated",
        "equipment was isolated, locked out",
    ]

    unsafe_verification_phrases = [
        "was not verified",
        "not verified",
        "wasn't verified",
        "could not be verified",
        "not been verified",
    ]

    has_safe_isolation = any(
        phrase in report_lower
        for phrase in safe_isolation_phrases
    )

    has_unverified_isolation = any(
        phrase in report_lower
        for phrase in unsafe_verification_phrases
    )

    if has_safe_isolation and has_unverified_isolation:

        contradiction_detected = True

        contradiction_reason = (
            "Isolation was reported as completed, "
            "but verification was reported as incomplete."
        )

    # --------------------------------------------------------
    # Work authorization / permit contradiction
    # --------------------------------------------------------

    permit_conflict_phrases = [
        "conflicting information about whether the work permit was approved",
        "conflicting information about whether the permit was approved",
        "unclear whether the work permit was approved",
        "unclear whether the permit was approved",
    ]

    if any(phrase in report_lower for phrase in permit_conflict_phrases):
        contradiction_detected = True
        contradiction_reason = (
            "The report contains conflicting or unclear information about "
            "whether work authorization was approved before the task started."
        )

    return {
        "contradiction_detected": contradiction_detected,
        "contradiction_reason": contradiction_reason
    }


# ============================================================
# MAIN REPORT ANALYSIS
# ============================================================

def analyze_report(report):

    # --------------------------------------------------------
    # 1. ML SIF CLASSIFICATION
    # --------------------------------------------------------

    if model is not None:
        try:
            ml_prediction = model.predict([report])[0]
            probabilities = model.predict_proba([report])[0]
            sif_score = float(probabilities[1])
        except Exception:
            ml_prediction = 0
            sif_score = 0.5
    else:
        ml_prediction = 0
        sif_score = 0.5


    # --------------------------------------------------------
    # 2. SAFETY CONTEXT
    # --------------------------------------------------------

    context_result = analyze_safety_context(report)

    context = context_result["context"]

    dangerous_conditions = context_result["dangerous_conditions"]

    safe_controls = context_result["safe_controls"]

    routine_observations = context_result["routine_observations"]


    # --------------------------------------------------------
    # 3. CONTRADICTION CHECK
    # --------------------------------------------------------

    contradiction_result = detect_contradictions(report)

    contradiction_detected = contradiction_result[
        "contradiction_detected"
    ]

    contradiction_reason = contradiction_result[
        "contradiction_reason"
    ]


    # --------------------------------------------------------
    # 4. ACTIVITY DETECTION
    # --------------------------------------------------------

    activity_result = detect_activity(report)

    activity = activity_result["activity"]

    activities = activity_result["activities"]

    activity_evidence = activity_result["activity_evidence"]


    # --------------------------------------------------------
    # 5. MULTIPLE HAZARD DETECTION
    # --------------------------------------------------------

    hazards_result = detect_hazards(report)

    hazards = hazards_result

    # Keep primary hazard for backward compatibility

    primary_hazard = hazards[0]

    hazard = primary_hazard["hazard"]

    hazard_evidence = primary_hazard["evidence"]


    # --------------------------------------------------------
    # 6. MULTIPLE BARRIER DETECTION
    # --------------------------------------------------------

    barriers_result = detect_barriers(report)

    barriers = barriers_result

    # Keep primary barrier for backward compatibility

    primary_barrier = barriers[0]

    barrier = primary_barrier["barrier"]

    barrier_evidence = primary_barrier["evidence"]


    # --------------------------------------------------------
    # 7. LIFE-SAVING RULE DETECTION
    # --------------------------------------------------------

    lsr_result = detect_life_saving_rules(report)

    lsr_rules = lsr_result["lsr_rules"]

    lsr_evidence = lsr_result["lsr_evidence"]

    safe_control_present = lsr_result["safe_control_present"]


    # --------------------------------------------------------
    # 8. FINAL SIF DECISION
    # --------------------------------------------------------
    #
    # Priority:
    #
    # Contradictory Information
    #       ↓
    # Needs Review
    #
    # Dangerous Condition
    #       ↓
    # SIF Potential
    #
    # Clear Safe Control
    #       ↓
    # Non-SIF Potential
    #
    # Routine / Low-Potential Observation
    #       ↓
    # Non-SIF Potential
    #
    # Insufficient Information
    #       ↓
    # Needs Review
    #
    # --------------------------------------------------------

    if contradiction_detected:

        final_result = "Needs Review"

        context = "Contradictory Information"

    elif context == "Dangerous Condition":

        final_result = "SIF Potential"

    elif context == "Control Present":

        final_result = "Non-SIF Potential"

    elif context == "Routine / Low-Potential Observation":

        final_result = "Non-SIF Potential"

    elif context == "Insufficient Information":

        final_result = "Needs Review"

    else:

        # Fallback to ML prediction

        if ml_prediction == 1:

            final_result = "SIF Potential"

        else:

            final_result = "Non-SIF Potential"


    # --------------------------------------------------------
    # 9. PRIMARY EVIDENCE
    # --------------------------------------------------------

    if contradiction_detected:

        primary_evidence = contradiction_reason

    elif dangerous_conditions:

        primary_evidence = dangerous_conditions[0]["evidence"]

    elif safe_controls:

        sc = safe_controls[0]
        primary_evidence = sc.get("evidence", str(sc)) if isinstance(sc, dict) else str(sc)

    elif routine_observations:

        primary_evidence = routine_observations[0]

    elif hazard_evidence:

        primary_evidence = hazard_evidence[0] if isinstance(hazard_evidence, list) and hazard_evidence else str(hazard_evidence)

    elif barrier_evidence:

        primary_evidence = barrier_evidence[0] if isinstance(barrier_evidence, list) and barrier_evidence else str(barrier_evidence)

    else:

        primary_evidence = None


    # --------------------------------------------------------
    # 10. BARRIER CONDITION & INTELLIGENCE
    # --------------------------------------------------------

    if final_result == "SIF Potential" or dangerous_conditions:
        barrier_condition = "Incomplete / Failed"
        priority = "High"
    elif final_result == "Non-SIF Potential" or safe_controls:
        barrier_condition = "Intact / Verified"
        priority = "Low"
    else:
        barrier_condition = "Uncertain / Unspecified"
        priority = "High"  # Prioritize for human triage

    # Review reason
    if final_result == "Needs Review":
        if contradiction_detected:
            review_reason = contradiction_reason
        else:
            review_reason = context_result.get("reason") or "Insufficient information to establish hazard exposure and barrier condition."
    else:
        review_reason = None

    # Potential consequence mapping
    consequence_map = {
        "Unexpected Energization": "Electrocution / High-Pressure Discharge / Severe Trauma",
        "Suspended Load / Struck-by": "Crush Injury / Fatality / Heavy Impact Trauma",
        "Fall from Height": "Fatal Fall / Severe Skeletal Trauma",
        "Confined Space Exposure": "Asphyxiation / Toxic Gas Inhalation / Loss of Consciousness",
        "Hot Work Exposure": "Explosion / Flash Fire / Severe Burn Injury",
        "Vehicle / Pedestrian Interaction": "Pedestrian Run-Over / Severe Crush Injury",
        "Line-of-Fire Exposure": "Line-of-Fire Impact / Pinch Point Severing",
    }
    if final_result == "SIF Potential":
        potential_consequence = consequence_map.get(hazard, "Serious Injury / Fatality (SIF)")
    elif final_result == "Needs Review":
        potential_consequence = "Unspecified / Insufficient narrative to establish consequence"
    else:
        potential_consequence = "Minor Impact / Routine Observation / Controlled State"

    # Recommended HSE Action
    if final_result == "SIF Potential":
        if "Energy Isolation" in lsr_rules or hazard == "Unexpected Energization" or barrier == "Energy Isolation":
            recommended_action = "Review isolation compliance, verify zero energy, and audit permit/LOTO controls."
        elif "Safe Mechanical Lifting" in lsr_rules or "Line of Fire" in lsr_rules or hazard == "Suspended Load / Struck-by":
            recommended_action = "Halt lifting immediately; re-establish physical exclusion zones and remove personnel from line-of-fire."
        elif "Working at Height" in lsr_rules or hazard == "Fall from Height":
            recommended_action = "Suspend work at height until 100% fall protection and anchor points are inspected and verified."
        elif "Confined Space" in lsr_rules or hazard == "Confined Space Exposure":
            recommended_action = "Evacuate space immediately; conduct atmospheric gas testing and verify entry authorization permit."
        elif "Hot Work" in lsr_rules or hazard == "Hot Work Exposure":
            recommended_action = "Halt hot work; verify gas testing certificates and ensure 15m combustible clearance."
        elif "Driving" in lsr_rules or hazard == "Vehicle / Pedestrian Interaction":
            recommended_action = "Enforce pedestrian-vehicle segregation distances and assign dedicated spotters during movement."
        else:
            recommended_action = "Initiate immediate operational pause and conduct safety barrier verification."
    elif final_result == "Needs Review":
        recommended_action = "Assign HSE reviewer to verify missing hazard exposure, task details, and barrier status with site supervisor."
    else:
        recommended_action = "Log observation in HSE tracking system; reinforce positive safety practices and routine housekeeping."


    # --------------------------------------------------------
    # 11. RETURN COMPLETE ANALYSIS
    # --------------------------------------------------------

    return {

        # ----------------------------------------------------
        # ML RESULT
        # ----------------------------------------------------

        "ml_prediction":
            "SIF Potential"
            if ml_prediction == 1
            else "Non-SIF Potential",

        "model_score":
            round(float(sif_score), 2),


        # ----------------------------------------------------
        # FINAL DECISION & INTELLIGENCE
        # ----------------------------------------------------

        "context":
            context,

        "final_result":
            final_result,

        "priority":
            priority,

        "barrier_condition":
            barrier_condition,

        "potential_consequence":
            potential_consequence,

        "recommended_action":
            recommended_action,

        "review_reason":
            review_reason,


        # ----------------------------------------------------
        # CONTRADICTION
        # ----------------------------------------------------

        "contradiction_detected":
            contradiction_detected,

        "contradiction_reason":
            contradiction_reason,


        # ----------------------------------------------------
        # ACTIVITY
        # ----------------------------------------------------

        "activity":
            activity,

        "activities":
            activities,

        "activity_evidence":
            activity_evidence,


        # ----------------------------------------------------
        # PRIMARY EVIDENCE
        # ----------------------------------------------------

        "primary_evidence":
            primary_evidence,


        # ----------------------------------------------------
        # PRIMARY HAZARD
        # ----------------------------------------------------

        "hazard":
            hazard,

        "hazard_evidence":
            hazard_evidence,


        # ----------------------------------------------------
        # ALL HAZARDS
        # ----------------------------------------------------

        "hazards":
            hazards,


        # ----------------------------------------------------
        # PRIMARY BARRIER
        # ----------------------------------------------------

        "barrier":
            barrier,

        "barrier_evidence":
            barrier_evidence,


        # ----------------------------------------------------
        # ALL BARRIERS
        # ----------------------------------------------------

        "barriers":
            barriers,


        # ----------------------------------------------------
        # LIFE-SAVING RULES
        # ----------------------------------------------------

        "lsr_rules":
            lsr_rules,

        "lsr_evidence":
            lsr_evidence,


        # ----------------------------------------------------
        # SAFETY CONTEXT
        # ----------------------------------------------------

        "safe_control_present":
            safe_control_present,

        "dangerous_conditions":
            dangerous_conditions,

        "safe_controls":
            safe_controls,

        "routine_observations":
            routine_observations
    }


# ============================================================
# TEST REPORTS
# ============================================================

if __name__ == "__main__":

    test_reports = [

        "During pump maintenance, electrical isolation was not completed before the technician entered the equipment area.",

        "Hot work was performed after the permit was approved and gas testing was completed.",

        "The confined space was tested and confirmed safe before authorized entry.",

        "A worker was standing below a suspended load during crane lifting operations.",

        "A vehicle was reversing near workers without adequate separation or spotter control.",

        "The equipment was isolated, locked out, and verified before maintenance."
    ]


    for report in test_reports:

        print("\n")
        print("=" * 80)

        print("REPORT:")
        print(report)

        print("=" * 80)

        result = analyze_report(report)


        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        print("\nFINAL RESULT:")
        print(result["final_result"])


        # ----------------------------------------------------
        # ML
        # ----------------------------------------------------

        print("\nML PREDICTION:")
        print(result["ml_prediction"])

        print("MODEL SCORE:")
        print(result["model_score"])


        # ----------------------------------------------------
        # CONTEXT
        # ----------------------------------------------------

        print("\nSAFETY CONTEXT:")
        print(result["context"])


        # ----------------------------------------------------
        # ACTIVITY
        # ----------------------------------------------------

        print("\nACTIVITY:")
        print(result["activity"])

        print("ALL ACTIVITIES:")
        print(result["activities"])


        # ----------------------------------------------------
        # HAZARDS
        # ----------------------------------------------------

        print("\nHAZARDS:")

        for item in result["hazards"]:

            print(
                "-",
                item["hazard"],
                "→",
                item["evidence"]
            )


        # ----------------------------------------------------
        # BARRIERS
        # ----------------------------------------------------

        print("\nBARRIERS:")

        for item in result["barriers"]:

            print(
                "-",
                item["barrier"],
                "→",
                item["evidence"]
            )


        # ----------------------------------------------------
        # LIFE-SAVING RULES
        # ----------------------------------------------------

        print("\nLIFE-SAVING RULES:")

        if result["lsr_rules"]:

            for rule in result["lsr_rules"]:

                print(
                    "-",
                    rule
                )

        else:

            print("- None")


        # ----------------------------------------------------
        # CONTRADICTION
        # ----------------------------------------------------

        print("\nCONTRADICTION DETECTED:")
        print(result["contradiction_detected"])

        if result["contradiction_reason"]:

            print("CONTRADICTION REASON:")
            print(result["contradiction_reason"])


        # ----------------------------------------------------
        # PRIMARY EVIDENCE
        # ----------------------------------------------------

        print("\nPRIMARY EVIDENCE:")

        print(result["primary_evidence"])


        print("\n")