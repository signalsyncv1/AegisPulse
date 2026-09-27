# SIF Intelligence Platform

AI-assisted safety intelligence for detecting Serious Injury and Fatality (SIF) precursors from unstructured safety reports.

## Overview

SIF Intelligence Platform analyzes free-text unsafe-act, unsafe-condition, near-miss, and incident reports and converts them into structured HSE intelligence.

The platform helps identify:

- SIF-potential and Non-SIF-potential reports
- reports requiring human review
- operational activities
- high-consequence hazards
- critical safety barriers
- barrier conditions
- relevant Life-Saving Rules
- recurring precursor patterns
- site and activity SIF-precursor density
- HSE intervention hotspots

The system is designed as AI-assisted HSE decision support and not as an autonomous safety authority.

## Key Features

### Report Analyzer

Analyze a single free-text safety report and obtain:

- ML Classification
- Final Safety Decision
- Priority
- Activity
- Hazard
- Critical Barrier
- Barrier Condition
- Life-Saving Rule
- Evidence
- Potential Consequence
- Recommended Action
- Internal Classifier Score

### Batch Analysis

Upload CSV safety-report datasets for bulk analysis and export the resulting structured safety intelligence.

Supported narrative columns include:

- `text`
- `report_text`
- `description`
- `narrative`

Optional metadata includes:

- `report_id`
- `site`

### Site & Activity Risk

Ranks operational sites and activities using SIF-precursor density.

SIF Precursor Density:

```text
SIF-Potential Reports
--------------------- × 100
Total Reports