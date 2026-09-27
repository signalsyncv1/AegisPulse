import sys
from pathlib import Path

# Add src to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analyze_report import analyze_report


def test_case_1_sif():
    """Case 1: SIF candidate - dangerous isolation condition with clear evidence."""
    narrative = (
        "During pump maintenance, the technician entered the equipment area "
        "while electrical isolation had not been completed. No injury occurred."
    )
    result = analyze_report(narrative)
    assert result["final_result"] == "SIF Potential", f"Expected SIF Potential, got {result['final_result']}"
    assert "Energy Isolation" in result["lsr_rules"], f"Expected Energy Isolation in LSR, got {result['lsr_rules']}"
    assert result["hazard"] == "Unexpected Energization", f"Expected Unexpected Energization, got {result['hazard']}"
    assert result["barrier_condition"] == "Incomplete / Failed"
    assert result["primary_evidence"] is not None
    assert "isolation had not been completed" in result["primary_evidence"].lower()
    assert result["priority"] == "High"


def test_case_2_non_sif():
    """Case 2: Non-SIF - verified safe isolation control present."""
    narrative = "The electrical supply was isolated, locked and verified before the maintenance activity began."
    result = analyze_report(narrative)
    assert result["final_result"] == "Non-SIF Potential", f"Expected Non-SIF Potential, got {result['final_result']}"
    assert result["barrier_condition"] == "Intact / Verified"
    assert result["lsr_rules"] == []
    assert result["priority"] == "Low"


def test_case_3_needs_review():
    """Case 3: Insufficient information to establish hazard or barrier condition."""
    narrative = "Pump maintenance issue was observed."
    result = analyze_report(narrative)
    assert result["final_result"] == "Needs Review", f"Expected Needs Review, got {result['final_result']}"
    assert result["review_reason"] == "Insufficient information to establish hazard exposure and barrier condition."
    assert result["barrier_condition"] == "Uncertain / Unspecified"


def test_case_4_multi_lsr():
    """Case 4: Multi-label Life-Saving Rule detection (Line of Fire + Safe Mechanical Lifting)."""
    narrative = "A worker entered below a suspended crane load while lifting operations were underway."
    result = analyze_report(narrative)
    assert result["final_result"] == "SIF Potential", f"Expected SIF Potential, got {result['final_result']}"
    assert "Line of Fire" in result["lsr_rules"], f"Expected Line of Fire in LSR, got {result['lsr_rules']}"
    assert "Safe Mechanical Lifting" in result["lsr_rules"], f"Expected Safe Mechanical Lifting in LSR, got {result['lsr_rules']}"
    assert result["hazard"] == "Suspended Load / Struck-by"
    assert result["barrier_condition"] == "Incomplete / Failed"


def test_paraphrase_failed_loto():
    """Generalized test: LOTO never applied."""
    narrative = "LOTO was never applied before the technician opened the electrical enclosure."
    result = analyze_report(narrative)
    assert result["final_result"] == "SIF Potential"
    assert "Energy Isolation" in result["lsr_rules"]


def test_paraphrase_controlled_loto():
    """Generalized test: De-energized, locked and independently verified."""
    narrative = "Equipment was de-energized, locked out and independently verified before work started."
    result = analyze_report(narrative)
    assert result["final_result"] == "Non-SIF Potential"
    assert result["barrier_condition"] == "Intact / Verified"


def test_paraphrase_crane_swing_radius():
    """Generalized test: Standing inside crane swing radius during repositioning."""
    narrative = "An operator stood inside the crane swing radius while a suspended load was being repositioned."
    result = analyze_report(narrative)
    assert result["final_result"] == "SIF Potential"
    assert "Line of Fire" in result["lsr_rules"]
    assert "Safe Mechanical Lifting" in result["lsr_rules"]


def test_paraphrase_vague_observation():
    """Generalized test: Vague statement requires review."""
    narrative = "An issue was noticed near the compressor."
    result = analyze_report(narrative)
    assert result["final_result"] == "Needs Review"


def test_contradiction_handling():
    """Contradictory reports flag Needs Review."""
    narrative = "Isolation was completed, but it was not verified before maintenance began."
    result = analyze_report(narrative)
    assert result["final_result"] == "Needs Review"
    assert result["contradiction_detected"] is True


def test_schema_completeness():
    """Verify all standard and enriched fields are returned."""
    narrative = "Worker entered confined space without atmospheric gas testing."
    result = analyze_report(narrative)
    required_keys = [
        "final_result", "model_score", "priority", "activity",
        "hazard", "barrier", "barrier_condition", "lsr_rules",
        "primary_evidence", "potential_consequence", "recommended_action",
        "context", "ml_prediction"
    ]
    for key in required_keys:
        assert key in result, f"Missing key in result schema: {key}"


if __name__ == "__main__":
    print("\nRunning Safety Intelligence Regression Tests...\n")
    tests = [
        test_case_1_sif,
        test_case_2_non_sif,
        test_case_3_needs_review,
        test_case_4_multi_lsr,
        test_paraphrase_failed_loto,
        test_paraphrase_controlled_loto,
        test_paraphrase_crane_swing_radius,
        test_paraphrase_vague_observation,
        test_contradiction_handling,
        test_schema_completeness
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  [PASS] {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {t.__name__}: {e}")
    print(f"\nCompleted: {passed}/{len(tests)} tests passed successfully.\n")
