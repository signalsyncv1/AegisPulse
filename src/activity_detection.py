import re


# ==========================================
# ACTIVITY PATTERNS
# ==========================================

ACTIVITY_PATTERNS = {

    "Pump Maintenance": [
        r"pump maintenance",
        r"maintenance of pump",
        r"pump repair",
        r"pump servicing",
    ],

    "Electrical Maintenance": [
        r"electrical maintenance",
        r"electrical work",
        r"electrical repair",
        r"electrical equipment",
        r"electrical isolation",
    ],

    "Confined Space Entry": [
        r"confined space",
        r"entered a confined space",
        r"confined space entry",
        r"entry into confined space",
    ],

    "Crane / Lifting Operation": [
        r"crane lifting",
        r"crane operation",
        r"lifting operation",
        r"lifting operations",
        r"suspended load",
        r"mechanical lifting",
    ],

    "Hot Work": [
        r"hot work",
        r"welding",
        r"cutting",
        r"grinding",
        r"hot work permit",
    ],

    "Working at Height": [
        r"working at height",
        r"work at height",
        r"height work",
        r"fall protection",
        r"harness",
        r"lifeline",
    ],

    "Driving / Vehicle Movement": [
        r"driving",
        r"vehicle movement",
        r"vehicle was",
        r"vehicle",
        r"reversing",
        r"reverse movement",
        r"driver",
        r"pedestrian",
    ],

    "Heavy Equipment Operation": [
        r"heavy equipment",
        r"heavy machinery",
        r"equipment was operating",
        r"equipment operating",
    ],

    "General Maintenance": [
        r"general maintenance",
        r"routine maintenance",
        r"routine repair",
        r"general repair",
        r"routine servicing",
        r"during maintenance",
        r"maintenance area",
    ],
}


# ==========================================
# ACTIVITY PRIORITY
# ==========================================

ACTIVITY_PRIORITY = [

    "Pump Maintenance",

    "Confined Space Entry",

    "Crane / Lifting Operation",

    "Hot Work",

    "Working at Height",

    "Driving / Vehicle Movement",

    "Heavy Equipment Operation",

    "Electrical Maintenance",

    "General Maintenance",
]


# ==========================================
# ACTIVITY DETECTION
# ==========================================

def detect_activity(text):

    text_lower = text.lower()

    detected_activities = []

    evidence_by_activity = {}


    for activity in ACTIVITY_PRIORITY:

        patterns = ACTIVITY_PATTERNS[activity]

        matches = []


        for pattern in patterns:

            for match in re.finditer(
                pattern,
                text_lower
            ):

                evidence = text[
                    match.start():match.end()
                ]

                matches.append(evidence)


        unique_matches = list(
            dict.fromkeys(matches)
        )


        if unique_matches:

            detected_activities.append(
                activity
            )

            evidence_by_activity[
                activity
            ] = unique_matches


    if detected_activities:

        primary_activity = (
            detected_activities[0]
        )

    else:

        primary_activity = "Unknown"


    return {

        "activity": primary_activity,

        "activities": detected_activities,

        "activity_evidence":
            evidence_by_activity
    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    test_reports = [

        "A worker entered the maintenance area after energy isolation had not been verified.",

        "During maintenance, stored pressure was not fully released before work started.",

        "A worker crossed a line-of-fire area while heavy equipment was operating nearby.",

    ]


    for report in test_reports:

        print("=" * 70)

        print("REPORT:")
        print(report)

        print()

        result = detect_activity(report)

        print(
            "Primary Activity:",
            result["activity"]
        )

        print()

        print("All Detected Activities:")

        for activity in result["activities"]:

            print(
                "-",
                activity
            )

        print()

        print("Activity Evidence:")

        for activity, evidence_list in (
            result["activity_evidence"].items()
        ):

            print(
                activity,
                ":"
            )

            for evidence in evidence_list:

                print(
                    "   →",
                    evidence
                )

        print()