import ast
import sys
from pathlib import Path
from typing import Any, List
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import plotly.io as pio

pio.templates.default = "plotly_white"

def improve_chart_contrast(fig):
    """Apply a consistent high-contrast light theme to Plotly charts."""
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            color="#111827",
            size=13,
        ),
        title_font=dict(
            color="#111827",
            size=16,
        ),
        legend=dict(
            font=dict(color="#111827")
        ),
        margin=dict(l=20, r=20, t=40, b=20),
    )

    fig.update_xaxes(
        tickfont=dict(color="#334155", size=12),
        title_font=dict(color="#111827", size=13),
        linecolor="#CBD5E1",
        gridcolor="#E5E7EB",
        zerolinecolor="#CBD5E1",
    )

    fig.update_yaxes(
        tickfont=dict(color="#334155", size=12),
        title_font=dict(color="#111827", size=13),
        linecolor="#CBD5E1",
        gridcolor="#E5E7EB",
        zerolinecolor="#CBD5E1",
    )

    return fig

# ======================================================
# BACKEND ADAPTER IMPORT (ZERO MOCK DATA)
# ======================================================

CURRENT_DIR = Path(__file__).resolve().parent

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from src.backend_adapter import (  # noqa: E402
    analyze_single_report,
    analyze_batch_reports,
    get_reports,
    get_dashboard_summary,
    get_site_density,
    get_activity_density,
    get_site_activity_hotspots,
    get_life_saving_rule_summary,
    get_precursor_patterns,
    get_review_queue,
)


# ======================================================
# PAGE CONFIGURATION
# ======================================================

st.set_page_config(
    page_title="SIF Precursor Intelligence | HSE AI Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>

/* ================================
   GLOBAL APP STYLING
================================ */
html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif;
}

.stApp {
    background-color: #f5f7fb;
    color: #111827;
}

/* Main content spacing */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}

/* ================================
   HEADERS / TITLES
================================ */
h1, h2, h3, h4, h5, h6 {
    color: #111827 !important;
    font-weight: 700 !important;
}

p, label, span, div {
    color: #111827;
}

/* ================================
   SIDEBAR
================================ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border-right: 1px solid #e5e7eb;
}

section[data-testid="stSidebar"] * {
    color: #111827 !important;
}

/* ================================
   GENERIC CARD CONTAINER
================================ */
.custom-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 1rem 1.2rem;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
    color: #111827;
}

.metric-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 1rem 1.2rem;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
    color: #111827;
}

/* ================================
   INPUTS / TEXT BOXES / TEXT AREA
================================ */
input, textarea {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
}

input::placeholder,
textarea::placeholder {
    color: #6b7280 !important;
}

/* Streamlit text input */
div[data-testid="stTextInput"] input {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
    padding: 0.7rem 0.9rem !important;
    box-shadow: none !important;
}

/* Streamlit text area */
div[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 14px !important;
    padding: 0.8rem 0.9rem !important;
    min-height: 120px !important;
    box-shadow: none !important;
}

/* Number input */
div[data-testid="stNumberInput"] input {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
}

/* ================================
   SELECT BOX / MULTISELECT
================================ */
div[data-testid="stSelectbox"] > div {
    background: transparent !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
}

div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
}

/* dropdown text */
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: #111827 !important;
}

/* ================================
   FILE UPLOADER
================================ */
div[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 1px dashed #cbd5e1 !important;
    border-radius: 16px !important;
    padding: 1rem !important;
    color: #111827 !important;
}

div[data-testid="stFileUploader"] * {
    color: #111827 !important;
}

/* ================================
   BUTTONS
================================ */
button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1rem !important;
}

button[kind="secondary"] {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

/* ALL streamlit buttons */
.stButton > button {
    border-radius: 12px !important;
    padding: 0.65rem 1rem !important;
    font-weight: 600 !important;
    border: none !important;
}

/* red action button if you want */
.danger-btn button {
    background: #ef4444 !important;
    color: white !important;
}

/* ================================
   TABS
================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px 10px 0 0;
    color: #111827 !important;
    padding: 10px 16px;
}

.stTabs [aria-selected="true"] {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    border-bottom: 2px solid #2563eb !important;
}

/* ================================
   TABLES / DATAFRAMES
================================ */
div[data-testid="stDataFrame"] {
    background: #ffffff !important;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 0.4rem;
}

table {
    color: #111827 !important;
}

/* ================================
   ALERT / RESULT BOXES
================================ */
.result-box {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-left: 5px solid #2563eb;
    border-radius: 14px;
    padding: 1rem;
    margin-top: 0.5rem;
    color: #111827;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.success-box {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 5px solid #22c55e;
    color: #14532d;
    border-radius: 14px;
    padding: 1rem;
}

.warning-box {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 5px solid #f59e0b;
    color: #78350f;
    border-radius: 14px;
    padding: 1rem;
}

.danger-box {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-left: 5px solid #ef4444;
    color: #7f1d1d;
    border-radius: 14px;
    padding: 1rem;
}

/* ================================
   EXPANDERS
================================ */
details {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 0.5rem 0.8rem !important;
}

summary {
    color: #111827 !important;
    font-weight: 600 !important;
}

/* ================================
   METRIC LABELS / SMALL TEXT
================================ */
small, .caption {
    color: #6b7280 !important;
}

/* ================================
   REMOVE DARK LOOK FROM CUSTOM BOXES
================================ */
.dark-box, .black-box {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 14px !important;
}

/* ================================
   STREAMLIT MARKDOWN BLOCK FIX
================================ */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] strong {
    color: #111827 !important;
}

/* ================================
   BADGES
================================ */
.badge {
    display: inline-block;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
}

.badge-red {
    background: #fee2e2;
    color: #b91c1c;
}

.badge-green {
    background: #dcfce7;
    color: #166534;
}

.badge-yellow {
    background: #fef3c7;
    color: #92400e;
}

.badge-blue {
    background: #dbeafe;
    color: #1d4ed8;
}

</style>
""", unsafe_allow_html=True)


# ======================================================
# SAFE HTML RENDERER (NO RAW HTML TAGS EVER)
# ======================================================

def render_html(html_content: str) -> None:
    """Strip leading line indentation so Markdown never turns HTML into code blocks."""
    cleaned = "\n".join(line.lstrip() for line in html_content.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


def format_lsr_display(val: Any) -> str:
    """Format list or stringified list of Life-Saving Rules cleanly."""
    if val is None:
        return "None"
    if isinstance(val, list):
        return ", ".join(str(x) for x in val if str(x).strip()) or "None"
    s = str(val).strip()
    if not s or s.lower() in {"none", "nan", "[]"}:
        return "None"
    try:
        parsed = ast.literal_eval(s)
        if isinstance(parsed, (list, tuple)):
            return ", ".join(str(x) for x in parsed if str(x).strip()) or "None"
    except Exception:
        pass
    return s.strip("[]'\"") or "None"


def parse_lsr_list(val: Any) -> List[str]:
    disp = format_lsr_display(val)
    if disp == "None":
        return []
    sep = ";" if ";" in disp else ","
    return [x.strip() for x in disp.split(sep) if x.strip()]


# ======================================================
# SESSION STATE INITIALIZATION
# ======================================================

if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

if "analyzer_text" not in st.session_state:
    st.session_state.analyzer_text = "Electrical isolation was not completed before maintenance started."

if "analyzer_site" not in st.session_state:
    st.session_state.analyzer_site = "Duliajan Central Asset"

if "review_overrides" not in st.session_state:
    st.session_state.review_overrides = {}


# ======================================================
# ENTERPRISE DASHBOARD CSS (UPLOADED REFERENCE STYLE)
# ======================================================

render_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: #16181D !important;
    background-color: #F7F8FA !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0px !important;
}

.stApp {
    background-color: #F7F8FA !important;
}

.block-container {
    padding-top: 1.05rem !important;
    padding-bottom: 2.4rem !important;
    padding-left: 1.75rem !important;
    padding-right: 1.75rem !important;
    max-width: 100% !important;
}

/* Slim White Left Sidebar */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E8EAF0 !important;
    width: 246px !important;
    min-width: 246px !important;
}

section[data-testid="stSidebar"] > div {
    background-color: #FFFFFF !important;
    padding-top: 1.0rem !important;
    padding-left: 0.85rem !important;
    padding-right: 0.85rem !important;
}

/* Unselected Sidebar Navigation Buttons */
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    width: 100% !important;
    justify-content: flex-start !important;
    text-align: left !important;
    background-color: transparent !important;
    color: #737985 !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    padding: 0.5rem 0.85rem !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    margin-bottom: 2px !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"] p,
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] span {
    color: #5E6470 !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background-color: #F3F5F9 !important;
    color: #16181D !important;
}

/* Selected Sidebar Navigation Button (Primary Blue Pill) */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    width: 100% !important;
    justify-content: flex-start !important;
    text-align: left !important;
    background-color: #2457F5 !important;
    color: #FFFFFF !important;
    border: 1px solid #2457F5 !important;
    border-radius: 10px !important;
    padding: 0.54rem 0.85rem !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(36, 87, 245, 0.22) !important;
    margin-bottom: 2px !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
section[data-testid="stSidebar"] .stButton > button[kind="primary"] span {
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
}

/* Main Content Buttons */
.main .stButton > button[kind="primary"] {
    background-color: #2457F5 !important;
    color: #FFFFFF !important;
    border: 1px solid #2457F5 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.05rem !important;
}

.main .stButton > button[kind="primary"] p,
.main .stButton > button[kind="primary"] span {
    color: #FFFFFF !important;
}

.main .stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #16181D !important;
    border: 1px solid #E8EAF0 !important;
    border-radius: 8px !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
}

.main .stButton > button[kind="secondary"] p {
    color: #16181D !important;
}

/* Plotly Chart Container Card Bottom */
div[data-testid="stPlotlyChart"] {
    background: #FFFFFF !important;
    border: 1px solid #E8EAF0 !important;
    border-radius: 0 0 14px 14px !important;
    border-top: none !important;
    padding: 4px 12px 10px 12px !important;
    margin-top: -1rem !important;
    margin-bottom: 0.8rem !important;
}

/* Reusable Enterprise UI Components */
.top-nav-bar {
    background: #FFFFFF;
    border: 1px solid #E8EAF0;
    border-radius: 14px;
    padding: 12px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}

.page-header-title {
    font-size: 24px;
    font-weight: 700;
    color: #16181D;
    letter-spacing: -0.02em;
    margin: 0;
}

.search-pill {
    background: #F7F8FA;
    border: 1px solid #ECEEF3;
    border-radius: 999px;
    padding: 8px 18px;
    width: 400px;
    max-width: 44vw;
    display: flex;
    align-items: center;
    gap: 10px;
    color: #9AA0AA;
    font-size: 13px;
}

.profile-cluster {
    display: flex;
    align-items: center;
    gap: 14px;
}

.notif-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #F7F8FA;
    border: 1px solid #E8EAF0;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.notif-dot {
    width: 7px;
    height: 7px;
    background: #EF4444;
    border-radius: 50%;
    position: absolute;
    top: 7px;
    right: 8px;
}

.v-divider {
    width: 1px;
    height: 28px;
    background: #E8EAF0;
}

.avatar-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #EEF2FF;
    border: 1px solid #C7D2FE;
    color: #2457F5;
    font-weight: 700;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E8EAF0;
    border-radius: 14px;
    padding: 16px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 108px;
}

.kpi-label {
    font-size: 12px;
    font-weight: 600;
    color: #737985;
    margin-bottom: 5px;
}

.kpi-metric {
    font-size: 27px;
    font-weight: 700;
    color: #16181D;
    line-height: 1.15;
    margin-bottom: 4px;
}

.kpi-sub {
    font-size: 11px;
    color: #9AA0AA;
    font-weight: 500;
}

.chart-header-box {
    background: #FFFFFF;
    border: 1px solid #E8EAF0;
    border-bottom: none;
    border-radius: 14px 14px 0 0;
    padding: 15px 18px 6px 18px;
}

.chart-title {
    font-size: 15.5px;
    font-weight: 600;
    color: #16181D;
    margin: 0;
}

.chart-subtitle {
    font-size: 11.5px;
    color: #737985;
    margin-top: 2px;
}

.exec-strip-card {
    background: #FFFFFF;
    border: 1px solid #E8EAF0;
    border-radius: 12px;
    padding: 10px 13px;
    height: 100%;
}

.exec-strip-label {
    font-size: 10.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: #737985;
    margin-bottom: 3px;
}

.exec-strip-val {
    font-size: 13px;
    font-weight: 700;
    color: #16181D;
}

.exec-strip-meta {
    font-size: 11px;
    color: #9AA0AA;
    margin-top: 2px;
}

.saas-card {
    background: #FFFFFF;
    border: 1px solid #E8EAF0;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 14px;
}

.saas-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
}

.saas-table th {
    text-align: left;
    padding: 9px 11px;
    color: #737985;
    font-weight: 600;
    font-size: 11.5px;
    border-bottom: 1px solid #E8EAF0;
    background: #FAFBFD;
}

.saas-table td {
    padding: 10px 11px;
    color: #16181D;
    border-bottom: 1px solid #F1F3F7;
    vertical-align: middle;
}

.saas-table tr:last-child td {
    border-bottom: none;
}

.saas-table tr:hover td {
    background: #F9FAFC;
}

.badge {
    display: inline-block;
    padding: 3px 9px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    line-height: 1.3;
}

.badge-sif {
    background: #FEF2F2;
    color: #EF4444;
    border: 1px solid #FECACA;
}

.badge-nonsif {
    background: #ECFDF5;
    color: #22A06B;
    border: 1px solid #A7F3D0;
}

.badge-review {
    background: #FFFBEB;
    color: #D97706;
    border: 1px solid #FDE68A;
}

.badge-blue {
    background: #EEF2FF;
    color: #2457F5;
    border: 1px solid #C7D2FE;
}

.badge-grey {
    background: #F3F4F6;
    color: #6B7280;
    border: 1px solid #E5E7EB;
}

.prio-high {
    color: #EF4444;
    font-weight: 600;
}

.prio-med {
    color: #F59E0B;
    font-weight: 600;
}

.prio-low {
    color: #22A06B;
    font-weight: 600;
}

.action-pill {
    display: inline-block;
    padding: 3px 9px;
    border-radius: 6px;
    background: #F0F4FF;
    color: #2457F5;
    font-weight: 600;
    font-size: 11px;
    border: 1px solid #DCE4FF;
}
</style>
""")


# ======================================================
# REUSABLE VISUAL HELPERS
# ======================================================

def render_top_header(page_title: str) -> None:
    render_html(f"""
    <div class="top-nav-bar">
        <div>
            <h1 class="page-header-title">{page_title}</h1>
        </div>
        <div class="search-pill">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#9AA0AA" stroke-width="2.2">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <span>Search reports, hazards, sites or activities...</span>
        </div>
        <div class="profile-cluster">
            <div class="notif-circle" title="System Notifications">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#16181D" stroke-width="2">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                    <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                </svg>
                <span class="notif-dot"></span>
            </div>
            <div class="v-divider"></div>
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="text-align:right;line-height:1.25;">
                    <div style="font-size:13px;font-weight:600;color:#16181D;">HSE Analyst</div>
                    <div style="font-size:11px;color:#737985;">Prototype Admin</div>
                </div>
                <div class="avatar-circle">HA</div>
            </div>
        </div>
    </div>
    """)


def render_kpi_ring_card(label: str, value: str, subtext: str, pct: float, pct_label: str, color: str, track: str = "#F1F3F7") -> None:
    radius = 23
    circumference = 2 * 3.14159 * radius
    dash_offset = circumference * (1 - max(0.0, min(100.0, float(pct))) / 100.0)
    render_html(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-metric">{value}</div>
            <div class="kpi-sub">{subtext}</div>
        </div>
        <div style="position:relative;width:58px;height:58px;flex-shrink:0;">
            <svg width="58" height="58" viewBox="0 0 58 58">
                <circle cx="29" cy="29" r="{radius}" fill="none" stroke="{track}" stroke-width="5"></circle>
                <circle cx="29" cy="29" r="{radius}" fill="none" stroke="{color}" stroke-width="5"
                    stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{dash_offset:.1f}"
                    stroke-linecap="round" transform="rotate(-90 29 29)"></circle>
            </svg>
            <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#16181D;">
                {pct_label}
            </div>
        </div>
    </div>
    """)


def format_result_badge(res: str) -> str:
    if res == "SIF Potential":
        return '<span class="badge badge-sif">SIF Potential</span>'
    if res in ("Non-SIF Potential", "Non-SIF"):
        return '<span class="badge badge-nonsif">Non-SIF Potential</span>'
    return '<span class="badge badge-review">Needs Review</span>'


def format_priority_badge(prio: str) -> str:
    if prio == "High":
        return '<span class="prio-high">High</span>'
    if prio == "Medium":
        return '<span class="prio-med">Medium</span>'
    return '<span class="prio-low">Low</span>'


def render_disclaimer_footer() -> None:
    render_html("""
    <div style="margin-top:20px;padding:12px 18px;background:#FFFFFF;border:1px solid #E8EAF0;border-radius:12px;display:flex;align-items:center;justify-content:space-between;font-size:11.5px;color:#737985;">
        <div>
            <strong style="color:#16181D;">Data & Positioning Notice:</strong>
            Prototype demonstration using synthetic / demonstration safety-report data. Production deployment would require validation using appropriately labelled representative operational HSSE data.
        </div>
        <div style="color:#9AA0AA;font-weight:500;">AI-assisted HSE decision support � AegisPulse</div>
    </div>
    """)


# ======================================================
# LEFT SIDEBAR NAVIGATION (10 PAGES)
# ======================================================

with st.sidebar:
    render_html("""
    <div style="display:flex;align-items:center;gap:11px;padding:6px 6px 18px 6px;border-bottom:1px solid #F1F3F7;margin-bottom:14px;">
        <div style="width:36px;height:36px;border-radius:10px;background:#2457F5;display:flex;align-items:center;justify-content:center;box-shadow:0 3px 8px rgba(36,87,245,0.25);">
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
        </div>
        <div style="line-height:1.2;">
            <div style="font-size:15.5px;font-weight:700;color:#16181D;letter-spacing:-0.01em;">SIF Intelligence</div>
            <div style="font-size:11px;font-weight:500;color:#737985;">HSE AI Platform</div>
        </div>
    </div>
    """)

    NAV_ITEMS = [
        ("Dashboard", "⊞"),
        ("Report Analyzer", "⌖"),
        ("Batch Analysis", "⇪"),
        ("Reports", "☰"),
        ("SIF Analysis", "◫"),
        ("Site & Activity Risk", "◈"),
        ("Life-Saving Rules", "🛡"),
        ("Precursor Patterns", "❖"),
        ("Review Queue", "✓"),
        ("Settings", "⚙"),
    ]

    for nav_name, nav_icon in NAV_ITEMS:
        is_selected = st.session_state.active_page == nav_name
        if st.button(
            f"{nav_icon}   {nav_name}",
            key=f"nav_{nav_name}",
            type="primary" if is_selected else "secondary",
            width="stretch",
        ):
            st.session_state.active_page = nav_name
            st.rerun()


# ======================================================
# 1. DASHBOARD PAGE
# ======================================================

def page_dashboard():
    render_top_header("Dashboard")

    try:
        summary = get_dashboard_summary()
        site_df = get_site_density()
        lsr_df = get_life_saving_rule_summary()
        reports_df = get_reports()
    except Exception as exc:
        st.error(f"Unable to load dashboard data: {exc}")
        return

    total = int(summary["total_reports"])
    sif_cnt = int(summary["sif_potential"])
    non_sif_cnt = int(summary["non_sif_potential"])
    review_cnt = int(summary["needs_review"])
    high_cnt = int(summary["high_priority"])

    sif_pct = round((sif_cnt / total * 100.0) if total else 0.0, 1)
    non_sif_pct = round((non_sif_cnt / total * 100.0) if total else 0.0, 1)
    review_pct = float(summary["abstention_rate_pct"])
    high_pct = round((high_cnt / total * 100.0) if total else 0.0, 1)

    # TOP KPI CARDS (5 REAL KPI CARDS)
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        render_kpi_ring_card("Total Reports", str(total), "Safety reports analyzed", 100, "100%", "#2457F5", "#E8EEFF")
    with k2:
        render_kpi_ring_card("SIF Potential", str(sif_cnt), "Potential SIF precursor", sif_pct, f"{sif_pct:.0f}%", "#EF4444", "#FEE2E2")
    with k3:
        render_kpi_ring_card("Non-SIF Potential", str(non_sif_cnt), "Controlled / routine state", non_sif_pct, f"{non_sif_pct:.0f}%", "#22A06B", "#DCFCE7")
    with k4:
        render_kpi_ring_card("Needs Review", str(review_cnt), "Requires HSE review", review_pct, f"{review_pct:.1f}%", "#F59E0B", "#FEF3C7")
    with k5:
        render_kpi_ring_card("High Priority", str(high_cnt), "SIF + Needs Review escalation", high_pct, f"{high_pct:.0f}%", "#EF4444", "#FEE2E2")

    render_html('<div style="height:10px;"></div>')

    # Check if multiple sites are tied for highest density
    max_site_density = float(site_df["sif_density"].max()) if not site_df.empty else 0.0
    tied_sites = site_df[site_df["sif_density"] == max_site_density] if not site_df.empty else pd.DataFrame()
    if len(tied_sites) > 1:
        site_card_title = "Top Density Sites (Tied)"
        top_row = tied_sites.iloc[0]
        site_card_value = f"{len(tied_sites)} Sites at {int(top_row['sif_reports'])}/{int(top_row['total_reports'])} ({max_site_density:.1f}%)"
        site_card_meta = ", ".join(tied_sites["site"].tolist()[:3])
    else:
        site_card_title = "Highest Density Site"
        top_row = site_df.iloc[0] if not site_df.empty else None
        site_card_value = f"{summary['highest_density_site']}"
        site_card_meta = (
            f"{int(top_row['sif_reports'])} / {int(top_row['total_reports'])} ({summary['highest_density_site_value']:.1f}%)"
            if top_row is not None
            else f"{summary['highest_density_site_value']:.1f}%"
        )

    # EXECUTIVE INTELLIGENCE STRIP (7 REAL BACKEND METRICS)
    strip_items = [
        ("Classification Coverage", f"{summary['classification_coverage_pct']:.1f}%", f"{summary['binary_classified']} / {total} binary classified", "#2457F5"),
        ("Abstention Rate", f"{summary['abstention_rate_pct']:.1f}%", f"{review_cnt} / {total} routed to review", "#F59E0B"),
        (site_card_title, site_card_value, site_card_meta, "#EF4444"),
        ("Highest Density Activity", str(summary["highest_density_activity"]), f"{summary['highest_density_activity_value']:.1f}% SIF density", "#2457F5"),
        ("Top Hazard", str(summary["top_hazard"]), "Primary SIF energy exposure", "#EF4444"),
        ("Top Critical Barrier", str(summary["top_barrier"]), "Primary barrier weakness", "#F59E0B"),
        ("Top Life-Saving Rule", str(summary["top_lsr"]), "Most triggered IOGP rule", "#2457F5"),
    ]
    s_cols = st.columns(7)
    for col, (st_lbl, st_val, st_meta, st_color) in zip(s_cols, strip_items):
        with col:
            render_html(f"""
            <div class="exec-strip-card" style="border-top:3px solid {st_color};">
                <div class="exec-strip-label">{st_lbl}</div>
                <div class="exec-strip-val" title="{st_val}">{st_val}</div>
                <div class="exec-strip-meta" title="{st_meta}">{st_meta}</div>
            </div>
            """)

    render_html('<div style="height:12px;"></div>')

    # ROW 2: LEFT SIF PRECURSOR TREND (BY HAZARD) | RIGHT SAFETY CLASSIFICATION DONUT
    col_left, col_right = st.columns([65, 35])

    with col_left:
        sif_only = reports_df[reports_df["ai_result"] == "SIF Potential"]
        hazard_counts = (
            sif_only["hazard"]
            .value_counts()
            .reset_index()
        )
        hazard_counts.columns = ["hazard", "count"]
        max_cap = max(int(hazard_counts["count"].max()) + 2, 10) if not hazard_counts.empty else 10

        render_html(f"""
        <div class="chart-header-box">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div>
                    <div class="chart-title">SIF Precursor Trend</div>
                    <div class="chart-subtitle">Real SIF-potential hazard concentration across {sif_cnt} flagged reports</div>
                </div>
                <span class="badge badge-sif">{sif_cnt} SIF Potential</span>
            </div>
        </div>
        """)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=hazard_counts["hazard"],
            y=[max_cap] * len(hazard_counts),
            marker=dict(color="#F2F4F8", cornerradius=6),
            width=0.36,
            hoverinfo="skip",
            showlegend=False,
        ))
        fig_trend.add_trace(go.Bar(
            x=hazard_counts["hazard"],
            y=hazard_counts["count"],
            marker=dict(color="#2457F5", cornerradius=6),
            width=0.36,
            text=hazard_counts["count"],
            textposition="outside",
            textfont=dict(size=11.5, color="#16181D"),
            hovertemplate="<b>%{x}</b><br>SIF Reports: %{y}<extra></extra>",
            showlegend=False,
        ))
        fig_trend.update_layout(
            barmode="overlay",
            height=255,
            margin=dict(l=8, r=8, t=10, b=8),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#737985")),
            yaxis=dict(showgrid=True, gridcolor="#F1F3F7", range=[0, max_cap + 1.5], tickfont=dict(size=11, color="#9AA0AA")),
        )
        st.plotly_chart(fig_trend, width="stretch", config={"displayModeBar": False})

    with col_right:
        render_html(f"""
        <div class="chart-header-box">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div>
                    <div class="chart-title">Safety Classification</div>
                    <div class="chart-subtitle">Hybrid ML + safety rules decision split</div>
                </div>
                <span class="badge badge-blue">{total} Reports</span>
            </div>
        </div>
        """)
        fig_donut = go.Figure(data=[go.Pie(
            labels=["SIF Potential", "Non-SIF Potential", "Needs Review"],
            values=[sif_cnt, non_sif_cnt, review_cnt],
            hole=0.68,
            marker=dict(colors=["#EF4444", "#22A06B", "#F59E0B"], line=dict(color="#FFFFFF", width=2)),
            textinfo="none",
            hovertemplate="<b>%{label}</b>: %{value} reports (%{percent})<extra></extra>",
            sort=False,
        )])
        fig_donut.update_layout(
            height=255,
            margin=dict(l=8, r=8, t=8, b=8),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            annotations=[dict(
                text=f"<b>{total}</b><br><span style='font-size:11px;color:#737985;'>Total Reports</span>",
                x=0.5,
                y=0.5,
                font=dict(size=16, color="#16181D"),
                showarrow=False,
            )],
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=0.80, font=dict(size=11.5)),
        )
        st.plotly_chart(fig_donut, width="stretch", config={"displayModeBar": False})

    # ROW 3: SITE DENSITY RANKING (WITH SIF/TOTAL + %) | LIFE-SAVING RULE DISTRIBUTION
    r3_left, r3_right = st.columns([60, 40])

    with r3_left:
        render_html("""
        <div class="chart-header-box">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div>
                    <div class="chart-title">Top Density Sites — SIF-Precursor Ranking</div>
                    <div class="chart-subtitle">Prototype ranking based on demonstration data (showing SIF / Total and Density %)</div>
                </div>
                <span class="badge badge-blue">SIF / Total (%)</span>
            </div>
        </div>
        """)
        site_sorted = site_df.sort_values(["sif_density", "sif_reports"], ascending=[True, True])
        bar_labels = [
            f"{int(r['sif_reports'])} / {int(r['total_reports'])} ({r['sif_density']:.1f}%)"
            for _, r in site_sorted.iterrows()
        ]
        fig_site = go.Figure()
        fig_site.add_trace(go.Bar(
            y=site_sorted["site"],
            x=[100] * len(site_sorted),
            orientation="h",
            marker=dict(color="#F2F4F8", cornerradius=5),
            width=0.48,
            hoverinfo="skip",
            showlegend=False,
        ))
        fig_site.add_trace(go.Bar(
            y=site_sorted["site"],
            x=site_sorted["sif_density"],
            orientation="h",
            marker=dict(color="#2457F5", cornerradius=5),
            width=0.48,
            text=bar_labels,
            textposition="outside",
            textfont=dict(size=11, color="#16181D"),
            hovertemplate="<b>%{y}</b><br>SIF Density: %{text}<extra></extra>",
            showlegend=False,
        ))
        fig_site.update_layout(
            barmode="overlay",
            height=250,
            margin=dict(l=10, r=65, t=8, b=8),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            xaxis=dict(range=[0, 108], showgrid=True, gridcolor="#F1F3F7", ticksuffix="%", tickfont=dict(size=11, color="#9AA0AA")),
            yaxis=dict(showgrid=False, tickfont=dict(size=11.5, color="#16181D")),
        )
        st.plotly_chart(fig_site, width="stretch", config={"displayModeBar": False})

    with r3_right:
        render_html("""
        <div class="chart-header-box">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div>
                    <div class="chart-title">Life-Saving Rule Distribution</div>
                    <div class="chart-subtitle">IOGP rule triggers on SIF-potential reports</div>
                </div>
            </div>
        </div>
        """)
        lsr_nonzero = lsr_df[lsr_df["sif_reports"] > 0]
        palette = ["#2457F5", "#EF4444", "#0EA5E9", "#F59E0B", "#22A06B", "#8B5CF6", "#EC4899", "#64748B"]
        fig_lsr = go.Figure(data=[go.Pie(
            labels=lsr_nonzero["life_saving_rule"],
            values=lsr_nonzero["sif_reports"],
            hole=0.62,
            marker=dict(colors=palette[:len(lsr_nonzero)], line=dict(color="#FFFFFF", width=2)),
            textinfo="none",
            hovertemplate="<b>%{label}</b>: %{value} SIF reports<extra></extra>",
            sort=False,
        )])
        fig_lsr.update_layout(
            height=250,
            margin=dict(l=8, r=8, t=8, b=8),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            annotations=[dict(
                text=f"<b>{int(lsr_df['sif_reports'].sum())}</b><br><span style='font-size:10.5px;color:#737985;'>Rule Triggers</span>",
                x=0.5,
                y=0.5,
                font=dict(size=14, color="#16181D"),
                showarrow=False,
            )],
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=0.76, font=dict(size=10.5)),
        )
        st.plotly_chart(fig_lsr, width="stretch", config={"displayModeBar": False})

    # DASHBOARD SITE DENSITY TABLE (SHOWING ALL REQUIRED COLUMNS + SIF/TOTAL AND %)
    site_rows_html = ""
    for _, r in site_df.iterrows():
        site_rows_html += f"""
        <tr>
            <td style="font-weight:600;color:#16181D;">{r['site']}</td>
            <td>{int(r['total_reports'])}</td>
            <td><span class="badge badge-sif">{int(r['sif_reports'])}</span></td>
            <td><span class="badge badge-nonsif">{int(r['non_sif_reports'])}</span></td>
            <td><span class="badge badge-review">{int(r['needs_review'])}</span></td>
            <td style="font-weight:700;color:#2457F5;">{int(r['sif_reports'])} / {int(r['total_reports'])} ({r['sif_density']:.1f}%)</td>
            <td>{r['top_hazard']}</td>
            <td>{r['top_barrier']}</td>
            <td>{r['top_activity']}</td>
            <td><span class="badge badge-blue">{r['top_lsr']}</span></td>
        </tr>
        """

    render_html(f"""
    <div class="saas-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
            <div>
                <span style="font-size:15.5px;font-weight:700;color:#16181D;">Site SIF-Precursor Summary Table</span>
                <span style="font-size:12px;color:#737985;margin-left:10px;">Prototype ranking based on demonstration data.</span>
            </div>
            <span class="badge badge-grey">Tied sites at 5 / 10 (50.0%) shown as Top Density Sites</span>
        </div>
        <table class="saas-table">
            <thead>
                <tr>
                    <th>Site</th>
                    <th>Total Reports</th>
                    <th>SIF Reports</th>
                    <th>Non-SIF Reports</th>
                    <th>Needs Review</th>
                    <th>SIF Density</th>
                    <th>Top Hazard</th>
                    <th>Top Barrier</th>
                    <th>Top Activity</th>
                    <th>Top LSR</th>
                </tr>
            </thead>
            <tbody>{site_rows_html}</tbody>
        </table>
    </div>
    """)


# ======================================================
# 2. REPORT ANALYZER PAGE
# ======================================================

def page_report_analyzer():
    render_top_header("Report Analyzer")

    render_html("""
    <div class="saas-card" style="margin-bottom:12px;">
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
                <div style="font-size:16.5px;font-weight:700;color:#16181D;">Live Free-Text Safety Report Analyzer</div>
                <div style="font-size:12.5px;color:#737985;">Paste an unsafe-act, unsafe-condition, near-miss or incident report.</div>
            </div>
            <span class="badge badge-blue">Connected to src.backend_adapter.analyze_single_report</span>
        </div>
    </div>
    """)

    # 3 Live Test Preset Buttons for 1-click verification
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        if st.button("Live Test 1: Incomplete Isolation (SIF)", key="lt_1", width="stretch"):
            st.session_state.analyzer_text = "Electrical isolation was not completed before maintenance started."
    with t_col2:
        if st.button("Live Test 2: Verified Isolation (Non-SIF)", key="lt_2", width="stretch"):
            st.session_state.analyzer_text = "Electrical isolation was completed and verified before maintenance."
    with t_col3:
        if st.button("Live Test 3: Vague Condition (Needs Review)", key="lt_3", width="stretch"):
            st.session_state.analyzer_text = "An unsafe condition was observed near equipment during maintenance."

    report_text = st.text_area(
        "Paste an unsafe-act, unsafe-condition, near-miss or incident report.",
        value=st.session_state.analyzer_text,
        height=105,
    )

    in_c1, in_c2 = st.columns([75, 25])
    with in_c1:
        site_value = st.text_input("Site / Location (Optional)", value=st.session_state.analyzer_site)
    with in_c2:
        render_html('<div style="height:24px;"></div>')
        analyze_clicked = st.button("Analyze Report", key="btn_analyze_live", type="primary", width="stretch")

    if analyze_clicked:
        st.session_state.analyzer_text = report_text
        st.session_state.analyzer_site = site_value

    try:
        result = analyze_single_report(
            report_text,
            site=site_value,
            report_id=None,
        )
    except Exception as exc:
        st.error(f"Unable to analyze safety report: {exc}")
        return

    lsr_str = format_lsr_display(result.get("life_saving_rules"))
    ev_str = result.get("evidence") or "None extracted"
    rev_reason_str = result.get("review_reason") or "Not applicable (Direct classification)"

    # TOP ROW: ML Classification vs Final Safety Decision, Priority, Internal classifier score
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_html(f"""
        <div class="saas-card" style="padding:15px 18px;">
            <div class="kpi-label">ML Classification</div>
            <div style="margin:6px 0;">{format_result_badge(result['model_prediction'])}</div>
            <div class="kpi-sub">Binary ML classifier output</div>
        </div>
        """)
    with c2:
        render_html(f"""
        <div class="saas-card" style="padding:15px 18px;">
            <div class="kpi-label">Final Safety Decision</div>
            <div style="margin:6px 0;">{format_result_badge(result['ai_result'])}</div>
            <div class="kpi-sub">Hybrid safety decision + abstention layer</div>
        </div>
        """)
    with c3:
        render_html(f"""
        <div class="saas-card" style="padding:15px 18px;">
            <div class="kpi-label">Priority</div>
            <div style="font-size:20px;margin:4px 0;">{format_priority_badge(result['priority'])}</div>
            <div class="kpi-sub">Context: {result['context']}</div>
        </div>
        """)
    with c4:
        render_html(f"""
        <div class="saas-card" style="padding:15px 18px;">
            <div class="kpi-label">Internal classifier score</div>
            <div style="font-size:21px;font-weight:700;color:#16181D;margin:4px 0;">{float(result['model_score']):.2f}</div>
            <div class="kpi-sub">Internal classifier score (non-probabilistic)</div>
        </div>
        """)

    # SECOND ROW: ALL EXTRACTED REPORT ANALYZER CARDS
    ic1, ic2, ic3, ic4, ic5, ic6 = st.columns(6)
    cards_meta = [
        ("Context", result["context"]),
        ("Site", result["site"]),
        ("Activity", result["activity"]),
        ("Hazard", result["hazard"]),
        ("Critical Barrier", result["barrier"]),
        ("Barrier Condition", result["barrier_condition"]),
    ]
    for col, (k_lbl, k_val) in zip([ic1, ic2, ic3, ic4, ic5, ic6], cards_meta):
        with col:
            render_html(f"""
            <div class="saas-card" style="padding:12px 14px;">
                <div style="font-size:11px;font-weight:600;color:#737985;margin-bottom:4px;">{k_lbl}</div>
                <div style="font-size:13.5px;font-weight:700;color:#16181D;">{k_val}</div>
            </div>
            """)

    # IOGP LIFE-SAVING RULES, EVIDENCE & REVIEW REASON
    render_html(f"""
    <div class="saas-card" style="border-left:4px solid #2457F5;">
        <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:14px;">
            <div>
                <div style="font-size:11px;font-weight:700;color:#2457F5;text-transform:uppercase;">IOGP Life-Saving Rules</div>
                <div style="font-size:17px;font-weight:700;color:#16181D;margin:3px 0;">{lsr_str}</div>
                <div style="font-size:12.5px;color:#737985;">
                    <strong style="color:#16181D;">Evidence:</strong> {ev_str}
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:11px;font-weight:600;color:#737985;">Review Reason</div>
                <div style="font-size:12.5px;font-weight:600;color:#D97706;margin-top:3px;">{rev_reason_str}</div>
            </div>
        </div>
    </div>
    """)

    # COMPACT CONNECTED ANALYSIS FLOW
    render_html(f"""
    <div class="saas-card" style="padding:13px 16px;">
        <div style="font-size:12px;font-weight:600;color:#737985;margin-bottom:8px;">Report Analysis Flow</div>
        <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:nowrap;overflow-x:auto;">
            <div style="flex:1;background:#F7F8FA;border:1px solid #E8EAF0;border-radius:9px;padding:8px 10px;">
                <div style="font-size:10px;color:#737985;font-weight:600;">Report</div>
                <div style="font-size:11.5px;font-weight:600;color:#16181D;">{result['site']}</div>
            </div>
            <div style="color:#2457F5;font-weight:700;">→</div>
            <div style="flex:1;background:#F7F8FA;border:1px solid #E8EAF0;border-radius:9px;padding:8px 10px;">
                <div style="font-size:10px;color:#737985;font-weight:600;">AI/NLP Analysis</div>
                <div style="font-size:11.5px;font-weight:600;color:#2457F5;">{result['ai_result']} ({float(result['model_score']):.2f})</div>
            </div>
            <div style="color:#2457F5;font-weight:700;">→</div>
            <div style="flex:1;background:#F7F8FA;border:1px solid #E8EAF0;border-radius:9px;padding:8px 10px;">
                <div style="font-size:10px;color:#737985;font-weight:600;">Hazard</div>
                <div style="font-size:11.5px;font-weight:600;color:#EF4444;">{result['hazard']}</div>
            </div>
            <div style="color:#2457F5;font-weight:700;">→</div>
            <div style="flex:1;background:#F7F8FA;border:1px solid #E8EAF0;border-radius:9px;padding:8px 10px;">
                <div style="font-size:10px;color:#737985;font-weight:600;">Critical Barrier</div>
                <div style="font-size:11.5px;font-weight:600;color:#16181D;">{result['barrier']}</div>
            </div>
            <div style="color:#2457F5;font-weight:700;">→</div>
            <div style="flex:1;background:#F7F8FA;border:1px solid #E8EAF0;border-radius:9px;padding:8px 10px;">
                <div style="font-size:10px;color:#737985;font-weight:600;">IOGP Life-Saving Rule</div>
                <div style="font-size:11.5px;font-weight:600;color:#2457F5;">{lsr_str}</div>
            </div>
            <div style="color:#2457F5;font-weight:700;">→</div>
            <div style="flex:1.2;background:#EEF2FF;border:1px solid #C7D2FE;border-radius:9px;padding:8px 10px;">
                <div style="font-size:10px;color:#2457F5;font-weight:600;">Recommended Action</div>
                <div style="font-size:11px;font-weight:600;color:#16181D;">{str(result['recommended_action'])[:45]}...</div>
            </div>
        </div>
    </div>
    """)

    # POTENTIAL CONSEQUENCE & RECOMMENDED ACTION
    pc1, pc2 = st.columns(2)
    with pc1:
        render_html(f"""
        <div class="saas-card" style="border-left:4px solid #EF4444;">
            <div style="font-size:11.5px;font-weight:600;color:#737985;margin-bottom:4px;">Potential Consequence</div>
            <div style="font-size:14px;font-weight:700;color:#16181D;">{result['potential_consequence']}</div>
        </div>
        """)
    with pc2:
        render_html(f"""
        <div class="saas-card" style="border-left:4px solid #22A06B;">
            <div style="font-size:11.5px;font-weight:600;color:#737985;margin-bottom:4px;">Recommended Action</div>
            <div style="font-size:14px;font-weight:700;color:#16181D;">{result['recommended_action']}</div>
        </div>
        """)


# ======================================================
# 3. BATCH ANALYSIS PAGE
# ======================================================

def page_batch_analysis():
    render_top_header("Batch Safety Report Analysis")

    render_html("""
    <div class="saas-card">
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
                <div style="font-size:16px;font-weight:700;color:#16181D;">Batch CSV Safety Report Ingestion</div>
                <div style="font-size:12px;color:#737985;">
                    Expected columns: <code>report_id</code>, <code>text</code> (or <code>report_text</code> / <code>description</code> / <code>narrative</code>), <code>site</code>
                </div>
            </div>
            <span class="badge badge-blue">Uses src.backend_adapter.analyze_batch_reports</span>
        </div>
    </div>
    """)

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    try:
        if uploaded_file is not None:
            input_df = pd.read_csv(uploaded_file)
            result_df = analyze_batch_reports(input_df)
        else:
            # Analyze real backend dataset via analyze_batch_reports / get_reports
            result_df = get_reports()
    except Exception as exc:
        st.error(f"Unable to process batch reports: {exc}")
        return

    total_proc = len(result_df)
    sif_proc = int((result_df["ai_result"] == "SIF Potential").sum())
    nonsif_proc = int((result_df["ai_result"] == "Non-SIF Potential").sum())
    rev_proc = int((result_df["ai_result"] == "Needs Review").sum())

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_ring_card("Reports Processed", str(total_proc), "Analyzed via backend adapter", 100, "100%", "#2457F5")
    with k2:
        render_kpi_ring_card("SIF Potential", str(sif_proc), "Flagged SIF precursors", round(sif_proc / max(total_proc, 1) * 100, 1), f"{round(sif_proc / max(total_proc, 1) * 100)}%", "#EF4444")
    with k3:
        render_kpi_ring_card("Non-SIF Potential", str(nonsif_proc), "Controlled / routine", round(nonsif_proc / max(total_proc, 1) * 100, 1), f"{round(nonsif_proc / max(total_proc, 1) * 100)}%", "#22A06B")
    with k4:
        render_kpi_ring_card("Needs Review", str(rev_proc), "Human HSE review queue", round(rev_proc / max(total_proc, 1) * 100, 1), f"{round(rev_proc / max(total_proc, 1) * 100)}%", "#F59E0B")

    display_cols = [
        "report_id",
        "site",
        "report_text",
        "model_prediction",
        "ai_result",
        "priority",
        "activity",
        "hazard",
        "barrier",
        "barrier_condition",
        "life_saving_rules",
        "model_score",
    ]
    existing_cols = [c for c in display_cols if c in result_df.columns]

    st.download_button(
        label="Download Results (CSV)",
        data=result_df[existing_cols].to_csv(index=False).encode("utf-8"),
        file_name="sif_batch_analysis_results.csv",
        mime="text/csv",
    )

    st.dataframe(result_df[existing_cols], width="stretch", hide_index=True)


# ======================================================
# 4. REPORTS PAGE
# ======================================================

def page_reports():
    render_top_header("Safety Reports")

    try:
        reports_df = get_reports()
    except Exception as exc:
        st.error(f"Unable to load reports: {exc}")
        return

    f1, f2, f3, f4, f5, f6 = st.columns([22, 16, 16, 14, 16, 16])
    with f1:
        q_search = st.text_input("Search", placeholder="Search narrative or ID...")
    with f2:
        f_ai = st.selectbox("AI Result", ["All"] + sorted(reports_df["ai_result"].dropna().unique().tolist()))
    with f3:
        f_site = st.selectbox("Site", ["All"] + sorted(reports_df["site"].dropna().unique().tolist()))
    with f4:
        f_prio = st.selectbox("Priority", ["All"] + sorted(reports_df["priority"].dropna().unique().tolist()))
    with f5:
        f_act = st.selectbox("Activity", ["All"] + sorted(reports_df["activity"].dropna().unique().tolist()))
    with f6:
        f_haz = st.selectbox("Hazard", ["All"] + sorted(reports_df["hazard"].dropna().unique().tolist()))

    filtered = reports_df.copy()
    if q_search:
        mask = (
            filtered["report_text"].astype(str).str.contains(q_search, case=False, na=False)
            | filtered["report_id"].astype(str).str.contains(q_search, case=False, na=False)
        )
        filtered = filtered[mask]
    if f_ai != "All":
        filtered = filtered[filtered["ai_result"] == f_ai]
    if f_site != "All":
        filtered = filtered[filtered["site"] == f_site]
    if f_prio != "All":
        filtered = filtered[filtered["priority"] == f_prio]
    if f_act != "All":
        filtered = filtered[filtered["activity"] == f_act]
    if f_haz != "All":
        filtered = filtered[filtered["hazard"] == f_haz]

    rows_html = ""
    for _, r in filtered.iterrows():
        rows_html += f"""
        <tr>
            <td style="font-weight:700;color:#2457F5;">{r['report_id']}</td>
            <td style="max-width:260px;">{str(r['report_text'])[:75]}...</td>
            <td>{r['site']}</td>
            <td>{format_result_badge(str(r['ai_result']))}</td>
            <td>{format_priority_badge(str(r['priority']))}</td>
            <td>{r['activity']}</td>
            <td>{r['hazard']}</td>
            <td>{r['barrier']}</td>
            <td style="font-weight:600;">{float(r['model_score']):.2f}</td>
        </tr>
        """

    render_html(f"""
    <div class="saas-card">
        <div style="font-size:15.5px;font-weight:700;color:#16181D;margin-bottom:10px;">
            Safety Reports ({len(filtered)} of {len(reports_df)} reports)
        </div>
        <table class="saas-table">
            <thead>
                <tr>
                    <th>report_id</th>
                    <th>report_text</th>
                    <th>site</th>
                    <th>ai_result</th>
                    <th>priority</th>
                    <th>activity</th>
                    <th>hazard</th>
                    <th>barrier</th>
                    <th>model_score</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """)

    if not filtered.empty:
        sel_id = st.selectbox("Select Report ID to View Full Analysis", filtered["report_id"].tolist(), index=0)
        sel_row = filtered[filtered["report_id"] == sel_id].iloc[0]
        render_html(f"""
        <div class="saas-card" style="border-left:4px solid #2457F5;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <div style="font-size:15px;font-weight:700;color:#16181D;">Report {sel_row['report_id']} — {sel_row['site']}</div>
                <div>
                    <span style="font-size:12px;color:#737985;margin-right:10px;">ML Classification: <strong>{sel_row['model_prediction']}</strong></span>
                    <span style="font-size:12px;color:#737985;margin-right:6px;">Final Safety Decision:</span>
                    {format_result_badge(str(sel_row['ai_result']))}
                </div>
            </div>
            <div style="font-size:13px;background:#F7F8FA;padding:10px 14px;border-radius:8px;margin-bottom:10px;">
                <strong>Original Report:</strong> “{sel_row['report_text']}”
            </div>
            <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:10px;font-size:12px;">
                <div><strong style="color:#737985;">Context:</strong> {sel_row['context']}</div>
                <div><strong style="color:#737985;">Activity:</strong> {sel_row['activity']}</div>
                <div><strong style="color:#737985;">Hazard:</strong> {sel_row['hazard']}</div>
                <div><strong style="color:#737985;">Barrier:</strong> {sel_row['barrier']} ({sel_row['barrier_condition']})</div>
                <div><strong style="color:#737985;">Life-Saving Rules:</strong> {format_lsr_display(sel_row['life_saving_rules'])}</div>
                <div><strong style="color:#737985;">Evidence:</strong> {sel_row['evidence']}</div>
                <div><strong style="color:#737985;">Potential Consequence:</strong> {sel_row['potential_consequence']}</div>
                <div><strong style="color:#737985;">Recommended Action:</strong> {sel_row['recommended_action']}</div>
            </div>
        </div>
        """)


# ======================================================
# 5. SIF ANALYSIS PAGE
# ======================================================

def page_sif_analysis():
    render_top_header("SIF Analysis")

    try:
        reports_df = get_reports()
        lsr_df = get_life_saving_rule_summary()
    except Exception as exc:
        st.error(f"Unable to load SIF analysis data: {exc}")
        return

    sif_df = reports_df[reports_df["ai_result"] == "SIF Potential"].copy()
    total_sif = len(sif_df)
    high_prio_sif = int((sif_df["priority"] == "High").sum())
    top_haz = sif_df["hazard"].mode().iloc[0] if not sif_df.empty else "None"
    top_bar = sif_df["barrier"].mode().iloc[0] if not sif_df.empty else "None"
    top_act = sif_df[sif_df["activity"] != "Unknown"]["activity"].mode().iloc[0] if not sif_df.empty else "None"
    top_site = sif_df["site"].mode().iloc[0] if not sif_df.empty else "None"

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    kpi_items = [
        ("Total SIF Potential", str(total_sif), "#EF4444"),
        ("High Priority SIF", str(high_prio_sif), "#EF4444"),
        ("Most Frequent SIF Hazard", str(top_haz), "#16181D"),
        ("Most Frequent Barrier", str(top_bar), "#2457F5"),
        ("Most Frequent Activity", str(top_act), "#16181D"),
        ("Most Frequent Site", str(top_site), "#2457F5"),
    ]
    for col, (lbl, val, clr) in zip([k1, k2, k3, k4, k5, k6], kpi_items):
        with col:
            render_html(f"""
            <div class="saas-card" style="padding:13px 14px;border-top:3px solid {clr};min-height:92px;">
                <div style="font-size:11px;font-weight:600;color:#737985;margin-bottom:4px;">{lbl}</div>
                <div style="font-size:14.5px;font-weight:700;color:{clr};">{val}</div>
            </div>
            """)

    c1, c2 = st.columns(2)
    with c1:
        render_html('<div class="chart-header-box"><div class="chart-title">SIF by Activity</div></div>')
        act_c = sif_df["activity"].value_counts().reset_index()
        act_c.columns = ["activity", "count"]
        fig1 = go.Figure(go.Bar(x=act_c["activity"], y=act_c["count"], marker=dict(color="#2457F5", cornerradius=5), text=act_c["count"], textposition="outside"))
        fig1.update_layout(height=240, margin=dict(l=8, r=8, t=14, b=8), paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF")
        st.plotly_chart(fig1, width="stretch", config={"displayModeBar": False})

    with c2:
        render_html('<div class="chart-header-box"><div class="chart-title">SIF by Hazard</div></div>')
        haz_c = sif_df["hazard"].value_counts().reset_index()
        haz_c.columns = ["hazard", "count"]
        fig2 = go.Figure(go.Bar(y=haz_c["hazard"][::-1], x=haz_c["count"][::-1], orientation="h", marker=dict(color="#EF4444", cornerradius=5), text=haz_c["count"][::-1], textposition="outside"))
        fig2.update_layout(height=240, margin=dict(l=10, r=30, t=14, b=8), paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF")
        st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})

    c3, c4, c5 = st.columns(3)
    with c3:
        render_html('<div class="chart-header-box"><div class="chart-title">SIF by Site</div></div>')
        site_c = sif_df["site"].value_counts().reset_index()
        site_c.columns = ["site", "count"]
        fig3 = go.Figure(go.Bar(x=site_c["site"], y=site_c["count"], marker=dict(color="#2457F5", cornerradius=5), text=site_c["count"], textposition="outside"))
        fig3.update_layout(height=235, margin=dict(l=8, r=8, t=14, b=8), paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF")
        st.plotly_chart(fig3, width="stretch", config={"displayModeBar": False})

    with c4:
        render_html('<div class="chart-header-box"><div class="chart-title">Critical Barrier Distribution</div></div>')
        bar_c = sif_df["barrier"].value_counts().reset_index()
        bar_c.columns = ["barrier", "count"]
        fig4 = go.Figure(go.Bar(y=bar_c["barrier"][::-1], x=bar_c["count"][::-1], orientation="h", marker=dict(color="#2457F5", cornerradius=5), text=bar_c["count"][::-1], textposition="outside"))
        fig4.update_layout(height=235, margin=dict(l=10, r=28, t=14, b=8), paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF")
        st.plotly_chart(fig4, width="stretch", config={"displayModeBar": False})

    with c5:
        render_html('<div class="chart-header-box"><div class="chart-title">Life-Saving Rule Distribution</div></div>')
        lsr_nz = lsr_df[lsr_df["sif_reports"] > 0]
        fig5 = go.Figure(go.Bar(y=lsr_nz["life_saving_rule"][::-1], x=lsr_nz["sif_reports"][::-1], orientation="h", marker=dict(color="#0EA5E9", cornerradius=5), text=lsr_nz["sif_reports"][::-1], textposition="outside"))
        fig5.update_layout(height=235, margin=dict(l=10, r=28, t=14, b=8), paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF")
        st.plotly_chart(fig5, width="stretch", config={"displayModeBar": False})


# ======================================================
# 6. SITE & ACTIVITY RISK PAGE
# ======================================================

def page_site_activity_risk():
    render_top_header("Site & Activity SIF-Precursor Density")

    try:
        site_df = get_site_density()
        activity_df = get_activity_density()
        hotspots_df = get_site_activity_hotspots()
    except Exception as exc:
        st.error(f"Unable to load site and activity density data: {exc}")
        return

    tab_site, tab_act = st.tabs(["🏢  Site SIF-Precursor Density", "⚙️  Activity SIF-Precursor Density"])

    with tab_site:
        sc1, sc2 = st.columns([40, 60])
        with sc1:
            render_html("""
            <div class="chart-header-box">
                <div class="chart-title">Top Density Sites (SIF / Total & %)</div>
                <div class="chart-subtitle">Prototype ranking based on demonstration data</div>
            </div>
            """)
            s_sorted = site_df.sort_values(["sif_density", "sif_reports"], ascending=[True, True])
            s_labels = [f"{int(r['sif_reports'])} / {int(r['total_reports'])} ({r['sif_density']:.1f}%)" for _, r in s_sorted.iterrows()]
            fig_s = go.Figure(go.Bar(
                y=s_sorted["site"],
                x=s_sorted["sif_density"],
                orientation="h",
                marker=dict(color="#2457F5", cornerradius=5),
                text=s_labels,
                textposition="outside",
            ))
            fig_s.update_layout(height=275, margin=dict(l=10, r=70, t=10, b=8), paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", xaxis=dict(range=[0, 80], ticksuffix="%"))
            st.plotly_chart(fig_s, width="stretch", config={"displayModeBar": False})

        with sc2:
            s_rows = ""
            for idx, r in site_df.iterrows():
                s_rows += f"""
                <tr>
                    <td style="font-weight:700;color:#2457F5;">#{idx + 1}</td>
                    <td style="font-weight:600;">{r['site']}</td>
                    <td>{int(r['total_reports'])}</td>
                    <td><span class="badge badge-sif">{int(r['sif_reports'])}</span></td>
                    <td><span class="badge badge-nonsif">{int(r['non_sif_reports'])}</span></td>
                    <td><span class="badge badge-review">{int(r['needs_review'])}</span></td>
                    <td style="font-weight:700;color:#2457F5;">{int(r['sif_reports'])} / {int(r['total_reports'])} ({r['sif_density']:.1f}%)</td>
                    <td>{r['top_hazard']}</td>
                    <td>{r['top_barrier']}</td>
                    <td>{r['top_activity']}</td>
                    <td><span class="badge badge-blue">{r['top_lsr']}</span></td>
                </tr>
                """
            render_html(f"""
            <div class="saas-card">
                <div style="font-size:15px;font-weight:700;color:#16181D;margin-bottom:8px;">Ranked Site Density Table</div>
                <table class="saas-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Site</th>
                            <th>Total Reports</th>
                            <th>SIF Reports</th>
                            <th>Non-SIF Reports</th>
                            <th>Needs Review</th>
                            <th>SIF Density</th>
                            <th>Top Hazard</th>
                            <th>Top Barrier</th>
                            <th>Top Activity</th>
                            <th>Top LSR</th>
                        </tr>
                    </thead>
                    <tbody>{s_rows}</tbody>
                </table>
            </div>
            """)

    with tab_act:
        ac1, ac2 = st.columns([40, 60])
        with ac1:
            render_html("""
            <div class="chart-header-box">
                <div class="chart-title">Activity SIF Density (Showing Volume & %)</div>
                <div class="chart-subtitle">Small-volume categories (e.g. 2/2) explicitly annotated</div>
            </div>
            """)
            a_sorted = activity_df.sort_values(["sif_density", "sif_reports"], ascending=[True, True])
            a_labels = [
                f"{int(r['sif_reports'])} / {int(r['total_reports'])} ({r['sif_density']:.1f}%)"
                + (" [low vol]" if int(r["total_reports"]) <= 2 else "")
                for _, r in a_sorted.iterrows()
            ]
            fig_a = go.Figure(go.Bar(
                y=a_sorted["activity"],
                x=a_sorted["sif_density"],
                orientation="h",
                marker=dict(color="#2457F5", cornerradius=5),
                text=a_labels,
                textposition="outside",
            ))
            fig_a.update_layout(height=360, margin=dict(l=10, r=95, t=10, b=8), paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", xaxis=dict(range=[0, 135], ticksuffix="%"))
            st.plotly_chart(fig_a, width="stretch", config={"displayModeBar": False})

        with ac2:
            a_rows = ""
            for idx, r in activity_df.iterrows():
                vol_note = ' <span class="badge badge-grey">Small sample (n≤2)</span>' if int(r["total_reports"]) <= 2 else ""
                a_rows += f"""
                <tr>
                    <td style="font-weight:700;color:#2457F5;">#{idx + 1}</td>
                    <td style="font-weight:600;">{r['activity']}{vol_note}</td>
                    <td>{int(r['total_reports'])}</td>
                    <td><span class="badge badge-sif">{int(r['sif_reports'])}</span></td>
                    <td><span class="badge badge-nonsif">{int(r['non_sif_reports'])}</span></td>
                    <td><span class="badge badge-review">{int(r['needs_review'])}</span></td>
                    <td style="font-weight:700;color:#2457F5;">{int(r['sif_reports'])} / {int(r['total_reports'])} ({r['sif_density']:.1f}%)</td>
                    <td>{r['top_hazard']}</td>
                    <td>{r['top_barrier']}</td>
                    <td>{r['top_site']}</td>
                    <td><span class="badge badge-blue">{r['top_lsr']}</span></td>
                </tr>
                """
            render_html(f"""
            <div class="saas-card">
                <div style="font-size:15px;font-weight:700;color:#16181D;margin-bottom:8px;">Ranked Activity Density Table</div>
                <table class="saas-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Activity</th>
                            <th>Total Reports</th>
                            <th>SIF Reports</th>
                            <th>Non-SIF Reports</th>
                            <th>Needs Review</th>
                            <th>SIF Density</th>
                            <th>Top Hazard</th>
                            <th>Top Barrier</th>
                            <th>Top Site</th>
                            <th>Top LSR</th>
                        </tr>
                    </thead>
                    <tbody>{a_rows}</tbody>
                </table>
            </div>
            """)

    # HSE INTERVENTION HOTSPOTS
    hs_rows = ""
    for _, h in hotspots_df.iterrows():
        hs_rows += f"""
        <tr>
            <td style="font-weight:600;">{h['site']}</td>
            <td style="font-weight:600;">{h['activity']}</td>
            <td>{int(h['total_reports'])}</td>
            <td><span class="badge badge-sif">{int(h['sif_reports'])}</span></td>
            <td style="font-weight:700;color:#EF4444;">{int(h['sif_reports'])} / {int(h['total_reports'])} ({h['sif_density']:.1f}%)</td>
            <td>{h['top_hazard']}</td>
            <td>{h['top_barrier']}</td>
        </tr>
        """

    render_html(f"""
    <div class="saas-card" style="margin-top:10px;">
        <div style="margin-bottom:8px;">
            <div style="font-size:16px;font-weight:700;color:#16181D;">HSE Intervention Hotspots</div>
            <div style="font-size:12px;color:#737985;">Site and activity combinations with elevated concentrations of potential SIF precursors.</div>
        </div>
        <table class="saas-table">
            <thead>
                <tr>
                    <th>Site</th>
                    <th>Activity</th>
                    <th>Total Reports</th>
                    <th>SIF Reports</th>
                    <th>SIF Density</th>
                    <th>Top Hazard</th>
                    <th>Top Barrier</th>
                </tr>
            </thead>
            <tbody>{hs_rows}</tbody>
        </table>
    </div>
    """)


# ======================================================
# 7. LIFE-SAVING RULES PAGE
# ======================================================

def page_life_saving_rules():
    render_top_header("Life-Saving Rule Intelligence")

    try:
        lsr_df = get_life_saving_rule_summary()
    except Exception as exc:
        st.error(f"Unable to load Life-Saving Rule summary: {exc}")
        return

    icon_map = {
        "Bypassing Safety Controls": "🛡️",
        "Confined Space": "🛢️",
        "Driving": "🚛",
        "Energy Isolation": "⚡",
        "Hot Work": "🔥",
        "Line of Fire": "🎯",
        "Safe Mechanical Lifting": "🏗️",
        "Work Authorization": "📋",
        "Working at Height": "🪜",
    }

    max_cnt = max(int(lsr_df["sif_reports"].max()), 1) if not lsr_df.empty else 1

    render_html("""
    <div class="chart-header-box">
        <div class="chart-title">IOGP Life-Saving Rule Triggers (SIF Potential Reports Only)</div>
        <div class="chart-subtitle">Real rule frequency from src.backend_adapter.get_life_saving_rule_summary()</div>
    </div>
    """)
    fig_l = go.Figure(go.Bar(
        x=lsr_df["life_saving_rule"],
        y=lsr_df["sif_reports"],
        marker=dict(color="#2457F5", cornerradius=6),
        width=0.38,
        text=lsr_df["sif_reports"],
        textposition="outside",
    ))
    fig_l.update_layout(height=230, margin=dict(l=8, r=8, t=12, b=8), paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", yaxis=dict(range=[0, max_cnt + 2]))
    st.plotly_chart(fig_l, width="stretch", config={"displayModeBar": False})

    records = lsr_df.to_dict("records")
    for i in range(0, len(records), 3):
        cols = st.columns(3)
        for col, item in zip(cols, records[i:i + 3]):
            r_name = item["life_saving_rule"]
            r_cnt = int(item["sif_reports"])
            pct = int(round(r_cnt / max_cnt * 100))
            icon = icon_map.get(r_name, "🛡️")
            with col:
                render_html(f"""
                <div class="saas-card" style="padding:16px 18px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="width:32px;height:32px;border-radius:8px;background:#EEF2FF;display:flex;align-items:center;justify-content:center;font-size:15px;">{icon}</div>
                            <div style="font-size:14px;font-weight:700;color:#16181D;">{r_name}</div>
                        </div>
                        <span class="badge badge-sif">{r_cnt} SIF Reports</span>
                    </div>
                    <div style="height:6px;background:#F1F3F7;border-radius:999px;overflow:hidden;margin-top:6px;">
                        <div style="width:{pct}%;height:100%;background:#2457F5;border-radius:999px;"></div>
                    </div>
                </div>
                """)

    render_html('<div style="font-size:12px;color:#737985;">Prototype analysis using demonstration safety-report data.</div>')


# ======================================================
# 8. PRECURSOR PATTERNS PAGE
# ======================================================

def page_precursor_patterns():
    render_top_header("Recurring SIF Precursor Patterns")

    try:
        patterns_df = get_precursor_patterns()
    except Exception as exc:
        st.error(f"Unable to load precursor patterns: {exc}")
        return

    render_html("""
    <div class="saas-card" style="border-left:4px solid #2457F5;margin-bottom:14px;">
        <div style="font-size:13.5px;font-weight:700;color:#2457F5;margin-bottom:3px;">Why this matters</div>
        <div style="font-size:12.5px;color:#16181D;">
            Repeated precursor combinations can help HSE teams identify recurring critical-control weaknesses before a serious event occurs.
        </div>
    </div>
    """)

    if not patterns_df.empty:
        top_p = patterns_df.iloc[0]
        sites_str = ", ".join(top_p["sites"]) if isinstance(top_p.get("sites"), list) else str(top_p.get("site", ""))
        render_html(f"""
        <div class="saas-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <div style="font-size:15px;font-weight:700;color:#16181D;">
                    Top Recurring Pattern ({top_p['pattern_id']} • {top_p['pattern_type']}) — Affected Sites: {sites_str}
                </div>
                <span class="badge badge-sif">{top_p['status']}</span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
                <div style="flex:1;background:#F7F8FA;border:1px solid #E8EAF0;border-radius:10px;padding:10px 12px;">
                    <div style="font-size:10px;color:#737985;font-weight:600;">Activity</div>
                    <div style="font-size:13px;font-weight:700;color:#16181D;">{top_p['activity']}</div>
                </div>
                <div style="color:#2457F5;font-weight:700;">↓</div>
                <div style="flex:1;background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;padding:10px 12px;">
                    <div style="font-size:10px;color:#EF4444;font-weight:600;">Hazard</div>
                    <div style="font-size:13px;font-weight:700;color:#EF4444;">{top_p['hazard']}</div>
                </div>
                <div style="color:#2457F5;font-weight:700;">↓</div>
                <div style="flex:1;background:#F7F8FA;border:1px solid #E8EAF0;border-radius:10px;padding:10px 12px;">
                    <div style="font-size:10px;color:#737985;font-weight:600;">Critical Barrier</div>
                    <div style="font-size:13px;font-weight:700;color:#16181D;">{top_p['barrier']}</div>
                </div>
                <div style="color:#2457F5;font-weight:700;">↓</div>
                <div style="flex:0.7;background:#EEF2FF;border:1px solid #C7D2FE;border-radius:10px;padding:10px 12px;text-align:center;">
                    <div style="font-size:10px;color:#2457F5;font-weight:600;">Occurrences</div>
                    <div style="font-size:14px;font-weight:700;color:#2457F5;">{int(top_p['occurrences'])}</div>
                </div>
            </div>
        </div>
        """)

    p_rows = ""
    for _, p in patterns_df.iterrows():
        status_val = str(p["status"])
        if status_val == "Recurring Pattern":
            s_badge = '<span class="badge badge-sif">Recurring Pattern</span>'
        elif status_val == "Repeated Pattern":
            s_badge = '<span class="badge badge-review">Repeated Pattern</span>'
        else:
            s_badge = '<span class="badge badge-grey">Single Occurrence</span>'

        sites_disp = ", ".join(p["sites"]) if isinstance(p.get("sites"), list) else str(p.get("site", ""))
        acts_disp = ", ".join(p["activities"]) if isinstance(p.get("activities"), list) else str(p.get("activity", ""))

        p_rows += f"""
        <tr>
            <td style="font-weight:700;color:#2457F5;">{p['pattern_id']}</td>
            <td><span class="badge badge-blue">{p['pattern_type']}</span></td>
            <td>{sites_disp}</td>
            <td style="font-weight:600;">{acts_disp}</td>
            <td>{p['hazard']}</td>
            <td>{p['barrier']}</td>
            <td style="font-weight:700;color:#16181D;">{int(p['occurrences'])}</td>
            <td>{s_badge}</td>
        </tr>
        """

    render_html(f"""
    <div class="saas-card">
        <div style="font-size:15.5px;font-weight:700;color:#16181D;margin-bottom:10px;">
            Detected SIF Precursor Patterns ({len(patterns_df)} patterns)
        </div>
        <table class="saas-table">
            <thead>
                <tr>
                    <th>Pattern ID</th>
                    <th>Pattern Type</th>
                    <th>Affected Sites</th>
                    <th>Activity / Activities</th>
                    <th>Hazard</th>
                    <th>Critical Barrier</th>
                    <th>Occurrences</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>{p_rows}</tbody>
        </table>
    </div>
    """)


# ======================================================
# 9. REVIEW QUEUE PAGE
# ======================================================

def page_review_queue():
    render_top_header("Human Review Queue")

    try:
        review_df = get_review_queue()
    except Exception as exc:
        st.error(f"Unable to load review queue: {exc}")
        return

    t_col, p_col = st.columns([64, 36])

    with t_col:
        q_rows = ""
        for _, r in review_df.iterrows():
            rid = str(r["report_id"])
            override = st.session_state.review_overrides.get(rid, {})
            status_val = override.get("status", str(r.get("review_status") or "Pending"))
            badge_html = (
                '<span class="badge badge-nonsif">Completed</span>'
                if status_val == "Completed"
                else '<span class="badge badge-review">Pending</span>'
            )
            q_rows += f"""
            <tr>
                <td style="font-weight:700;color:#2457F5;">{rid}</td>
                <td>{r['site']}</td>
                <td style="max-width:200px;">{r['report_text']}</td>
                <td>{r['context']}</td>
                <td><span class="badge badge-sif">{r['review_reason']}</span></td>
                <td>{format_priority_badge(str(r['priority']))}</td>
                <td>{r['hazard']}</td>
                <td>{r['barrier']}</td>
                <td>{badge_html}</td>
                <td><span class="action-pill">View</span></td>
            </tr>
            """

        render_html(f"""
        <div class="saas-card">
            <div style="font-size:15.5px;font-weight:700;color:#16181D;margin-bottom:10px;">
                Needs Review Reports ({len(review_df)} uncertain / contradictory reports)
            </div>
            <table class="saas-table">
                <thead>
                    <tr>
                        <th>Report ID</th>
                        <th>Site</th>
                        <th>Report</th>
                        <th>Context</th>
                        <th>Review Reason</th>
                        <th>Priority</th>
                        <th>Hazard</th>
                        <th>Barrier</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>{q_rows}</tbody>
            </table>
        </div>
        """)

    with p_col:
        if not review_df.empty:
            sel_id = st.selectbox("Select Report ID for HSE Review", review_df["report_id"].tolist(), index=0)
            row = review_df[review_df["report_id"] == sel_id].iloc[0]
            render_html(f"""
            <div class="saas-card" style="border-top:3px solid #2457F5;">
                <div style="font-size:15px;font-weight:700;color:#16181D;margin-bottom:8px;">Review Panel — {sel_id}</div>
                <div style="font-size:12px;line-height:1.6;color:#16181D;">
                    <div><strong>AI Result:</strong> <span class="badge badge-review">Needs Review</span></div>
                    <div><strong>ML Classification:</strong> {row['model_prediction']}</div>
                    <div><strong>Context:</strong> {row['context']}</div>
                    <div><strong>Hazard:</strong> {row['hazard']}</div>
                    <div><strong>Barrier:</strong> {row['barrier']}</div>
                    <div><strong>Evidence:</strong> {row['evidence']}</div>
                    <div><strong>Review Reason:</strong> {row['review_reason']}</div>
                </div>
            </div>
            """)

            decision = st.selectbox(
                "Reviewer Decision",
                ["Confirm SIF Potential", "Confirm Non-SIF Potential", "Request More Information"],
            )
            rev_name = st.text_input("Reviewer Name", value="HSE Officer")
            rev_comment = st.text_area("Reviewer Comment", height=72)
            if st.button("Submit Review", key="btn_submit_rev_session", type="primary", width="stretch"):
                st.session_state.review_overrides[str(sel_id)] = {
                    "status": "Completed",
                    "decision": decision,
                    "name": rev_name,
                    "comment": rev_comment,
                }
                st.success(f"Recorded review decision ({decision}) for {sel_id} in session_state.")


# ======================================================
# 10. SETTINGS PAGE
# ======================================================

def page_settings():
    render_top_header("Settings")

    modules = [
        "ML Classifier",
        "Safety Rule Engine",
        "Hazard / Barrier Detection",
        "IOGP Life-Saving Rule Mapping",
        "Precursor Pattern Engine",
        "Human Review Workflow",
        "Batch Analysis",
        "Analytics Adapter",
    ]

    for i in range(0, len(modules), 4):
        cols = st.columns(4)
        for col, mod_name in zip(cols, modules[i:i + 4]):
            with col:
                render_html(f"""
                <div class="saas-card" style="padding:16px 18px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;">
                        <div style="font-size:14px;font-weight:700;color:#16181D;">{mod_name}</div>
                        <div style="display:flex;align-items:center;gap:6px;background:#ECFDF5;padding:3px 10px;border-radius:999px;border:1px solid #A7F3D0;">
                            <span style="width:8px;height:8px;border-radius:50%;background:#22A06B;display:inline-block;"></span>
                            <span style="font-size:11px;font-weight:600;color:#22A06B;">Online</span>
                        </div>
                    </div>
                </div>
                """)

    render_html("""
    <div class="saas-card" style="border-left:4px solid #2457F5;">
        <div style="font-size:15px;font-weight:700;color:#16181D;margin-bottom:6px;">Prototype validation on demonstration dataset</div>
        <div style="font-size:12.5px;color:#737985;line-height:1.6;">
            <div>• <strong>Binary classification coverage:</strong> approximately 91.7% (55 / 60 demonstration reports)</div>
            <div>• <strong>Needs Review / abstention:</strong> approximately 8.3% (5 / 60 demonstration reports)</div>
            <div>• <strong>Note:</strong> Production deployment requires validation on appropriately labelled representative operational HSSE data.</div>
        </div>
    </div>
    """)


# ======================================================
# PAGE ROUTER
# ======================================================

page = st.session_state.active_page
if page == "Dashboard":
    page_dashboard()
elif page == "Report Analyzer":
    page_report_analyzer()
elif page == "Batch Analysis":
    page_batch_analysis()
elif page == "Reports":
    page_reports()
elif page == "SIF Analysis":
    page_sif_analysis()
elif page == "Site & Activity Risk":
    page_site_activity_risk()
elif page == "Life-Saving Rules":
    page_life_saving_rules()
elif page == "Precursor Patterns":
    page_precursor_patterns()
elif page == "Review Queue":
    page_review_queue()
elif page == "Settings":
    page_settings()
else:
    page_dashboard()

render_disclaimer_footer()
