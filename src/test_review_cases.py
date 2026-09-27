from analyze_report import analyze_report


TEST_CASES = [
    {
        "id": "T001",
        "text": "An unsafe condition was observed near the equipment during maintenance."
    },
    {
        "id": "T002",
        "text": "Isolation was completed, but it was not verified before maintenance began."
    },
    {
        "id": "T003",
        "text": "Electrical isolation was not completed before maintenance started."
    },
    {
        "id": "T004",
        "text": "Electrical isolation was completed and verified before maintenance."
    },
    {
        "id": "T005",
        "text": "A worker was standing below a suspended load during crane lifting operations."
    },
]


def main():

    print("\n" + "=" * 70)
    print("             NEEDS REVIEW TEST CASES")
    print("=" * 70)

    for case in TEST_CASES:

        result = analyze_report(case["text"])

        print("\n" + "-" * 70)
        print(f"Test ID : {case['id']}")
        print(f"Report  : {case['text']}")

        print(f"\nFinal Result : {result['final_result']}")
        print(f"Context      : {result.get('context')}")
        print(f"Activity     : {result.get('activity')}")
        print(f"Hazard       : {result.get('hazard')}")
        print(f"Barrier      : {result.get('barrier')}")
        print(f"LSR          : {result.get('lsr_rules')}")
        print(f"Evidence     : {result.get('primary_evidence')}")


if __name__ == "__main__":
    main()