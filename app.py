"""
Redrob Hackathon — Candidate Ranking Demo App
A lightweight Streamlit app to run the ranker on sample data, upload custom data,
or paste candidate JSON directly.

Deploy on HuggingFace Spaces: https://huggingface.co/spaces
Runtime: Python 3.11+, CPU
"""
import json
import os
import sys
import time

import streamlit as st

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from ranker import process_candidates, compute_total_score, generate_reasoning

st.set_page_config(
    page_title="Redrob Candidate Ranker",
    page_icon="\U0001F3C6",
    layout="wide",
)

st.title("\U0001F3C6 Redrob Hackathon \u2014 Intelligent Candidate Ranking")
st.markdown(
    """
    Ranks candidates for a **Senior AI Engineer (Founding Team)** role using
    a multi-component rule-based scoring engine. Built entirely in Python, no ML dependencies.
    """
)

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_candidates.json")


def run_ranker(candidates, source_label):
    """Run the ranker on a list of candidates and store results in session state."""
    if not candidates:
        st.error("No candidates found in the provided data.")
        return

    start = time.time()
    rankings = process_candidates(candidates)
    elapsed = time.time() - start

    st.session_state["rankings"] = rankings
    st.session_state["elapsed"] = elapsed
    st.session_state["total"] = len(candidates)
    st.session_state["source"] = source_label
    st.success(f"Ranked {len(candidates)} candidates in {elapsed:.2f}s")


def parse_json_input(raw):
    """Try to parse a JSON string into a list of candidate objects."""
    data = json.loads(raw)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # Check if it's a single candidate wrapped in an object
        if "candidate_id" in data:
            return [data]
        # Check for common wrappers like {"candidates": [...]}
        for key in ("candidates", "data", "results", "profiles"):
            if key in data and isinstance(data[key], list):
                return data[key]
    raise ValueError("JSON must be an array of candidate objects")


# --- Sidebar ---

with st.sidebar:
    st.header("\U0001F4E5 Custom Input")

    # Option 1: File upload
    uploaded_file = st.file_uploader(
        "Upload a JSON file",
        type=["json"],
        help="Upload a .json file containing an array of candidate objects matching the Redrob schema.",
    )

    if uploaded_file is not None:
        try:
            raw = uploaded_file.read().decode("utf-8")
            candidates = parse_json_input(raw)
            st.success(f"\U00002705 Loaded {len(candidates)} candidates from file")
            if st.button("\U0001F504 Run on Uploaded Data", type="primary", use_container_width=True):
                with st.spinner("Ranking uploaded candidates..."):
                    run_ranker(candidates, f"Uploaded file ({len(candidates)} candidates)")
        except Exception as e:
            st.error(f"Failed to parse JSON file: {e}")

    # Option 2: Paste JSON
    with st.expander("\U0001F4DD Or paste JSON"):
        pasted_json = st.text_area(
            "Paste candidate JSON here",
            height=200,
            placeholder='[\n  {\n    "candidate_id": "CAND_0000001",\n    "profile": { ... },\n    ...\n  }\n]',
            help="Paste a JSON array of candidate objects matching the Redrob schema.",
        )
        if pasted_json.strip():
            try:
                candidates = parse_json_input(pasted_json)
                st.success(f"\U00002705 Parsed {len(candidates)} candidates")
                if st.button("\U0001F504 Run on Pasted Data", type="primary", use_container_width=True):
                    with st.spinner("Ranking pasted candidates..."):
                        run_ranker(candidates, f"Pasted JSON ({len(candidates)} candidates)")
            except Exception as e:
                st.error(f"Failed to parse pasted JSON: {e}")

    st.divider()

    # Option 3: Sample data (always available)
    st.header("\U0001F4CA Sample Data")
    if st.button("\U0001F504 Run on Sample Data (20 candidates)", type="secondary", use_container_width=True):
        with st.spinner("Loading and ranking sample candidates..."):
            if not os.path.exists(SAMPLE_PATH):
                st.error(f"Sample data not found at {SAMPLE_PATH}")
                st.stop()
            with open(SAMPLE_PATH, "r") as f:
                samples = json.load(f)
            run_ranker(samples, "Sample data (20 candidates)")

    # Show current weights when results exist
    if "rankings" in st.session_state:
        import config as cfg
        st.divider()
        st.header("\u2696\uFE0F Feature Weights")
        for name, weight in cfg.WEIGHTS.items():
            label = name.replace("_", " ").title()
            st.metric(label, f"{weight:.0%}")

# --- Main Content ---

if "rankings" in st.session_state:
    rankings = st.session_state["rankings"]
    total = st.session_state["total"]
    source = st.session_state.get("source", "")

    st.markdown(f"**Source:** {source}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Candidates", total)
    col2.metric("Time", f"{st.session_state['elapsed']:.2f}s")
    col3.metric("Top Score", f"{rankings[0][0]:.4f}")
    col4.metric("Bottom Score", f"{rankings[-1][0]:.4f}")

    # Honeypot summary
    honeypot_count = sum(1 for h in rankings if h[3] < 0.5)
    suspicious_count = sum(1 for h in rankings if 0.5 <= h[3] < 0.8)
    clean_count = total - honeypot_count - suspicious_count
    col5, col6, col7 = st.columns(3)
    col5.metric("\U0001F534 Honeypots", honeypot_count)
    col6.metric("\U0001F7E1 Suspicious", suspicious_count)
    col7.metric("\u2705 Clean", clean_count)

    st.divider()

    # Display rankings table
    st.subheader(f"\U0001F3C5 Rankings (Top {len(rankings)})")
    for rank, (score, cid, reasoning, penalty, issues) in enumerate(rankings, 1):
        if penalty < 0.3:
            badge = "\U0001F534 HIGH-RISK HONEYPOT"
        elif penalty < 0.8:
            badge = "\U0001F7E1 SUSPICIOUS"
        else:
            badge = "\u2705"

        with st.container(border=True):
            cols = st.columns([1, 2, 6])
            with cols[0]:
                st.markdown(f"### #{rank}")
            with cols[1]:
                st.markdown(f"**{cid}**")
                st.markdown(f"Score: `{score:.4f}` | Pen: `{penalty:.2f}`")
            with cols[2]:
                st.markdown(f"{badge} {reasoning}")
                if issues:
                    st.caption(f"\u26A0\uFE0F Issues: {'; '.join(issues[:3])}")

    # Button to clear results
    if st.button("\U0001F5D1 Clear Results", type="secondary"):
        for key in ["rankings", "elapsed", "total", "source"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

else:
    # Welcome message
    st.info(
        "\U0001F448 Choose one of the options in the **sidebar** to get started:\n\n"
        "1. **Upload a JSON file** of candidates\n"
        "2. **Paste JSON** directly into the text area\n"
        "3. **Run on sample data** (20 pre-loaded candidates)"
    )

    # Show sample data preview
    if os.path.exists(SAMPLE_PATH):
        with open(SAMPLE_PATH, "r") as f:
            samples = json.load(f)
        with st.expander(f"\U0001F4CB Preview: {len(samples)} sample candidates"):
            for s in samples[:5]:
                p = s.get("profile", {})
                st.markdown(
                    f"- **{p.get('anonymized_name', 'N/A')}** | "
                    f"{p.get('current_title', 'N/A')} @ {p.get('current_company', 'N/A')} | "
                    f"{p.get('location', 'N/A')}"
                )
            if len(samples) > 5:
                st.markdown(f"... and {len(samples) - 5} more")

    with st.expander("\U0001F4D6 About the Ranking Algorithm"):
        st.markdown("""
        ### Scoring Components

        | Component | Weight | Description |
        |-----------|--------|-------------|
        | **Career Relevance** | 35% | Title tier, industry fit, consulting penalty, startup bonus |
        | **Role Relevance** | 20% | Current title + headline match to AI/ML engineering |
        | **Production AI Evidence** | 14% | Keywords for ML deployment, retrieval, ranking, search |
        | **Retrieval & Ranking** | 10% | JD's #1 ask — search/ranking system experience |
        | **Behavioral Signals** | 10% | Response rate, GitHub, profile completeness |
        | **Experience Fit** | 5% | Years of experience (peak 5\u20139 years) |
        | **Skills Match** | 3% | Minimal weight |
        | **Education** | 3% | Institution tier, field relevance |
        | **Location Bonus** | +3% | Pune/Noida preferred |
        | **Notice Period** | +2% | Sub-30 day preferred |

        ### Honeypot Detection (8 checks)
        - Timeline inconsistency, overlapping education, AI skills without background
        - Missing/short descriptions, job-hopping, summary mismatch
        - Endorsement/skill count mismatch, career history exceeds stated experience

        Runs 100K candidates in ~92s on CPU. 0 honeypots in top 100.
        """)

st.markdown("---")
st.caption("Built for the Redrob Hackathon \u2014 Intelligent Candidate Discovery & Ranking Challenge")
