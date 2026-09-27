import re


# ============================================================
# SAFETY CONTEXT ENGINE
# ============================================================
#
# Purpose:
#   Classify a safety report into:
#
#   1. Dangerous Condition
#   2. Control Present
#   3. Routine / Low-Potential Observation
#   4. Insufficient Information
#
# This is an advisory HSE decision-support component.
# It does NOT predict probability of injury or death.
#
# ============================================================


# ============================================================
# 1. DANGEROUS CONDITION PATTERNS
# ============================================================

DANGEROUS_PATTERNS = {

    # --------------------------------------------------------
    # ENERGY ISOLATION
    # --------------------------------------------------------

    "Energy Isolation": [

        r"not\s+(?:been\s+)?isolat(?:ed|ion)",

        r"(?:electrical\s+|energy\s+)?isolation\s+(?:had\s+not\s+been|was\s+not|is\s+not|not\s+been|has\s+not\s+been|not\s+yet|not)\s+(?:completed|verified|confirmed|done)",

        r"isolation\s+(?:was\s+)?(?:incomplete|missing|failed|omitted)",

        r"isolation\s+had\s+not\s+been\s+verified",

        r"failed\s+to\s+isolate",

        r"before\s+(?:the\s+)?(?:equipment\s+|energy\s+|electrical\s+)?isolation\s+(?:was\s+)?(?:completed|verified)",

        r"without\s+(?:proper\s+|electrical\s+|energy\s+)?isolation",

        r"without\s+(?:proper\s+)?(?:lockout|tagout|loto)",

        r"(?:loto|lockout|tagout)\s+(?:was\s+)?(?:never\s+applied|not\s+applied|was\s+not\s+completed|missing|not\s+implemented|not\s+used)",

        r"lockout\s+(?:was\s+)?not\s+(?:completed|applied|verified)",

        r"lockout/tagout\s+(?:was\s+)?not",

        r"energized\s+(?:equipment|enclosure|panel|line|system)",

        r"equipment\s+(?:remained|was)\s+energized",

        r"unexpected\s+energiz(?:ation|ing)",

        r"stored\s+(?:hydraulic\s+|electrical\s+|mechanical\s+)?pressure\s+(?:was\s+)?(?:still\s+)?present",

        r"stored\s+pressure\s+(?:was\s+)?not\s+(?:fully\s+)?released",

        r"pressure\s+(?:was\s+)?not\s+(?:fully\s+)?released",

        r"started\s+before\s+(?:confirming|verification\s+of)\s+isolation",

        r"without\s+(?:zero\s+energy|confirming\s+isolation|verifying\s+isolation)",
    ],


    # --------------------------------------------------------
    # CONFINED SPACE
    # --------------------------------------------------------

    "Confined Space": [

        r"confined\s+space.*without.*(?:gas|atmosphere|testing|monitoring)",

        r"confined\s+space.*not\s+(?:tested|checked|monitored)",

        r"entered\s+(?:a\s+)?confined\s+space\s+before",

        r"confined\s+space\s+entry\s+before",

        r"entry\s+before\s+(?:gas|atmosphere)\s+(?:testing|check)",

        r"without\s+(?:continuous\s+)?gas\s+monitoring",

        r"without\s+atmospheric\s+(?:testing|monitoring)",

        r"no\s+gas\s+monitoring",

        r"no\s+atmospheric\s+(?:testing|monitoring)",
    ],


    # --------------------------------------------------------
    # WORKING AT HEIGHT
    # --------------------------------------------------------

    "Working at Height": [

        r"without\s+(?:fall\s+protection|fall\s+arrest|harness|lifeline)",

        r"without\s+(?:wearing\s+)?(?:the\s+required\s+|a\s+)?(?:fall\s+arrest\s+)?harness",

        r"without\s+(?:a\s+)?harness",

        r"no\s+fall\s+protection",

        r"no\s+fall\s+arrest",

        r"open\s+edge.*(?:without|with\s+no).*?(?:guardrail|fall\s+protection)",

        r"(?:worked|working|worker|technician).*near\s+(?:an?\s+)?open\s+edge.*without.*(?:guardrail|fall\s+protection)",

        r"unprotected\s+(?:edge|height|platform)",

        r"working\s+at\s+height.*without",

        r"work(?:ing)?\s+at\s+height.*no\s+",

        r"started\s+work\s+at\s+height.*without",
    ],


    # --------------------------------------------------------
    # LINE OF FIRE
    # --------------------------------------------------------

    "Line of Fire": [

        r"(?:standing|entered|walked|stood|remained|working)\s+(?:below|underneath|under)\s+(?:a\s+)?(?:suspended\s+)?(?:\w+\s+)?load",

        r"(?:underneath|below|under)\s+(?:a\s+)?suspended\s+(?:\w+\s+)?load",

        r"inside\s+(?:the\s+)?(?:crane\s+)?(?:swing\s+radius|lifting\s+radius)",

        r"suspended\s+(?:\w+\s+)?load.*(?:over|above)\s+(?:personnel|workers|people)",

        r"personnel.*(?:under|below)\s+(?:a\s+)?suspended",

        r"entered\s+(?:the\s+)?line[\s-]of[\s-]fire",

        r"crossed\s+(?:(?:the|a)\s+)?line[\s-]of[\s-]fire",

        r"worker.*between.*moving.*(?:equipment|machine).*fixed",

        r"between\s+moving\s+equipment\s+and\s+(?:a\s+)?fixed\s+structure",

        r"inside\s+(?:the\s+)?line[\s-]of[\s-]fire",
    ],


    # --------------------------------------------------------
    # SAFE MECHANICAL LIFTING
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # A barricaded area is SAFE.
    #
    # Therefore this section only contains patterns that
    # explicitly indicate a failed or missing control.
    #
    # --------------------------------------------------------

    "Safe Mechanical Lifting": [

        r"(?:worker|personnel|operator|technician|entered|standing)\s+(?:below|underneath|under)\s+(?:a\s+)?suspended\s+(?:\w+\s+)?load",

        r"(?:below|underneath|under)\s+(?:a\s+)?suspended\s+(?:\w+\s+)?load",

        r"lifting.*without.*(?:exclusion|barricade|barrier)",

        r"lifting.*(?:exclusion\s+zone|barricade).*(?:not\s+(?:fully\s+)?(?:established|in\s+place|maintained|complete)|missing|absent)",

        r"crane\s+lift.*(?:not|without).*exclusion",

        r"exclusion\s+zone.*not\s+(?:fully\s+)?(?:established|maintained)",

        r"personnel.*(?:inside|within).*lifting.*(?:zone|area)",

        r"suspended\s+(?:\w+\s+)?load.*(?:over|above).*personnel",

        r"load.*moved.*over.*(?:workers|personnel|people)",

        r"suspended\s+load\s+was\s+being\s+repositioned.*(?:operator|worker|inside|crane)",

        r"crane\s+operations?.*(?:worker|personnel).*(?:beneath|under|below)",
    ],


    # --------------------------------------------------------
    # HOT WORK
    # --------------------------------------------------------

    "Hot Work": [

        r"hot\s+work.*without.*(?:permit|gas\s+test|gas\s+testing)",

        r"hot\s+work.*before.*permit",

        r"welding.*before.*permit",

        r"welding.*without.*permit",

        r"welding.*without.*gas\s+(?:test|testing)",

        r"cutting.*without.*permit",

        r"grinding.*without.*permit",

        r"gas\s+test.*not\s+(?:completed|performed)",

        r"gas\s+testing.*not\s+(?:completed|performed)",

        r"combustible.*near.*hot\s+work.*without",
    ],


    # --------------------------------------------------------
    # DRIVING / VEHICLE
    # --------------------------------------------------------

    "Driving": [

        r"vehicle.*reversing.*without.*(?:spotter|separation)",

        r"reversing\s+vehicle.*(?:close\s+to|near).*pedestrians?.*without.*(?:spotter|separation|exclusion\s+zone)",

        r"reversing.*(?:close\s+to|near).*(?:workers|pedestrians).*without.*(?:spotter|separation|exclusion\s+zone)",

        r"reversing.*near.*workers.*without",

        r"vehicle.*near.*pedestrians.*without",

        r"vehicle.*pedestrians.*(?:no|without).*separation",

        r"forklift.*pedestrian.*area.*workers",

        r"forklift.*near.*pedestrians.*without",

        r"vehicle.*movement.*without.*spotter",
    ],


    # --------------------------------------------------------
    # WORK AUTHORIZATION
    # --------------------------------------------------------

    "Work Authorization": [

        r"started.*before.*(?:work\s+)?authorization",

        r"started.*before.*permit.*approved",

        r"began.*before.*permit.*approved",

        r"work.*started.*without.*(?:work\s+)?authorization",

        r"work.*began.*without.*(?:work\s+)?authorization",

        r"contractor.*before.*(?:work\s+)?authorization",

        r"permit.*not\s+(?:approved|authorized)",

        r"work\s+authorization.*not\s+(?:confirmed|approved)",

        r"permit\s+conditions.*not\s+(?:checked|confirmed)",
    ],
}


# ============================================================
# 2. SAFE CONTROL PATTERNS
# ============================================================

SAFE_CONTROL_PATTERNS = {

    "Energy Isolation": [

        r"isolation\s+was\s+completed\s+and\s+verified",

        r"isolation\s+was\s+completed\s+and\s+confirmed",

        r"equipment\s+was\s+isolated,\s+locked\s+out,\s+and\s+verified",

        r"isolated.*locked(?:\s+out)?.*verified",

        r"isolated,\s*locked(?:\s+out)?\s*and\s*verified",

        r"de-energized,\s*locked\s*out\s*and\s*(?:independently\s+)?verified",

        r"de-energized\s+and\s+verified",

        r"locked\s+out.*and\s+verified",

        r"zero\s+energy\s+(?:was\s+)?verified",

        r"electrical\s+supply\s+(?:was\s+)?isolated\s+and\s+(?:tested|verified|locked)",

        r"properly\s+isolated",

        r"loto\s+applied",

        r"verified\s+isolation",

        r"isolation\s+confirmed",
    ],


    "Confined Space": [

        r"confined\s+space\s+was\s+tested\s+and\s+confirmed\s+safe",

        r"atmosphere\s+was\s+tested\s+and\s+confirmed\s+safe",

        r"gas\s+testing\s+was\s+completed.*before.*entry",

        r"gas\s+monitoring\s+was\s+established.*before.*entry",

        r"continuous\s+gas\s+monitoring\s+was\s+established",

        r"entry\s+was\s+authorized.*after.*testing",

        r"confined\s+space.*(?:inspected).*atmosphere\s+(?:was\s+)?tested.*entry\s+(?:was\s+)?authorized.*before.*entered",

        r"atmosphere\s+(?:was\s+)?tested.*entry\s+(?:was\s+)?authorized",
    ],


    "Working at Height": [

        r"fall\s+protection\s+was\s+inspected\s+and\s+(?:properly\s+)?secured",

        r"harness\s+was\s+inspected.*before.*work",

        r"lifeline\s+was\s+inspected.*before.*work",

        r"guardrails\s+were\s+installed\s+before",

        r"guardrail\s+was\s+installed\s+before",

        r"guardrails?\s+(?:were|was)\s+installed.*before",

        r"(?:used\s+)?(?:an\s+)?inspected\s+harness.*secured\s+(?:the\s+)?lifeline.*before.*work\s+at\s+height",
    ],


    "Safe Mechanical Lifting": [

        r"lifting\s+area\s+was\s+barricaded",

        r"lifting\s+area\s+was\s+barricaded\s+and\s+no\s+personnel",

        r"no\s+personnel\s+were\s+allowed\s+below",

        r"personnel\s+were\s+kept\s+outside.*(?:exclusion|lifting)",

        r"exclusion\s+zone\s+was\s+(?:fully\s+)?established",

        r"area\s+was\s+barricaded.*personnel.*(?:excluded|kept\s+outside)",
    ],


    "Hot Work": [

        r"hot\s+work.*after.*permit\s+was\s+approved.*gas\s+testing\s+was\s+completed",

        r"permit\s+was\s+approved.*before.*welding",

        r"gas\s+testing\s+was\s+completed.*before.*welding",

        r"hot\s+work\s+permit\s+approved.*gas\s+test.*safe",
    ],


    "Driving": [

        r"trained\s+spotter.*separation",

        r"spotter.*and.*separation",

        r"vehicle\s+operator\s+stopped\s+and\s+waited",

        r"pedestrian.*moved\s+to\s+a\s+safe\s+area",

        r"safe\s+separation\s+was\s+maintained",
    ],


    "Work Authorization": [

        r"work\s+authorization\s+was\s+approved.*permit\s+conditions\s+checked",

        r"work\s+authorization\s+approved",

        r"permit\s+was\s+approved\s+before\s+work",

        r"permit\s+conditions\s+were\s+checked.*before",

        r"authorized\s+before.*work\s+started",
    ],
}


# ============================================================
# 3. ROUTINE / LOW-POTENTIAL PATTERNS
# ============================================================

ROUTINE_PATTERNS = [

    r"minor\s+housekeeping",

    r"poor\s+housekeeping.*removed\s+immediately",

    r"small\s+amount\s+of\s+packaging.*removed",

    r"minor\s+(?:oil\s+)?spill.*cleaned(?:\s+it)?\s+immediately",

    r"minor\s+(?:oil\s+)?spill.*cleaned.*before\s+(?:anyone|personnel|workers?).*(?:entered|exposed)",

    r"slightly\s+damaged.*replaced",

    r"slightly\s+faded.*maintenance\s+was\s+requested",

    r"routine\s+inspection.*without.*significant\s+safety\s+exposure",

    r"routine\s+inspection.*no\s+significant\s+hazard",

    r"minor\s+observation",

    r"routine\s+maintenance\s+observation",

    r"routine\s+inspection.*damaged\s+handrail.*maintenance\s+request.*raised",

    r"damaged\s+handrail.*maintenance\s+request.*raised\s+immediately",
]


# ============================================================
# 4. CONTRADICTION PATTERNS
# ============================================================

CONTRADICTION_PATTERNS = [

    (
        r"(?:isolation|permit|authorization|testing|verification)"
        r".*(?:not|before)"
        r".*(?:completed|approved|verified|tested|confirmed)"
        r".*(?:but|however)"
        r".*(?:completed|approved|verified|tested|confirmed)"
    ),

    (
        r"(?:permit|authorization).*"
        r"(?:approved|authorized).*"
        r"(?:not\s+approved|not\s+authorized)"
    ),

    (
        r"isolation.*(?:completed|verified).*"
        r"(?:not\s+verified|not\s+completed)"
    ),
]


# ============================================================
# 5. FIND MATCHES
# ============================================================

def find_matches(text, patterns):

    matches = []

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE
        ):

            value = text[
                match.start():match.end()
            ].strip()

            if value and value not in matches:

                matches.append(value)

    return matches


# ============================================================
# 6. TEMPORAL DANGER DETECTION
# ============================================================

def detect_temporal_danger(text):

    temporal_patterns = [

        # Work before authorization
        r"(?:started|began|commenced).*(?:before|without).*(?:permit|authorization)",

        # Work before / while isolation failed
        r"(?:started|began|entered|opened).*(?:before|without|while).*(?:isolation|lockout|tagout|verification|loto)",

        # LOTO never applied
        r"(?:loto|lockout)\s+(?:was\s+)?never\s+applied",

        # Opening enclosure while energized
        r"opened.*(?:enclosure|panel).*(?:before|without|while).*(?:isolation|loto|lockout|energized)",

        # Entering below suspended load
        r"(?:entered|walked|stood|remained).*(?:below|underneath|under).*(?:suspended|crane)",

        # Confined space before testing
        r"entered.*confined\s+space.*before.*(?:gas|atmosphere|testing)",

        # Welding before permit
        r"(?:welding|hot\s+work).*(?:started|began|performed).*(?:before|without).*permit",

        # Lifting before exclusion zone
        r"(?:crane|lifting|lift).*(?:started|began).*(?:before|without).*exclusion\s+zone",

        # Height work without protection
        r"(?:started|began|performed).*work.*at\s+height.*without.*(?:harness|fall\s+protection)",
    ]

    return find_matches(
        text,
        temporal_patterns
    )


# ============================================================
# 7. SAFE CONTROL DETECTION
# ============================================================

def detect_safe_controls(text):

    safe_matches = []

    for category, patterns in SAFE_CONTROL_PATTERNS.items():

        matches = find_matches(
            text,
            patterns
        )

        for match in matches:

            lower_match = match.lower()

            # Do not treat phrases with negation as safe controls
            if any(neg in lower_match for neg in ["without", " not", "never", "no "]):
                continue

            safe_matches.append({
                "control": category,
                "evidence": match
            })

    return safe_matches


# ============================================================
# 8. DANGEROUS CONDITION DETECTION
# ============================================================

def detect_dangerous_conditions(text):

    dangerous_conditions = []

    # --------------------------------------------------------
    # Standard dangerous patterns
    # --------------------------------------------------------

    for category, patterns in DANGEROUS_PATTERNS.items():

        matches = find_matches(
            text,
            patterns
        )

        for match in matches:

            dangerous_conditions.append({
                "type": category,
                "evidence": match
            })


    # --------------------------------------------------------
    # Temporal dangerous patterns
    # --------------------------------------------------------

    temporal_matches = detect_temporal_danger(text)

    for match in temporal_matches:

        dangerous_conditions.append({
            "type": "Unsafe Sequence",
            "evidence": match
        })


    # --------------------------------------------------------
    # Remove duplicate entries
    # --------------------------------------------------------

    unique = []

    seen = set()

    for item in dangerous_conditions:

        key = (
            item["type"],
            item["evidence"].lower()
        )

        if key not in seen:

            seen.add(key)

            unique.append(item)

    return unique


# ============================================================
# 9. ROUTINE OBSERVATION DETECTION
# ============================================================

def detect_routine_observations(text):

    return find_matches(
        text,
        ROUTINE_PATTERNS
    )


# ============================================================
# 10. CONTRADICTION DETECTION
# ============================================================

def detect_contradictions(text):

    return find_matches(
        text,
        CONTRADICTION_PATTERNS
    )


# ============================================================
# 11. MAIN SAFETY CONTEXT ANALYZER
# ============================================================

def analyze_safety_context(text):

    # --------------------------------------------------------
    # Empty / invalid report
    # --------------------------------------------------------

    if not isinstance(text, str):

        return {
            "context": "Insufficient Information",
            "dangerous_conditions": [],
            "safe_controls": [],
            "routine_observations": [],
            "contradictions": [],
            "reason": "Invalid report text",
        }


    text = text.strip()


    if not text:

        return {
            "context": "Insufficient Information",
            "dangerous_conditions": [],
            "safe_controls": [],
            "routine_observations": [],
            "contradictions": [],
            "reason": "Empty report",
        }


    # --------------------------------------------------------
    # Detect all evidence
    # --------------------------------------------------------

    dangerous_conditions = detect_dangerous_conditions(text)

    safe_controls = detect_safe_controls(text)

    routine_observations = detect_routine_observations(text)

    contradictions = detect_contradictions(text)


    # ========================================================
    # PRIORITY 1 — CONTRADICTION
    # ========================================================

    if contradictions:

        return {
            "context": "Insufficient Information",

            "dangerous_conditions":
                dangerous_conditions,

            "safe_controls":
                safe_controls,

            "routine_observations":
                routine_observations,

            "contradictions":
                contradictions,

            "reason":
                "Contradictory Information",
        }


    # ========================================================
    # PRIORITY 2 — DANGEROUS CONDITION
    # ========================================================
    #
    # Dangerous evidence takes priority over generic words
    # such as "permit", "testing", "barricade", etc.
    #
    # Example:
    #
    # Welding started BEFORE permit approval
    #
    # = Dangerous
    #
    # ========================================================

    if dangerous_conditions:

        return {
            "context": "Dangerous Condition",

            "dangerous_conditions":
                dangerous_conditions,

            "safe_controls":
                safe_controls,

            "routine_observations":
                routine_observations,

            "contradictions":
                contradictions,

            "reason":
                "Potential SIF precursor identified",
        }


    # ========================================================
    # PRIORITY 3 — SAFE CONTROL
    # ========================================================

    if safe_controls:

        return {
            "context": "Control Present",

            "dangerous_conditions":
                dangerous_conditions,

            "safe_controls":
                safe_controls,

            "routine_observations":
                routine_observations,

            "contradictions":
                contradictions,

            "reason":
                "Safety control explicitly confirmed",
        }


    # ========================================================
    # PRIORITY 4 — ROUTINE / LOW POTENTIAL
    # ========================================================

    if routine_observations:

        return {
            "context":
                "Routine / Low-Potential Observation",

            "dangerous_conditions":
                dangerous_conditions,

            "safe_controls":
                safe_controls,

            "routine_observations":
                routine_observations,

            "contradictions":
                contradictions,

            "reason":
                "Routine or low-potential observation",
        }


    # ========================================================
    # PRIORITY 5 — INSUFFICIENT INFORMATION
    # ========================================================

    return {
        "context":
            "Insufficient Information",

        "dangerous_conditions":
            dangerous_conditions,

        "safe_controls":
            safe_controls,

        "routine_observations":
            routine_observations,

        "contradictions":
            contradictions,

        "reason":
            "Insufficient information to establish hazard exposure and barrier condition.",
    }


# ============================================================
# 12. MANUAL TEST
# ============================================================

if __name__ == "__main__":

    test_cases = [

        # ----------------------------------------------------
        # DANGEROUS CASES
        # ----------------------------------------------------

        "Electrical isolation was not completed before maintenance started.",

        "A worker entered the maintenance area after energy isolation had not been verified.",

        "During maintenance, stored hydraulic pressure was still present.",

        "A worker entered a confined space before atmosphere testing.",

        "A worker climbed an elevated platform without fall arrest harness.",

        "A worker was standing below a suspended load during crane lifting operations.",

        "Welding started before the hot-work permit was approved.",

        "A contractor began work before work authorization was confirmed.",

        "A crane lift started while the exclusion zone was not fully established.",


        # ----------------------------------------------------
        # SAFE CONTROL CASES
        # ----------------------------------------------------

        "Electrical isolation was completed and verified before maintenance began.",

        "The confined space was tested and confirmed safe before authorized entry.",

        "The lifting area was barricaded and no personnel were allowed below the suspended load.",

        "Hot work was performed after the permit was approved and gas testing was completed.",

        "Fall protection was inspected and properly secured before the worker started work at height.",

        "The vehicle operator stopped and waited until the pedestrian moved to a safe area.",

        "The equipment was isolated, locked out, and verified before maintenance.",


        # ----------------------------------------------------
        # ROUTINE CASES
        # ----------------------------------------------------

        "A minor housekeeping observation was recorded during the daily inspection.",

        "A worker noticed a minor spill and cleaned it immediately.",


        # ----------------------------------------------------
        # REVIEW CASES
        # ----------------------------------------------------

        "An unsafe condition was observed near the equipment during maintenance.",

        "A worker entered the area with no details about the work activity.",

        "The permit information was conflicting and unclear.",
    ]


    print("\n" + "=" * 70)

    print("SAFETY CONTEXT ENGINE TEST")

    print("=" * 70)


    for i, report in enumerate(test_cases, 1):

        result = analyze_safety_context(report)

        print(f"\nTEST {i}")

        print("-" * 70)

        print("REPORT :", report)

        print("CONTEXT:", result["context"])

        print("REASON :", result.get("reason"))


        if result["dangerous_conditions"]:

            print(
                "DANGER :",
                result["dangerous_conditions"]
            )


        if result["safe_controls"]:

            print(
                "CONTROL:",
                result["safe_controls"]
            )


        if result["routine_observations"]:

            print(
                "ROUTINE:",
                result["routine_observations"]
            )


        if result["contradictions"]:

            print(
                "CONFLICT:",
                result["contradictions"]
            )