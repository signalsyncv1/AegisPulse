import re


# =========================================================
# HAZARD PATTERNS
# =========================================================

HAZARD_PATTERNS = {

    "Unexpected Energization": [
        r"electrical isolation",
        r"energy isolation",
        r"isolation had not been verified",
        r"isolation was not completed",
        r"isolation",
        r"not been isolated",
        r"failed to isolate",
        r"stored pressure",
        r"stored\s+(?:hydraulic|pneumatic|mechanical|electrical)\s+(?:pressure|energy)",
        r"hydraulic\s+pressure.*(?:still\s+)?present",
        r"pressure was not fully released",
        r"locked out",
        r"lockout",
        r"loto",
        r"tagout",
        r"de-energiz\w+",
        r"energized",
        r"electrical\s+(?:enclosure|panel|supply|point)",
        r"unexpected energization",
    ],

    "Fall from Height": [
        r"working at height",
        r"work at height",
        r"elevated\s+platform",
        r"open\s+edge",
        r"without.*fall\s+protection",
        r"fall protection",
        r"fall\s+arrest\s+harness",
        r"harness",
        r"guardrail",
        r"lifeline",
    ],

    "Suspended Load / Struck-by": [
        r"suspended.*load",
        r"crane.*load",
        r"standing below.*suspended load",
        r"underneath.*suspended load",
        r"below.*suspended load",
        r"below.*load",
        r"lifting operation",
        r"crane lifting",
        r"crane\s+operations?",
        r"crane\s+(?:swing\s+)?radius",
    ],

    "Confined Space Exposure": [
        r"confined space",
        r"entered a confined space",
        r"confined space entry",
    ],

    "Hot Work Exposure": [
        r"hot work",
        r"welding",
        r"cutting",
        r"grinding",
    ],

    "Vehicle / Pedestrian Interaction": [
        r"vehicle was reversing",
        r"reversing\s+vehicle",
        r"reversing.*(?:workers|pedestrians)",
        r"vehicle.*(?:workers|pedestrians)",
        r"pedestrian.*vehicle",
        r"vehicle movement",
        r"driver",
        r"vehicle operator",
    ],

    "Line-of-Fire Exposure": [
        r"line.of.fire",
        r"line-of-fire",
        r"crossed.*line.of.fire",
        r"heavy equipment.*near",
        r"equipment.*operating nearby",
        r"swing\s+radius",
    ],
}


# =========================================================
# BARRIER PATTERNS
# =========================================================

BARRIER_PATTERNS = {

    "Energy Isolation": [
        r"electrical isolation",
        r"energy isolation",
        r"isolation had not been verified",
        r"isolation was not completed",
        r"not been isolated",
        r"stored pressure",
        r"stored\s+(?:hydraulic|pneumatic|mechanical|electrical)\s+(?:pressure|energy)",
        r"hydraulic\s+pressure.*(?:still\s+)?present",
        r"pressure was not fully released",
        r"locked out",
        r"lockout",
        r"loto",
        r"tagout",
        r"de-energiz\w+",
        r"isolation",
    ],

    "Fall Protection": [
        r"fall protection",
        r"fall\s+arrest",
        r"harness",
        r"lifeline",
        r"guardrails?",
        r"open\s+edge",
    ],

    "Gas Testing / Atmospheric Monitoring": [
        r"gas testing",
        r"gas monitoring",
        r"atmospheric testing",

        # Confined-space reports may describe the
        # control as "tested" rather than "gas testing".
        r"confined space.*tested",
        r"tested.*confined space",
        r"confirmed safe.*authorized entry",
    ],

    "Lifting Exclusion Zone": [
        r"(?:lifting|crane).*exclusion\s+zone",
        r"exclusion\s+zone.*(?:lifting|crane|suspended\s+load)",
        r"lifting\s+area.*barricad",
        r"(?:lifting|crane).*barricad",
        r"no\s+personnel.*(?:below|under).*(?:load|lifting)",
        r"suspended.*load",
        r"crane\s+(?:swing\s+)?radius",
        r"below.*load",
        r"underneath.*load",
        r"lifting.*operation",
        r"crane.*lifting",
    ],

    "Work Permit": [
        r"work permit",
        r"permit",
        r"work authorization",
    ],

    "Vehicle Separation / Spotter": [
        r"spotter",
        r"(?:vehicle|reversing).*separation",
        r"(?:vehicle|reversing).*exclusion\s+zone",
        r"pedestrian.*separation",
        r"safe area",
        r"stopped and waited",
    ],

    "Line-of-Fire Separation": [
        r"line.of.fire",
        r"line-of-fire",
        r"safe distance",
        r"swing\s+radius",
    ],
}


# =========================================================
# FIND ALL MATCHES
# =========================================================

def find_matches(text, patterns):

    matches = []

    text_lower = text.lower()

    for pattern in patterns:

        for match in re.finditer(pattern, text_lower):

            evidence = text[
                match.start():match.end()
            ]

            matches.append(evidence)

    # Remove duplicate evidence
    return list(dict.fromkeys(matches))


# =========================================================
# DETECT MULTIPLE HAZARDS
# =========================================================

def detect_hazards(text):

    detected = []

    priority_order = [

        "Hot Work Exposure",

        "Confined Space Exposure",

        "Unexpected Energization",

        "Fall from Height",

        "Suspended Load / Struck-by",

        "Vehicle / Pedestrian Interaction",

        "Line-of-Fire Exposure",
    ]

    for hazard in priority_order:

        matches = find_matches(
            text,
            HAZARD_PATTERNS[hazard]
        )

        if matches:

            detected.append({
                "hazard": hazard,
                "evidence": matches
            })

    if detected:
        return detected

    return [
        {
            "hazard": "Unknown",
            "evidence": []
        }
    ]


# =========================================================
# DETECT PRIMARY HAZARD
# =========================================================

def detect_hazard(text):

    hazards = detect_hazards(text)

    primary = hazards[0]

    return {

        "hazard": primary["hazard"],

        "evidence": (
            primary["evidence"][0]
            if primary["evidence"]
            else None
        ),

        "hazards": hazards
    }


# =========================================================
# DETECT MULTIPLE BARRIERS
# =========================================================

def detect_barriers(text):

    detected = []

    for barrier, patterns in BARRIER_PATTERNS.items():

        matches = find_matches(
            text,
            patterns
        )

        if matches:

            detected.append({
                "barrier": barrier,
                "evidence": matches
            })

    if detected:
        return detected

    return [
        {
            "barrier": "Unknown",
            "evidence": []
        }
    ]


# =========================================================
# DETECT PRIMARY BARRIER
# =========================================================

def detect_barrier(text):

    barriers = detect_barriers(text)

    primary = barriers[0]

    return {

        "barrier": primary["barrier"],

        "evidence": (
            primary["evidence"][0]
            if primary["evidence"]
            else None
        ),

        "barriers": barriers
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    test_reports = [

        # Hot Work
        "Hot work was performed after the permit was approved and gas testing was completed.",

        # Confined Space
        "The confined space was tested and confirmed safe before authorized entry.",

        # Energy Isolation
        "The equipment was isolated, locked out, and verified before maintenance.",

        # Vehicle
        "A vehicle was reversing near workers without adequate separation or spotter control.",

        # Lifting
        "A worker was standing below a suspended load during crane lifting operations.",
    ]


    for report in test_reports:

        print("=" * 70)

        print("REPORT:")
        print(report)

        print()

        # -----------------------------------------------
        # HAZARDS
        # -----------------------------------------------

        hazards = detect_hazards(report)

        print("HAZARDS:")

        for item in hazards:

            print(
                "-",
                item["hazard"],
                "→",
                item["evidence"]
            )

        print()

        # -----------------------------------------------
        # BARRIERS
        # -----------------------------------------------

        barriers = detect_barriers(report)

        print("BARRIERS:")

        for item in barriers:

            print(
                "-",
                item["barrier"],
                "→",
                item["evidence"]
            )

        print()