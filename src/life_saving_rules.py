import re


# ============================================================
# IOGP LIFE-SAVING RULES
# ============================================================

LSR_PATTERNS = {

    "Bypassing Safety Controls": [
        r"bypass(ed|ing)? safety",
        r"safety control.*bypass",
        r"bypassed.*interlock",
        r"interlock.*bypass",
        r"defeated.*safety",
        r"disabled.*safety",
    ],

    "Confined Space": [
        r"confined space.*without",
        r"entered.*confined space.*without",
        r"without.*atmospheric testing",
        r"without.*gas monitoring",
        r"without.*gas testing",
    ],

    "Driving": [
        r"vehicle.*reversing.*near workers",
        r"reversing\s+vehicle.*(?:close\s+to|near).*pedestrians?",
        r"reversing.*(?:workers|pedestrians).*without.*(?:spotter|separation|exclusion\s+zone)",
        r"reversing near workers",
        r"vehicle.*workers.*without",
        r"driving.*without",
        r"pedestrian.*vehicle",
    ],

    "Energy Isolation": [
        r"isolation\s+(?:had\s+not\s+been|was\s+not|is\s+not|not\s+been|not\s+yet|not)\s+(?:completed|verified|confirmed)",
        r"isolation was not completed",
        r"isolation not completed",
        r"isolation had not been verified",
        r"not been isolated",
        r"without isolation",
        r"failed to isolate",
        r"not fully isolated",
        r"(?:loto|lockout)\s+(?:was\s+)?never\s+applied",
        r"loto\s+not\s+applied",
        r"stored pressure was not",
        r"stored\s+(?:hydraulic|pneumatic|mechanical|electrical)\s+(?:pressure|energy).*?(?:still\s+)?present",
        r"hydraulic\s+pressure.*(?:still\s+)?present",
        r"pressure was not fully released",
        r"locked out.*before.*not",
        r"lockout.*not",
    ],

    "Hot Work": [
        r"hot work.*without",
        r"hot work.*not.*permit",
        r"hot work.*without.*gas testing",
        r"without.*gas testing.*hot work",
    ],

    "Line of Fire": [
        r"line of fire",
        r"line-of-fire",
        r"(?:standing|entered|walked|stood|remained|working)\s+(?:below|underneath|under)\s+(?:a\s+)?(?:suspended\s+)?(?:\w+\s+)?load",
        r"(?:underneath|below|under)\s+(?:a\s+)?suspended\s+(?:\w+\s+)?load",
        r"inside\s+(?:the\s+)?(?:crane\s+)?(?:swing\s+radius|lifting\s+radius)",
        r"crossed.*line.of.fire",
        r"crossed.*line-of-fire",
        r"crossed\s+(?:(?:the|a)\s+)?line[\s-]of[\s-]fire",
        r"heavy equipment.*near.*worker",
    ],

    "Safe Mechanical Lifting": [
        r"(?:worker|personnel|operator|technician|entered|standing)\s+(?:below|underneath|under)\s+(?:a\s+)?suspended\s+(?:\w+\s+)?load",
        r"(?:below|underneath|under)\s+(?:a\s+)?suspended\s+(?:\w+\s+)?load",
        r"worker.*below.*suspended load",
        r"worker.*underneath.*suspended load",
        r"standing below.*suspended load",
        r"personnel.*below.*suspended load",
        r"personnel.*underneath.*suspended load",
        r"lifting operation.*without",
        r"crane lifting.*without",
        r"suspended\s+load\s+was\s+being\s+repositioned",
        r"crane\s+operations?.*(?:worker|personnel).*(?:beneath|under|below)",
    ],

    "Work Authorization": [
        r"work permit.*not",
        r"permit was not",
        r"without.*permit",
        r"permit.*not.*approved",
        r"work authorization.*not",
        r"(?:started|began|commenced).*before.*(?:work\s+)?authorization.*(?:confirmed|approved)",
        r"contractor.*before.*(?:required\s+)?work\s+authorization.*(?:confirmed|approved)",
        r"authorization was not",
    ],

    "Working at Height": [
        r"working at height.*without",
        r"work at height.*without",
        r"without fall protection",
        r"without proper fall protection",
        r"without\s+(?:wearing\s+)?(?:the\s+required\s+|a\s+)?(?:fall\s+arrest\s+)?harness",
        r"open\s+edge.*without.*(?:guardrail|fall\s+protection)",
        r"no fall protection",
        r"fall protection.*not provided",
    ],
}


# ============================================================
# SAFE / CONTROLLED CONDITIONS
# ============================================================

SAFE_PATTERNS = [

    r"isolation was completed",
    r"isolation was completed and verified",
    r"isolated.*locked(?:\s+out)?.*verified",
    r"isolated,\s*locked(?:\s+out)?\s*and\s*verified",
    r"de-energized,\s*locked\s*out\s*and\s*(?:independently\s+)?verified",
    r"de-energized\s+and\s+verified",
    r"electrical\s+supply\s+(?:was\s+)?isolated",

    r"confined space was tested",
    r"confined\s+space.*atmosphere\s+(?:was\s+)?tested.*entry\s+(?:was\s+)?authorized",
    r"atmosphere\s+(?:was\s+)?tested.*entry\s+(?:was\s+)?authorized",
    r"confirmed safe before authorized entry",

    r"area was barricaded",
    r"no personnel were allowed below",

    r"permit was approved",
    r"gas testing was completed",

    r"fall protection was inspected",
    r"fall protection was properly secured",
    r"inspected\s+harness.*secured\s+(?:the\s+)?lifeline",
    r"guardrails?\s+(?:were|was)\s+installed.*before",

    r"stopped and waited until",
]


# ============================================================
# FIND EVIDENCE
# ============================================================

def find_matches(text, patterns):

    matches = []

    text_lower = text.lower()

    for pattern in patterns:

        for match in re.finditer(pattern, text_lower):

            evidence = text[
                match.start():match.end()
            ]

            matches.append(evidence)

    return list(dict.fromkeys(matches))


# ============================================================
# CHECK SAFE CONTROL
# ============================================================

def has_safe_control(text):

    return len(
        find_matches(
            text,
            SAFE_PATTERNS
        )
    ) > 0


# ============================================================
# DETECT LIFE-SAVING RULES
# ============================================================

def detect_life_saving_rules(text):

    detected_rules = []

    evidence_by_rule = {}

    safe_control_present = has_safe_control(text)

    # --------------------------------------------------------
    # If a clear safe control is present,
    # do not classify the report as an LSR violation.
    # --------------------------------------------------------

    if safe_control_present:

        return {
            "lsr_rules": [],
            "lsr_evidence": {},
            "safe_control_present": True
        }

    # --------------------------------------------------------
    # Detect dangerous LSR conditions
    # --------------------------------------------------------

    for rule, patterns in LSR_PATTERNS.items():

        matches = find_matches(
            text,
            patterns
        )

        if matches:

            detected_rules.append(rule)

            evidence_by_rule[rule] = matches

    return {
        "lsr_rules": detected_rules,
        "lsr_evidence": evidence_by_rule,
        "safe_control_present": False
    }


# ============================================================
# TEST THE RULE ENGINE
# ============================================================

if __name__ == "__main__":

    test_reports = [

        (
            "During pump maintenance, electrical isolation "
            "was not completed before the technician entered "
            "the equipment area."
        ),

        (
            "A worker entered a confined space without "
            "confirming atmospheric testing and gas monitoring."
        ),

        (
            "A worker was standing below a suspended load "
            "during crane lifting operations."
        ),

        (
            "A worker was working at height without "
            "proper fall protection."
        ),

        (
            "Electrical isolation was completed and verified "
            "before maintenance began."
        ),

        (
            "Hot work was performed after the permit was "
            "approved and gas testing was completed."
        ),

        (
            "The lifting area was barricaded and no personnel "
            "were allowed below the suspended load."
        )
    ]


    for report in test_reports:

        print("=" * 70)

        print("REPORT:")
        print(report)

        print()

        result = detect_life_saving_rules(report)

        print("Life-Saving Rules:")

        if result["lsr_rules"]:

            for rule in result["lsr_rules"]:

                print("-", rule)

        else:

            print("- None")

        print()

        print("Evidence:")

        if result["lsr_evidence"]:

            for rule, evidence_list in result[
                "lsr_evidence"
            ].items():

                print(rule, ":")

                for evidence in evidence_list:

                    print("   →", evidence)

        else:

            print("- None")

        print()

        print(
            "Safe Control Present:",
            result["safe_control_present"]
        )

        print()