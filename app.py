"""
Redrob Hackathon — Intelligent Candidate Ranking
Enterprise-grade UI with Excel/CSV/JSON input, tabbed analytics, dark/light theme, and professional design.
"""
import json
import os
import sys
import time
from collections import Counter

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))
from ranker import process_candidates

st.set_page_config(
    page_title="Redrob Candidate Ranker - Enterprise",
    page_icon="\U0001F3C6",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme ───────────────────────────────────────────────────────────────────

THEME = st.session_state.get("theme", "dark")

# Plotly colors — resolved here because CSS variables don't work in Plotly's SVG output
if THEME == "dark":
    P = {
        "chart_bg": "rgba(0,0,0,0)",
        "text_primary": "#e2e8f0",
        "text_muted": "#64748b",
        "chart_grid": "rgba(255,255,255,0.03)",
        "success": "#34d399",
        "warning": "#fbbf24",
        "danger": "#f87171",
        "bg_primary": "#0a0e17",
    }
else:
    P = {
        "chart_bg": "rgba(0,0,0,0)",
        "text_primary": "#0f172a",
        "text_muted": "#64748b",
        "chart_grid": "rgba(0,0,0,0.06)",
        "success": "#10b981",
        "warning": "#d97706",
        "danger": "#ef4444",
        "bg_primary": "#f8fafc",
    }

# CSS variable definitions for both themes
DARK_VARS = """
    --bg-primary: #0a0e17;
    --bg-secondary: #0f1629;
    --bg-tertiary: #1a1f3a;
    --bg-card: rgba(30,41,59,0.8);
    --bg-card-alt: rgba(15,23,42,0.8);
    --bg-card-hover: rgba(30,41,59,0.6);
    --bg-welcome: rgba(30,41,59,0.6);
    --bg-preview: rgba(30,41,59,0.4);
    --bg-sample: rgba(255,255,255,0.02);
    --sidebar-bg: #0f1629;
    --text-primary: #f1f5f9;
    --text-secondary: #e2e8f0;
    --text-muted: #64748b;
    --text-muted-dark: #94a3b8;
    --text-dim: #334155;
    --text-dim2: #475569;
    --border-color: rgba(255,255,255,0.06);
    --border-light: rgba(255,255,255,0.05);
    --border-card: rgba(255,255,255,0.05);
    --border-hover: rgba(59,130,246,0.2);
    --accent-blue: #3b82f6;
    --accent-blue-light: #60a5fa;
    --accent-blue-dark: #2563eb;
    --accent-purple: #8b5cf6;
    --success: #34d399;
    --warning: #fbbf24;
    --danger: #f87171;
    --gradient-blue: linear-gradient(135deg, #3b82f6, #8b5cf6);
    --gradient-nav: linear-gradient(135deg, #0f1629 0%, #1a1f3a 100%);
    --shadow: 0 8px 25px rgba(59,130,246,0.08);
    --chart-bg: rgba(0,0,0,0);
    --chart-grid: rgba(255,255,255,0.03);
    --badge-clean-bg: rgba(52,211,153,0.12);
    --badge-suspicious-bg: rgba(251,191,36,0.12);
    --badge-honeypot-bg: rgba(248,113,113,0.12);
    --score-bar-bg: rgba(255,255,255,0.06);
"""

LIGHT_VARS = """
    --bg-primary: #f8fafc;
    --bg-secondary: #ffffff;
    --bg-tertiary: #f1f5f9;
    --bg-card: rgba(255,255,255,0.95);
    --bg-card-alt: rgba(248,250,252,0.95);
    --bg-card-hover: rgba(248,250,252,0.85);
    --bg-welcome: rgba(255,255,255,0.8);
    --bg-preview: rgba(255,255,255,0.7);
    --bg-sample: rgba(0,0,0,0.02);
    --sidebar-bg: #ffffff;
    --text-primary: #0f172a;
    --text-secondary: #1e293b;
    --text-muted: #64748b;
    --text-muted-dark: #475569;
    --text-dim: #94a3b8;
    --text-dim2: #cbd5e1;
    --border-color: rgba(0,0,0,0.08);
    --border-light: rgba(0,0,0,0.06);
    --border-card: rgba(0,0,0,0.06);
    --border-hover: rgba(59,130,246,0.3);
    --accent-blue: #2563eb;
    --accent-blue-light: #3b82f6;
    --accent-blue-dark: #1d4ed8;
    --accent-purple: #7c3aed;
    --success: #10b981;
    --warning: #d97706;
    --danger: #ef4444;
    --gradient-blue: linear-gradient(135deg, #2563eb, #7c3aed);
    --gradient-nav: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
    --shadow: 0 8px 25px rgba(0,0,0,0.06);
    --chart-bg: rgba(0,0,0,0);
    --chart-grid: rgba(0,0,0,0.06);
    --badge-clean-bg: rgba(16,185,129,0.1);
    --badge-suspicious-bg: rgba(217,119,6,0.1);
    --badge-honeypot-bg: rgba(239,68,68,0.1);
    --score-bar-bg: rgba(0,0,0,0.08);
"""

# Inject theme variables
theme_vars = DARK_VARS if THEME == "dark" else LIGHT_VARS
st.markdown(f"<style>:root {{{theme_vars}}}</style>", unsafe_allow_html=True)

# ── Enterprise Theme ─────────────────────────────────────────────────────────

ENTERPRISE_CSS = f"""
<style>
    /* ── Font import must be first ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Base ── */
    .stApp {{ background: var(--bg-primary); }}
    .stApp > header {{ background: transparent !important; }}
    .stApp > header [data-testid="stDecoration"] {{ display: none; }}

    /* ── Typography ── */
    html, body, [class*="css"] {{ font-family: 'Inter', -apple-system, sans-serif; }}

    /* ── Theme toggle icon ── */
    .theme-toggle-icon {{
        font-size: 1.1rem;
        transition: transform 0.3s ease;
        display: inline-block;
    }}
    .theme-toggle-icon:hover {{
        transform: rotate(30deg);
    }}

    /* ── Responsive Container ── */
    .main > .block-container {{
        max-width: 100%;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        transition: padding 0.3s ease;
    }}

    /* ── Top Nav Bar ── */
    .nav-bar {{
        background: var(--gradient-nav);
        border-bottom: 1px solid var(--border-color);
        padding: 0.8rem 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: -1rem -1rem 1rem -1rem;
        gap: 0.5rem;
        transition: padding 0.3s ease;
    }}
    .nav-brand {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        min-width: 0;
    }}
    .nav-logo {{
        flex-shrink: 0;
        width: 36px; height: 36px;
        background: var(--gradient-blue);
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2rem;
    }}
    .nav-title {{
        font-weight: 700;
        font-size: clamp(0.9rem, 2.5vw, 1.2rem);
        color: var(--text-primary);
        letter-spacing: -0.3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .nav-subtitle {{
        font-size: clamp(0.65rem, 1.5vw, 0.8rem);
        color: var(--text-muted);
        margin-top: -0.1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .nav-version {{
        flex-shrink: 0;
        background: rgba(59,130,246,0.15);
        color: var(--accent-blue-light);
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: clamp(0.6rem, 1.2vw, 0.7rem);
        font-weight: 600;
        white-space: nowrap;
    }}

    /* ── Enterprise Metric Cards ── */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.6rem;
        margin-bottom: 1.5rem;
    }}
    .metric-card {{
        background: var(--bg-card);
        backdrop-filter: blur(8px);
        border: 1px solid var(--border-card);
        border-radius: 12px;
        padding: clamp(0.8rem, 1.5vw, 1.2rem) clamp(0.7rem, 1.2vw, 1rem);
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
        -webkit-tap-highlight-color: transparent;
    }}
    .metric-card:active {{
        transform: scale(0.97);
    }}
    @media (hover: hover) {{
        .metric-card:hover {{
            border-color: rgba(59,130,246,0.3);
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }}
    }}
    .metric-card .accent-line {{
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: var(--gradient-blue);
    }}
    .metric-value {{
        font-size: clamp(1.2rem, 3.5vw, 1.8rem);
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.5px;
        line-height: 1.2;
    }}
    .metric-label {{
        font-size: clamp(0.6rem, 1.5vw, 0.78rem);
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 0.25rem;
    }}
    .metric-trend {{ font-size: 0.7rem; margin-top: 0.3rem; }}
    .metric-trend.up {{ color: var(--success); }}
    .metric-trend.down {{ color: var(--danger); }}

    /* ── Enterprise Data Cards ── */
    .rank-card {{
        background: var(--bg-card-hover);
        border: 1px solid var(--border-card);
        border-radius: 10px;
        padding: clamp(0.6rem, 1.2vw, 1rem) clamp(0.8rem, 1.5vw, 1.2rem);
        margin-bottom: 0.5rem;
        transition: all 0.25s ease;
        animation: slideIn 0.35s ease-out;
        -webkit-tap-highlight-color: transparent;
    }}
    .rank-card:active {{
        transform: scale(0.99);
    }}
    @media (hover: hover) {{
        .rank-card:hover {{
            border-color: var(--border-hover);
            background: var(--bg-card);
            transform: translateX(3px);
        }}
    }}

    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateX(-10px); }}
        to   {{ opacity: 1; transform: translateX(0); }}
    }}

    .rank-number {{
        font-weight: 800;
        font-size: clamp(0.9rem, 2vw, 1.2rem);
        color: var(--accent-blue);
        min-width: clamp(1.8rem, 4vw, 2.5rem);
        flex-shrink: 0;
    }}
    .candidate-name {{
        font-weight: 600;
        color: var(--text-secondary);
        font-size: clamp(0.8rem, 1.5vw, 0.95rem);
        word-break: break-word;
    }}
    .candidate-meta {{
        color: var(--text-muted);
        font-size: clamp(0.65rem, 1.2vw, 0.8rem);
        word-break: break-word;
    }}
    .score-text {{
        font-family: 'JetBrains Mono', 'SF Mono', monospace;
        font-weight: 600;
        white-space: nowrap;
    }}

    /* ── Badges ── */
    .badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.15rem 0.55rem;
        border-radius: 6px;
        font-size: clamp(0.6rem, 1.2vw, 0.7rem);
        font-weight: 600;
        letter-spacing: 0.3px;
        white-space: nowrap;
    }}
    .badge-clean {{ background: var(--badge-clean-bg); color: var(--success); }}
    .badge-suspicious {{ background: var(--badge-suspicious-bg); color: var(--warning); }}
    .badge-honeypot {{ background: var(--badge-honeypot-bg); color: var(--danger); animation: pulse 2s infinite; }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}

    /* ── Progress bar ── */
    .score-bar {{
        height: 3px;
        border-radius: 3px;
        background: var(--score-bar-bg);
        margin: 0.4rem 0 0.3rem 0;
        overflow: hidden;
    }}
    .score-bar-fill {{
        height: 100%;
        border-radius: 3px;
        transition: width 1s ease;
    }}

    /* ── Tab styling ── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.25rem;
        border-bottom: 1px solid var(--border-color);
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        flex-wrap: nowrap;
    }}
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {{ display: none; }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: var(--text-muted) !important;
        font-weight: 500;
        font-size: clamp(0.7rem, 1.5vw, 0.85rem);
        padding: clamp(0.4rem, 1vw, 0.5rem) clamp(0.5rem, 1.5vw, 1rem);
        border-radius: 8px 8px 0 0;
        transition: all 0.2s;
        white-space: nowrap;
        flex-shrink: 0;
        -webkit-tap-highlight-color: transparent;
    }}
    @media (hover: hover) {{
        .stTabs [data-baseweb="tab"]:hover {{
            color: var(--text-secondary) !important;
            background: rgba(128,128,128,0.03) !important;
        }}
    }}
    .stTabs [aria-selected="true"] {{
        color: var(--accent-blue-light) !important;
        border-bottom: 2px solid var(--accent-blue) !important;
    }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {{
        background: var(--sidebar-bg);
        border-right: 1px solid var(--border-light);
    }}
    section[data-testid="stSidebar"] .stButton button {{
        border-radius: 8px;
        font-weight: 500;
        font-size: clamp(0.75rem, 1.2vw, 0.85rem);
        min-height: 44px;
        -webkit-tap-highlight-color: transparent;
    }}
    section[data-testid="stSidebar"] .stButton button[kind="primary"] {{
        background: var(--gradient-blue);
        color: white;
        border: none;
    }}
    section[data-testid="stSidebar"] .stButton button[kind="secondary"] {{
        background: rgba(128,128,128,0.05);
        color: var(--text-muted-dark);
        border: 1px solid var(--border-light);
    }}
    .sidebar-title {{
        font-weight: 700;
        font-size: clamp(0.75rem, 1.2vw, 0.85rem);
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 0.75rem;
    }}

    /* ── Dividers ── */
    .divider {{
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(59,130,246,0.15), transparent);
        margin: 1.2rem 0;
    }}

    /* ── Footer ── */
    .footer {{
        margin-top: 2rem;
        padding: 1rem 0;
        border-top: 1px solid var(--border-light);
        text-align: center;
        color: var(--text-dim);
        font-size: clamp(0.6rem, 1.2vw, 0.75rem);
    }}

    /* ── Plotly chart responsiveness ── */
    .stPlotlyChart, .js-plotly-plot, .plot-container {{
        width: 100% !important;
        max-width: 100% !important;
    }}

    /* ── File uploader responsiveness ── */
    .stFileUploader [data-testid="stFileUploadDropzone"] {{
        padding: clamp(0.5rem, 2vw, 1rem) !important;
        min-height: 44px;
    }}
    .stFileUploader [data-testid="stFileUploadDropzone"] small {{
        font-size: clamp(0.6rem, 1.2vw, 0.75rem) !important;
    }}

    /* ── Text input / slider responsiveness ── */
    .stTextInput input, .stSlider [data-baseweb="slider"] {{
        font-size: clamp(0.75rem, 1.2vw, 0.85rem) !important;
    }}

    /* ── Column stacking on narrow screens ── */
    @media (max-width: 640px) {{
        .row-widget.stColumns {{
            flex-direction: column !important;
        }}
        .row-widget.stColumns > div {{
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 0 !important;
        }}
    }}

    /* ── Tablet: 641px - 1024px ── */
    @media (min-width: 641px) and (max-width: 1024px) {{
        .main > .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        .nav-bar {{
            padding: 0.6rem 1rem;
            margin: -1rem -1rem 0.8rem -1rem;
        }}
        .metric-grid {{
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 0.5rem;
        }}
    }}

    /* ── Mobile landscape: 481px - 640px ── */
    @media (min-width: 481px) and (max-width: 640px) {{
        .main > .block-container {{
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }}
        .nav-bar {{
            padding: 0.5rem 0.75rem;
            margin: -1rem -1rem 0.6rem -1rem;
            flex-wrap: wrap;
            gap: 0.3rem;
        }}
        .nav-subtitle {{ display: none; }}
        .metric-grid {{
            grid-template-columns: repeat(2, 1fr);
            gap: 0.4rem;
        }}
        .metric-card {{ padding: 0.7rem 0.6rem; }}
        .rank-card > div:first-child {{ gap: 0.5rem !important; }}
    }}

    /* ── Mobile portrait: <= 480px ── */
    @media (max-width: 480px) {{
        .main > .block-container {{
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }}
        .nav-bar {{
            padding: 0.4rem 0.5rem;
            margin: -1rem -1rem 0.5rem -1rem;
            flex-wrap: wrap;
        }}
        .nav-logo {{ width: 28px; height: 28px; font-size: 0.9rem; }}
        .nav-subtitle {{ display: none; }}
        .metric-grid {{
            grid-template-columns: repeat(2, 1fr);
            gap: 0.35rem;
        }}
        .metric-card {{ padding: 0.6rem 0.5rem; border-radius: 8px; }}
        .metric-card .accent-line {{ height: 2px; }}
        .rank-card {{ padding: 0.5rem 0.6rem; border-radius: 8px; }}
        .rank-card > div:first-child {{ flex-wrap: wrap; gap: 0.3rem !important; }}
        .rank-number {{ min-width: 1.5rem; }}
        .stTabs [data-baseweb="tab"] {{ font-size: 0.7rem; padding: 0.3rem 0.5rem; }}
        .nav-version {{ display: none; }}
        .footer {{ font-size: 0.55rem; padding: 0.5rem 0; }}
    }}

    /* ── Large screens: > 1440px ── */
    @media (min-width: 1441px) {{
        .main > .block-container {{
            max-width: 1600px;
            margin: 0 auto;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }}
        .nav-bar {{ padding: 0.8rem 2rem; }}
        .metric-grid {{
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
        }}
    }}

    /* ── Ultra-wide: > 1900px ── */
    @media (min-width: 1901px) {{
        .main > .block-container {{
            max-width: 1800px;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
        }}
        .metric-grid {{
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        }}
    }}
</style>"""

st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)

# ── Nav bar ─────────────────────────────────────────────────────────────────

st.markdown("""
<div class="nav-bar">
    <div class="nav-brand">
        <div class="nav-logo">\U0001F3C6</div>
        <div>
            <div class="nav-title">Redrob Candidate Ranker</div>
            <div class="nav-subtitle">Intelligent Candidate Discovery &bull; Enterprise Edition</div>
        </div>
    </div>
    <div class="nav-version">v2.0 &bull; 11 honeypot checks</div>
</div>
""", unsafe_allow_html=True)

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_candidates.json")


# ── Helper functions ────────────────────────────────────────────────────────

def run_ranker(candidates, source_label):
    if not candidates:
        st.error("No candidates found.")
        return
    start = time.time()
    rankings = process_candidates(candidates)
    elapsed = time.time() - start

    st.session_state["rankings"] = rankings
    st.session_state["elapsed"] = elapsed
    st.session_state["total"] = len(candidates)
    st.session_state["source"] = source_label
    st.session_state["candidates_data"] = candidates
    st.session_state["active_tab"] = "Dashboard"
    st.toast(f"\u2705 Ranked {len(candidates)} candidates in {elapsed:.2f}s", icon="\U0001F3C6")


def parse_json_input(raw):
    data = json.loads(raw)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "candidate_id" in data:
            return [data]
        for key in ("candidates", "data", "results", "profiles"):
            if key in data and isinstance(data[key], list):
                return data[key]
    raise ValueError("JSON must be an array of candidate objects")


def parse_tabular_data(df):
    """Convert a flat DataFrame to the nested candidate schema."""
    candidates = []
    for _, row in df.iterrows():
        r = row.fillna("").to_dict()
        c = {
            "candidate_id": str(r.get("candidate_id", r.get("id", f"CAND_{len(candidates)+1:07d}"))),
            "profile": {
                "anonymized_name": str(r.get("name", r.get("anonymized_name", "Unknown"))),
                "headline": str(r.get("headline", "")),
                "summary": str(r.get("summary", "")),
                "location": str(r.get("location", "")),
                "country": str(r.get("country", "India")),
                "years_of_experience": float(r.get("years_of_experience", r.get("experience", 0)) or 0),
                "current_title": str(r.get("current_title", r.get("title", "Engineer"))),
                "current_company": str(r.get("current_company", r.get("company", ""))),
                "current_company_size": str(r.get("current_company_size", "501-1000")),
                "current_industry": str(r.get("current_industry", r.get("industry", "Technology"))),
            },
            "career_history": [{
                "company": str(r.get("company", r.get("current_company", ""))),
                "title": str(r.get("title", r.get("current_title", "Engineer"))),
                "start_date": str(r.get("start_date", "2020-01-01")),
                "end_date": str(r.get("end_date", "")),
                "duration_months": int(float(r.get("duration_months", 0) or 0)),
                "is_current": bool(r.get("is_current", True)),
                "industry": str(r.get("industry", "Technology")),
                "company_size": str(r.get("company_size", "501-1000")),
                "description": str(r.get("description", r.get("summary", ""))),
            }],
            "education": [{
                "institution": str(r.get("institution", "University")),
                "degree": str(r.get("degree", "B.Tech")),
                "field_of_study": str(r.get("field_of_study", "Computer Science")),
                "start_year": int(float(r.get("start_year", 2015) or 2015)),
                "end_year": int(float(r.get("end_year", 2019) or 2019)),
                "grade": str(r.get("grade", "")),
                "tier": str(r.get("tier", "tier_3")),
            }],
            "skills": [],
            "redrob_signals": {
                "profile_completeness_score": float(r.get("profile_completeness", 50)),
                "signup_date": str(r.get("signup_date", "2020-01-01")),
                "last_active_date": str(r.get("last_active_date", "2025-01-01")),
                "open_to_work_flag": bool(r.get("open_to_work", True)),
                "profile_views_received_30d": int(float(r.get("profile_views", 0) or 0)),
                "applications_submitted_30d": int(float(r.get("applications", 0) or 0)),
                "recruiter_response_rate": float(r.get("response_rate", 0.5) or 0.5),
                "avg_response_time_hours": float(r.get("avg_response_time", 48) or 48),
                "skill_assessment_scores": {},
                "connection_count": int(float(r.get("connections", 100) or 100)),
                "endorsements_received": int(float(r.get("endorsements", 10) or 10)),
                "notice_period_days": int(float(r.get("notice_period", 60) or 60)),
                "expected_salary_range_inr_lpa": {
                    "min": float(r.get("salary_min", r.get("expected_salary_min", 10)) or 10),
                    "max": float(r.get("salary_max", r.get("expected_salary_max", 30)) or 30),
                },
                "preferred_work_mode": str(r.get("work_mode", "remote")),
                "willing_to_relocate": bool(r.get("willing_relocate", True)),
                "github_activity_score": float(r.get("github_score", 0) or 0),
                "search_appearance_30d": int(float(r.get("search_appearances", 50) or 50)),
                "saved_by_recruiters_30d": int(float(r.get("saved_by_recruiters", 5) or 5)),
                "interview_completion_rate": float(r.get("interview_rate", 0.7) or 0.7),
                "offer_acceptance_rate": float(r.get("offer_rate", 0.5) or 0.5),
                "verified_email": bool(r.get("verified_email", True)),
                "verified_phone": bool(r.get("verified_phone", True)),
                "linkedin_connected": bool(r.get("linkedin", True)),
            },
        }

        # Parse skills from a comma-separated string if provided
        skills_raw = r.get("skills", "")
        if isinstance(skills_raw, str) and skills_raw.strip():
            for sk in skills_raw.split(","):
                sk = sk.strip()
                if sk:
                    c["skills"].append({"name": sk, "proficiency": "intermediate", "endorsements": 5})

        candidates.append(c)
    return candidates


def make_metric_card(value, label, accent_color=None, trend=None):
    accent = accent_color or "var(--accent-blue)"
    trend_html = ""
    if trend:
        cls = "up" if trend > 0 else "down"
        arrow = "\u25B2" if trend > 0 else "\u25BC"
        trend_html = f'<div class="metric-trend {cls}">{arrow} {abs(trend)}%</div>'
    return f"""
    <div class="metric-card">
        <div class="accent-line" style="background:linear-gradient(90deg, {accent}, var(--accent-purple));"></div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {trend_html}
    </div>
    """


def badge_html(penalty):
    if penalty < 0.3:
        return '<span class="badge badge-honeypot">HONEYPOT</span>'
    elif penalty < 0.8:
        return '<span class="badge badge-suspicious">SUSPICIOUS</span>'
    return '<span class="badge badge-clean">VERIFIED</span>'


def _render_rank_card(rank, score, cid, reasoning, penalty, issues, large_style=False):
    """Build a rank card HTML string. Handles HTML escaping internally."""
    pct = min(score * 100, 100)
    bc = P["danger"] if penalty < 0.3 else (P["warning"] if penalty < 0.8 else P["success"])
    fs = "1.1rem" if large_style else "0.95rem"
    rl = 120 if large_style else 150
    delay = (rank % 20) * 0.02

    safe_cid = cid.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe_reasoning = reasoning[:rl].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    issues_html = ""
    if issues:
        safe_issues = "; ".join(issues[:2]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        issues_html = f'<div style="color:{P["danger"]};font-size:0.75rem;margin-top:0.2rem;">\u26A0 {safe_issues}</div>'

    delay_style = f'style="animation-delay:{delay}s"' if not large_style else ""

    return (
        f'<div class="rank-card" {delay_style}>'
        f'<div style="display:flex;align-items:center;gap:0.8rem;">'
        f'<div class="rank-number" style="min-width:2rem;">#{rank}</div>'
        f'<div style="flex:1;">'
        f'<div class="candidate-name">{safe_cid}</div>'
        f'<div class="candidate-meta">{safe_reasoning}</div>'
        f'{issues_html}'
        f'</div>'
        f'<div style="text-align:right;">'
        f'<div class="score-text" style="color:{bc};font-size:{fs};">{score:.4f}</div>'
        f'{badge_html(penalty)}'
        f'</div>'
        f'</div>'
        f'<div class="score-bar"><div class="score-bar-fill" style="width:{pct:.1f}%;background:{bc};"></div></div>'
        f'</div>'
    )


def find_candidate_by_cid(cid):
    """Look up candidate data by candidate_id in session state."""
    candidates = st.session_state.get("candidates_data", [])
    for c in candidates:
        if c.get("candidate_id") == cid:
            return c
    return None


def _html_escape(text):
    """Escape HTML special characters."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _render_candidate_profile(candidate):
    """Render full candidate profile using Streamlit native components."""
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    skills = candidate.get("skills", [])
    edus = candidate.get("education", [])
    history = candidate.get("career_history", [])

    def esc(v, default=""):
        return _html_escape(v or default)

    # ── Profile Header ──
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(
            f'<div style="padding:0.5rem 0;">'
            f'<h4 style="color:var(--text-primary);margin:0;font-size:1.1rem;">{esc(profile.get("anonymized_name"), "?")}</h4>'
            f'<div style="color:var(--accent-blue);font-size:0.9rem;margin:0.2rem 0;">{esc(profile.get("headline"))}</div>'
            f'<div style="color:var(--text-muted);font-size:0.8rem;">'
            f'{esc(profile.get("current_title"), "?")} @ {esc(profile.get("current_company"), "?")}'
            f'</div>'
            f'<div style="color:var(--text-dim);font-size:0.75rem;margin-top:0.2rem;">'
            f'{esc(profile.get("location"))} &bull; {esc(profile.get("country"))}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with cols[1]:
        yrs = profile.get("years_of_experience", 0) or 0
        st.markdown(
            f'<div style="text-align:right;padding:0.5rem 0;">'
            f'<div style="color:var(--text-primary);font-size:1.3rem;font-weight:700;">{yrs:.1f}yrs</div>'
            f'<div style="color:var(--text-muted);font-size:0.7rem;">Experience</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Summary ──
    summary = profile.get("summary", "")
    if summary:
        st.markdown(
            f'<div style="color:var(--text-muted);font-size:0.8rem;line-height:1.5;'
            f'padding:0.5rem;background:var(--bg-sample);border-radius:6px;margin-bottom:0.8rem;">'
            f'{esc(summary[:300])}{"..." if len(summary) > 300 else ""}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Career History ──
    if history:
        st.markdown('<div style="color:var(--text-secondary);font-size:0.85rem;font-weight:600;margin:0.5rem 0 0.3rem 0;">\U0001F4BC Career History</div>', unsafe_allow_html=True)
        for job in history:
            title = esc(job.get("title"))
            company = esc(job.get("company"))
            duration = job.get("duration_months", 0) or 0
            is_current = job.get("is_current", False)
            desc = esc((job.get("description", "") or "")[:200])
            st.markdown(
                f'<div style="border-left:2px solid var(--accent-blue);padding:0.3rem 0.6rem;margin:0.2rem 0;">'
                f'<div style="color:var(--text-primary);font-size:0.8rem;font-weight:500;">{title} @ {company}</div>'
                f'<div style="color:var(--text-dim);font-size:0.7rem;">{duration}mo {"" if not is_current else "(Current)"}</div>'
                f'<div style="color:var(--text-muted);font-size:0.75rem;">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Education ──
    if edus:
        st.markdown('<div style="color:var(--text-secondary);font-size:0.85rem;font-weight:600;margin:0.5rem 0 0.3rem 0;">\U0001F393 Education</div>', unsafe_allow_html=True)
        for edu in edus:
            inst = esc(edu.get("institution"))
            degree = esc(edu.get("degree"))
            field = esc(edu.get("field_of_study"))
            grade = esc(edu.get("grade"))
            st.markdown(
                f'<div style="display:flex;gap:0.5rem;padding:0.2rem 0;color:var(--text-muted);font-size:0.78rem;">'
                f'<span style="color:var(--text-primary);">{degree}</span>'
                f'<span>{field}</span>'
                f'<span>@ {inst}</span>'
                f'<span style="color:var(--text-dim);">{grade}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Skills ──
    if skills:
        st.markdown('<div style="color:var(--text-secondary);font-size:0.85rem;font-weight:600;margin:0.5rem 0 0.3rem 0;">\U0001F528 Skills</div>', unsafe_allow_html=True)
        tags = ""
        for s in skills[:15]:
            name = esc(s.get("name"))
            prof = s.get("proficiency", "beginner")
            prof_color = {"beginner": "var(--text-dim)", "intermediate": "var(--warning)", "advanced": "var(--success)", "expert": "var(--accent-purple)"}.get(prof, "var(--text-dim)")
            tags += f'<span style="display:inline-block;background:var(--bg-sample);color:{prof_color};padding:0.15rem 0.5rem;border-radius:4px;font-size:0.7rem;margin:0.15rem;">{name}</span>'
        st.markdown(f'<div>{tags}</div>', unsafe_allow_html=True)

    # ── Redrob Signals ──
    st.markdown('<div style="color:var(--text-secondary);font-size:0.85rem;font-weight:600;margin:0.5rem 0 0.3rem 0;">\U0001F4CA Redrob Signals</div>', unsafe_allow_html=True)
    sig_cols = st.columns(4)
    _cross_mark = "\u2716"
    signal_items = [
        (f"{signals.get('profile_completeness_score', 0):.0f}%", "Completeness"),
        (f"{signals.get('connection_count', 0)}", "Connections"),
        (f"{signals.get('search_appearance_30d', 0)}", "Search Appearances"),
        (f'{signals.get("recruiter_response_rate", 0):.0%}', "Response Rate"),
        (f'{signals.get("interview_completion_rate", 0):.0%}', "Interview Rate"),
        (f"{signals.get('notice_period_days', 0)}d", "Notice Period"),
        ("Yes" if signals.get("open_to_work_flag", False) else "No", "Open to Work"),
        (f'\U0001F4E7{"" if signals.get("verified_email", False) else _cross_mark}', "Email"),
    ]
    for i, (val, label) in enumerate(signal_items):
        with sig_cols[i % 4]:
            st.markdown(
                f'<div style="padding:0.3rem 0;">'
                f'<div style="color:var(--text-primary);font-size:0.85rem;font-weight:600;">{val}</div>'
                f'<div style="color:var(--text-dim);font-size:0.65rem;">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Salary range
    salary = signals.get("expected_salary_range_inr_lpa", {})
    if salary and salary.get("min", 0) and salary.get("max", 0):
        s_min = salary["min"]
        s_max = salary["max"]
        st.markdown(
            f'<div style="color:var(--text-muted);font-size:0.75rem;margin-top:0.3rem;">'
            f'Salary: \u20B9{s_min:.1f} - \u20B9{s_max:.1f} LPA'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    # ── Theme toggle ──
    col_theme_label, col_theme_btn = st.columns([3, 1])
    with col_theme_label:
        st.markdown(
            f'<div class="sidebar-title" style="margin-bottom:0;">'
            f'{"☀️ Light" if THEME == "dark" else "🌙 Dark"} Mode</div>',
            unsafe_allow_html=True,
        )
    with col_theme_btn:
        icon = "☀️" if THEME == "dark" else "🌙"
        if st.button(icon, help=f"Switch to {'Light' if THEME == 'dark' else 'Dark'} theme", use_container_width=True):
            new_theme = "light" if THEME == "dark" else "dark"
            st.session_state["theme"] = new_theme
            st.rerun()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Data Source
    st.markdown('<div class="sidebar-title">\U0001F4E5 Data Source</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload file",
        type=["json", "csv", "xlsx", "xls"],
        label_visibility="collapsed",
        help="Upload JSON, CSV, or Excel (.xlsx/.xls) files",
    )

    if uploaded_file is not None:
        try:
            ext = uploaded_file.name.split(".")[-1].lower()
            if ext == "json":
                raw = uploaded_file.read().decode("utf-8")
                candidates = parse_json_input(raw)
            elif ext == "csv":
                df = pd.read_csv(uploaded_file)
                candidates = parse_tabular_data(df)
            elif ext in ("xlsx", "xls"):
                df = pd.read_excel(uploaded_file, engine="openpyxl")
                candidates = parse_tabular_data(df)

            st.success(f"\u2713 Loaded {len(candidates)} candidates")
            if st.button("\U0001F680 Run Ranker", type="primary", use_container_width=True):
                with st.spinner("Ranking..."):
                    run_ranker(candidates, f"File: {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Paste JSON
    st.markdown('<div class="sidebar-title">\U0001F4DD Paste Input</div>', unsafe_allow_html=True)
    with st.expander("Paste JSON", expanded=False):
        pasted = st.text_area("", height=140,
                              placeholder='[{"candidate_id": "CAND_0001", ...}]',
                              label_visibility="collapsed")
        if pasted.strip():
            try:
                candidates = parse_json_input(pasted)
                st.success(f"\u2713 Parsed {len(candidates)} candidates")
                if st.button("\U0001F680 Run on Pasted Data", type="primary", use_container_width=True):
                    with st.spinner("Ranking..."):
                        run_ranker(candidates, "Pasted JSON")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Sample data
    st.markdown('<div class="sidebar-title">\U0001F4CA Sample</div>', unsafe_allow_html=True)
    if st.button("\U0001F504 Run Sample (20 candidates)", type="secondary", use_container_width=True):
        with st.spinner("Running..."):
            if not os.path.exists(SAMPLE_PATH):
                st.error("Sample data not found")
                st.stop()
            with open(SAMPLE_PATH) as f:
                samples = json.load(f)
            run_ranker(samples, "Sample Data")

    # Show weights when results exist
    if "rankings" in st.session_state:
        import config as cfg
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">\u2696\uFE0F Weights</div>', unsafe_allow_html=True)
        for name, weight in cfg.WEIGHTS.items():
            label = name.replace("_", " ").title()
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'color:var(--text-muted);font-size:0.8rem;margin-bottom:0.15rem;">'
                f'<span>{label}</span><span>{weight*100:.0f}%</span></div>',
                unsafe_allow_html=True
            )
            st.progress(weight)

# ── Main Content ────────────────────────────────────────────────────────────

if "rankings" in st.session_state:
    rankings = st.session_state["rankings"]
    total = st.session_state["total"]
    source = st.session_state.get("source", "")
    elapsed = st.session_state["elapsed"]

    # Compute metrics
    top_score = rankings[0][0]
    bottom_score = rankings[-1][0]
    honeypot_count = sum(1 for h in rankings if h[3] < 0.5)
    suspicious_count = sum(1 for h in rankings if 0.5 <= h[3] < 0.8)
    clean_count = total - honeypot_count - suspicious_count

    # ── Enterprise Metric Cards ──
    st.markdown(
        f'<div style="color:var(--text-muted);font-size:0.8rem;margin-bottom:0.5rem;">'
        f'Source: {source} &bull; {time.strftime("%b %d, %Y %H:%M")}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"""
    <div class="metric-grid">
        {make_metric_card(f'{total:,}', 'Candidates', '#3b82f6')}
        {make_metric_card(f'{elapsed:.2f}s', 'Processing Time', '#8b5cf6')}
        {make_metric_card(f'{top_score:.4f}', 'Top Score', '#34d399')}
        {make_metric_card(f'{bottom_score:.4f}', 'Min Score', '#fbbf24')}
        {make_metric_card(f'{honeypot_count}', 'Honeypots', '#f87171')}
        {make_metric_card(f'{suspicious_count}', 'Suspicious', '#fbbf24')}
        {make_metric_card(f'{clean_count}', 'Verified', '#34d399')}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Tabs ──
    tab1, tab2, tab3 = st.tabs(["\U0001F4CA Dashboard", "\U0001F3C5 Rankings", "\U0001F4CA Insights"])

    # ── Tab 1: Dashboard ──
    with tab1:
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            scores = [r[0] for r in rankings]

            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=scores,
                nbinsx=20,
                marker=dict(
                    color=scores,
                    colorscale=[[0, '#f87171'], [0.5, '#fbbf24'], [1, '#34d399']],
                    line=dict(color='rgba(255,255,255,0.05)', width=1),
                ),
                hovertemplate="Score: %{x:.4f}<br>Count: %{y}<extra></extra>",
            ))
            fig.add_vline(
                x=top_score, line_dash="dash", line_color="#3b82f6",
                annotation_text=f"Top: {top_score:.4f}",
                annotation_position="top left",
                annotation_font=dict(color="#3b82f6", size=10),
            )
            fig.update_layout(
                title=dict(text="<b>Score Distribution</b>", font=dict(color=P["text_primary"], size=14)),
                paper_bgcolor=P["chart_bg"], plot_bgcolor=P["chart_bg"],
                font=dict(color=P["text_muted"], size=11),
                xaxis=dict(title="Score", gridcolor=P["chart_grid"], zeroline=False),
                yaxis=dict(title="Candidates", gridcolor=P["chart_grid"], zeroline=False),
                margin=dict(l=30, r=30, t=40, b=30),
                hovermode="x", bargap=0.06,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_chart2:
            labels = ["Verified", "Suspicious", "Honeypot"]
            values = [clean_count, suspicious_count, honeypot_count]
            colors = ["#34d399", "#fbbf24", "#f87171"]

            fig2 = go.Figure(data=[go.Pie(
                labels=labels, values=values,
                marker=dict(colors=colors, line=dict(color=P["bg_primary"], width=2)),
                textinfo="label+percent",
                textfont=dict(color=P["text_primary"], size=12),
                hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
                hole=0.55,
            )])
            fig2.update_layout(
                title=dict(text="<b>Candidate Integrity</b>", font=dict(color=P["text_primary"], size=14)),
                paper_bgcolor=P["chart_bg"], plot_bgcolor=P["chart_bg"],
                font=dict(color=P["text_muted"], size=11),
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False,
                annotations=[dict(
                    text=f"{clean_count}<br>Verified",
                    x=0.5, y=0.5,
                    font=dict(size=16, color=P["success"]),
                    showarrow=False,
                )],
            )
            st.plotly_chart(fig2, use_container_width=True)

        # ── Top 5 Quick View ──
        st.markdown(
            '<h4 style="color:var(--text-primary);font-size:1rem;margin:1rem 0 0.5rem 0;">'
            '\U0001F525 Top 5 Candidates</h4>',
            unsafe_allow_html=True,
        )

        for rank, (score, cid, reasoning, penalty, issues) in enumerate(rankings[:5], 1):
            card = _render_rank_card(rank, score, cid, reasoning, penalty, issues, large_style=True)
            st.markdown(card, unsafe_allow_html=True)

    # ── Tab 2: Full Rankings ──
    with tab2:
        col_left, col_right = st.columns([1, 3])
        with col_left:
            # Hamburger menu popover wrapping all filter/sort controls
            with st.popover("\u2630 Filters", use_container_width=True):
                search_term = st.text_input(
                    "\U0001F50D Search",
                    placeholder="ID or keyword...",
                    help="Search by candidate ID or keyword in reasoning",
                )

                badge_filter = st.selectbox(
                    "Badge",
                    ["All", "Verified", "Suspicious", "Honeypot"],
                    index=0,
                    help="Filter by candidate status",
                )

                sort_by = st.selectbox(
                    "Sort by",
                    ["Score: High to Low", "Score: Low to High", "Penalty: Low to High", "Penalty: High to Low"],
                    index=0,
                    help="Sort candidates",
                )

                min_score = st.slider("Min Score", 0.0, 1.0, 0.7, 0.01)

        with col_right:
            # ── Build filtered + sorted list ──
            filtered = []
            for score, cid, reasoning, penalty, issues in rankings:
                if score < min_score:
                    continue
                if search_term:
                    q = search_term.lower()
                    if q not in cid.lower() and q not in reasoning.lower():
                        continue
                if badge_filter == "Verified" and penalty < 0.8:
                    continue
                if badge_filter == "Suspicious" and not (0.3 <= penalty < 0.8):
                    continue
                if badge_filter == "Honeypot" and penalty >= 0.3:
                    continue
                filtered.append((score, cid, reasoning, penalty, issues))

            # Apply sorting
            if sort_by == "Score: High to Low":
                filtered.sort(key=lambda x: x[0], reverse=True)
            elif sort_by == "Score: Low to High":
                filtered.sort(key=lambda x: x[0])
            elif sort_by == "Penalty: Low to High":
                filtered.sort(key=lambda x: x[3])
            elif sort_by == "Penalty: High to Low":
                filtered.sort(key=lambda x: x[3], reverse=True)

            total_ranked = len(rankings)
            shown = len(filtered)
            st.markdown(
                f'<div style="color:var(--text-muted);font-size:0.85rem;margin-bottom:0.5rem;">'
                f'Showing {shown} of {total_ranked} candidates'
                f'{" | Filtered" if shown < total_ranked else ""}'
                f' | Sort: {sort_by}</div>',
                unsafe_allow_html=True,
            )

            if not filtered:
                st.markdown(
                    '<div style="text-align:center;color:var(--text-dim);padding:2rem;font-size:0.9rem;">'
                    '\U0001F50D No candidates match the current filters'
                    '</div>',
                    unsafe_allow_html=True,
                )
            else:
                for rank, (score, cid, reasoning, penalty, issues) in enumerate(filtered, 1):
                    card = _render_rank_card(rank, score, cid, reasoning, penalty, issues, large_style=False)
                    st.markdown(card, unsafe_allow_html=True)

        # ── Candidate Profile Viewer ──
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="color:var(--text-secondary);font-size:0.9rem;font-weight:600;margin-bottom:0.3rem;">'
            '\U0001F50D Candidate Lookup</div>',
            unsafe_allow_html=True,
        )

        # Build list of selectable candidates
        cid_list = [r[1] for r in rankings]
        selected_cid = st.selectbox(
            "Select a candidate to view full profile:",
            cid_list,
            index=None,
            placeholder="Choose a candidate...",
            label_visibility="collapsed",
            key="candidate_lookup",
        )

        if selected_cid:
            candidate = find_candidate_by_cid(selected_cid)
            if candidate:
                st.markdown(
                    f'<div style="background:var(--bg-card-alt);border:1px solid var(--border-card);'
                    f'border-radius:10px;padding:1rem;margin-top:0.5rem;">',
                    unsafe_allow_html=True,
                )
                _render_candidate_profile(candidate)

                # Close button
                if st.button("\u2716 Close Profile", key="close_candidate_profile", type="secondary"):
                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

        # ── Compare Candidates ──
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="color:var(--text-secondary);font-size:0.9rem;font-weight:600;margin-bottom:0.3rem;">'
            '\U0001F504 Compare Candidates</div>',
            unsafe_allow_html=True,
        )

        compare_cids = st.multiselect(
            "Select up to 2 candidates to compare:",
            cid_list,
            max_selections=2,
            placeholder="Choose candidates...",
            label_visibility="collapsed",
        )

        if len(compare_cids) == 2:
            c1 = find_candidate_by_cid(compare_cids[0])
            c2 = find_candidate_by_cid(compare_cids[1])
            if c1 and c2:
                st.markdown(
                    f'<div style="display:flex;gap:0.5rem;align-items:center;margin-bottom:0.5rem;">'
                    f'<span style="color:var(--accent-blue);font-weight:600;font-size:0.85rem;">'
                    f'Comparing: {compare_cids[0]} vs {compare_cids[1]}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                comp_col1, comp_col2 = st.columns(2)

                with comp_col1:
                    st.markdown(
                        f'<div style="background:var(--bg-card-alt);border:1px solid var(--border-card);'
                        f'border-radius:10px;padding:0.8rem;min-height:200px;">'
                        f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;'
                        f'padding-bottom:0.5rem;border-bottom:1px solid var(--border-color);">'
                        f'<span class="badge badge-clean">#{compare_cids[0]}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    _render_candidate_profile(c1)
                    st.markdown('</div>', unsafe_allow_html=True)

                with comp_col2:
                    st.markdown(
                        f'<div style="background:var(--bg-card-alt);border:1px solid var(--border-card);'
                        f'border-radius:10px;padding:0.8rem;min-height:200px;">'
                        f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;'
                        f'padding-bottom:0.5rem;border-bottom:1px solid var(--border-color);">'
                        f'<span class="badge badge-clean">#{compare_cids[1]}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    _render_candidate_profile(c2)
                    st.markdown('</div>', unsafe_allow_html=True)

                # Clear comparison button
                if st.button("\u2716 Clear Comparison", key="clear_comparison", type="secondary"):
                    st.rerun()

    # ── Tab 3: Insights ──
    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                '<h4 style="color:var(--text-primary);font-size:0.95rem;">Detection Summary</h4>',
                unsafe_allow_html=True,
            )

            # Honeypot issue frequency
            all_issues = []
            for _, _, _, _, issues in rankings:
                for i in issues:
                    if "timeline" in i:
                        all_issues.append("Timeline inconsistency")
                    elif "overlapping" in i:
                        all_issues.append("Overlapping education")
                    elif "AI skills" in i:
                        all_issues.append("AI skills mismatch")
                    elif "endorsements" in i:
                        all_issues.append("Endorsement mismatch")
                    elif "exceeds" in i:
                        all_issues.append("Career exceeds experience")
                    elif "empty" in i or "short" in i:
                        all_issues.append("Short/empty descriptions")
                    elif "hopping" in i or "duration" in i:
                        all_issues.append("Job-hopping")
                    elif "summary" in i:
                        all_issues.append("Summary mismatch")
                    elif "salary" in i:
                        all_issues.append("Salary anomaly")
                    elif "signup" in i:
                        all_issues.append("Date anomaly")
                    elif "offer" in i:
                        all_issues.append("Offer/interview mismatch")
                    else:
                        all_issues.append("Other")

            if all_issues:
                issue_counts = Counter(all_issues)
                issue_df = pd.DataFrame([
                    {"Issue": k, "Count": v}
                    for k, v in issue_counts.most_common()
                ])

                fig3 = px.bar(
                    issue_df, x="Count", y="Issue", orientation="h",
                    color="Count", color_continuous_scale=["#fbbf24", "#f87171"],
                    text="Count",
                )
                fig3.update_layout(
                    paper_bgcolor=P["chart_bg"], plot_bgcolor=P["chart_bg"],
                    font=dict(color=P["text_muted"], size=11),
                    xaxis=dict(gridcolor=P["chart_grid"], title=""),
                    yaxis=dict(title=""),
                    margin=dict(l=10, r=10, t=10, b=10),
                    showlegend=False,
                )
                fig3.update_traces(textposition="outside", textfont=dict(color=P["text_primary"]))
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No issues detected in top ranks.")

        with col2:
            st.markdown(
                '<h4 style="color:var(--text-primary);font-size:0.95rem;">Score vs Penalty</h4>',
                unsafe_allow_html=True,
            )

            scatter_data = pd.DataFrame({
                "Score": [r[0] for r in rankings],
                "Penalty": [r[3] for r in rankings],
                "Status": ["Honeypot" if r[3] < 0.3 else ("Suspicious" if r[3] < 0.8 else "Verified")
                           for r in rankings],
            })

            fig4 = px.scatter(
                scatter_data, x="Score", y="Penalty", color="Status",
                color_discrete_map={"Verified": P["success"], "Suspicious": P["warning"], "Honeypot": P["danger"]},
                opacity=0.7, size=[8] * len(scatter_data),
                hover_data={"Status": True},
            )
            fig4.update_layout(
                paper_bgcolor=P["chart_bg"], plot_bgcolor=P["chart_bg"],
                font=dict(color=P["text_muted"], size=11),
                xaxis=dict(gridcolor=P["chart_grid"], range=[0.5, 1.0]),
                yaxis=dict(gridcolor=P["chart_grid"], range=[0, 1.0]),
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(font=dict(color=P["text_muted"])),
            )
            st.plotly_chart(fig4, use_container_width=True)

        # Bottom: pipeline info
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.markdown(
                f'<div style="color:var(--text-muted);font-size:0.85rem;">'
                f'<strong style="color:var(--text-muted-dark);">Engine:</strong> 10-component ranker</div>',
                unsafe_allow_html=True)
        with col_info2:
            st.markdown(
                f'<div style="color:var(--text-muted);font-size:0.85rem;">'
                f'<strong style="color:var(--text-muted-dark);">Honeypot checks:</strong> 11</div>',
                unsafe_allow_html=True)
        with col_info3:
            st.markdown(
                f'<div style="color:var(--text-muted);font-size:0.85rem;">'
                f'<strong style="color:var(--text-muted-dark);">Throughput:</strong> {total/elapsed:.0f} cand/s</div>',
                unsafe_allow_html=True)

    # Clear button
    st.markdown('<div style="text-align:center;margin-top:1rem;">', unsafe_allow_html=True)
    if st.button("\U0001F5D1 Clear & Start Over", type="secondary", use_container_width=False):
        for key in ["rankings", "elapsed", "total", "source", "active_tab", "candidates_data"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # ── Welcome / Empty State ──
    col_intro, col_preview = st.columns([1.5, 1])

    with col_intro:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,var(--bg-welcome),var(--bg-card-alt));
                    border:1px solid var(--border-card);border-radius:14px;padding:2rem;">
            <h3 style="color:var(--text-primary);margin:0 0 0.5rem 0;font-size:1.3rem;">
                \U0001F44B Welcome to Candidate Ranker
            </h3>
            <p style="color:var(--text-muted-dark);font-size:0.95rem;line-height:1.6;">
            Enterprise-grade candidate ranking for <strong style="color:var(--text-primary);">Senior AI Engineer</strong>
            roles. Upload your candidate data in <strong>JSON</strong>, <strong>CSV</strong>, or
            <strong>Excel</strong> format and get instant AI-powered rankings.
            </p>
            <div style="display:flex;gap:0.8rem;flex-wrap:wrap;margin-top:1.5rem;">
                <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.15);
                            border-radius:8px;padding:0.6rem 1rem;text-align:center;flex:1;min-width:100px;">
                    <div style="font-size:1.3rem;">\U0001F4E5</div>
                    <div style="color:var(--text-muted);font-size:0.7rem;margin-top:0.2rem;">Upload</div>
                </div>
                <div style="background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.15);
                            border-radius:8px;padding:0.6rem 1rem;text-align:center;flex:1;min-width:100px;">
                    <div style="font-size:1.3rem;">\U0001F4CA</div>
                    <div style="color:var(--text-muted);font-size:0.7rem;margin-top:0.2rem;">Analyze</div>
                </div>
                <div style="background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.15);
                            border-radius:8px;padding:0.6rem 1rem;text-align:center;flex:1;min-width:100px;">
                    <div style="font-size:1.3rem;">\U0001F3C5</div>
                    <div style="color:var(--text-muted);font-size:0.7rem;margin-top:0.2rem;">Rank</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_preview:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,var(--bg-preview),var(--bg-card-alt));
                    border:1px solid var(--border-light);border-radius:14px;padding:1.5rem;">
            <h4 style="color:var(--text-primary);margin:0 0 0.5rem 0;font-size:0.95rem;">
                \U0001F4CB Supported Formats
            </h4>
            <div style="color:var(--text-muted-dark);font-size:0.85rem;line-height:1.8;">
                <div>\U0001F4C4 <strong>JSON</strong> &mdash; Array of candidate objects</div>
                <div>\U0001F4C4 <strong>CSV</strong> &mdash; Flat column format</div>
                <div>\U0001F4C4 <strong>Excel</strong> &mdash; .xlsx / .xls files</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Sample preview
    if os.path.exists(SAMPLE_PATH):
        with open(SAMPLE_PATH) as f:
            samples = json.load(f)
        st.markdown(f"""
        <div style="margin-top:1rem;background:var(--bg-sample);border:1px solid var(--border-light);
                    border-radius:10px;padding:1rem;">
            <h4 style="color:var(--text-muted);margin:0 0 0.5rem 0;font-size:0.85rem;text-transform:uppercase;
                       letter-spacing:0.5px;">\U0001F4CB Sample Data Preview</h4>
        """, unsafe_allow_html=True)
        for s in samples[:5]:
            p = s.get("profile", {})
            st.markdown(
                f'<div style="color:var(--text-muted);font-size:0.8rem;padding:0.2rem 0;'
                f'border-bottom:1px solid var(--border-light);">'
                f'<span style="color:var(--text-muted-dark);">{p.get("anonymized_name", "?")}</span>'
                f' &mdash; {p.get("current_title", "?")} @ {p.get("current_company", "?")}'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown(
            f'<div style="color:var(--text-dim2);font-size:0.75rem;padding-top:0.3rem;">'
            f'... and {len(samples) - 5} more</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Algorithm info
    with st.expander("About the Ranking Algorithm"):
        col_comp, col_hp = st.columns(2)
        with col_comp:
            st.markdown("""
            **Scoring Components**
            - Career Relevance (35%): Title tier, industry fit, startup bonus
            - Role Relevance (20%): Current title + headline match
            - Production AI Evidence (14%): ML deployment experience
            - Retrieval & Ranking (10%): Search/ranking systems
            - Behavioral Signals (10%): Response rate, GitHub activity
            - Experience Fit (5%): Peak 5-9 years
            - Skills Match (3%): Keyword coverage
            - Education (3%): Tier + field relevance
            - Location Bonus (+3%): Pune/Noida preferred
            - Notice Period (+2%): Sub-30 day preferred
            """)
        with col_hp:
            st.markdown("""
            **Honeypot Detection (11 checks)**
            - Timeline inconsistency, overlapping education
            - AI skills without background, endorsement mismatch
            - Career exceeds stated experience
            - Short/empty descriptions, job-hopping
            - Summary mismatch, salary inversion
            - Signup/active date mismatch
            - Offer acceptance without interviews

            **Performance**
            - 100K candidates in ~57s (CPU-only)
            - 16,157 honeypots detected
            - 0 honeypots in top 100
            - 100/100 unique reasonings
            """)

st.markdown(
    '<div class="footer">Built for the Redrob Hackathon &mdash; '
    'Intelligent Candidate Discovery &amp; Ranking Challenge</div>',
    unsafe_allow_html=True,
)
