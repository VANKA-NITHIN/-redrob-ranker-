"""
Redrob Hackathon — Candidate Ranking Demo App
A lightweight Streamlit app to run the ranker on sample data and view results.

Deploy on HuggingFace Spaces: https://huggingface.co/spaces
Runtime: Python 3.11+, CPU
"""
import json
import os
import sys

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

# --- App UI ---

with st.sidebar:
    st.header("Configuration")
    st.markdown("**Job:** Senior AI Engineer (Founding Team)")
    st.markdown("**Source:** Redrob Candidate Database")

    if st.button("\U0001F504 Run Ranker on Sample Data", type="primary", use_container_width=True):
        with st.spinner("Loading and ranking candidates..."):
            if not os.path.exists(SAMPLE_PATH):
                st.error(f"Sample data not found at {SAMPLE_PATH}")
                st.stop()

            with open(SAMPLE_PATH, "r") as f:
                samples = json.load(f)

            import time
            start = time.time()
            rankings = process_candidates(samples)
            elapsed = time.time() - start

            st.session_state["rankings"] = rankings
            st.session_state["elapsed"] = elapsed
            st.session_state["total"] = len(samples)
            st.success(f"Ranked {len(samples)} candidates in {elapsed:.2f}s")

    # Show current weights from config
    if "rankings" in st.session_state:
        import config as cfg
        st.header("\u2696\uFE0F Feature Weights")
        for name, weight in cfg.WEIGHTS.items():
            label = name.replace("_", " ").title()
            st.metric(label, f"{weight:.0%}")

# Main content
if "rankings" in st.session_state:
    rankings = st.session_state["rankings"]
    total = st.session_state["total"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Candidates", total)
    col2.metric("Time", f"{st.session_state['elapsed']:.2f}s")
    col3.metric("Top Score", f"{rankings[0][0]:.4f}")
    col4.metric("Bottom Score", f"{rankings[-1][0]:.4f}")

    # Honeypot summary
    honeypot_count = sum(1 for h in rankings if h[3] < 0.5)
    suspicious_count = sum(1 for h in rankings if 0.5 <= h[3] < 0.8)
    col5, col6 = st.columns(2)
    col5.metric("\U0001F534 Honeypots", honeypot_count)
    col6.metric("\U0001F7E1 Suspicious", suspicious_count)

    st.divider()

    # Display rankings table
    st.subheader(f"\U0001F3C5 Top {len(rankings)} Rankings")
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

else:
    # Welcome message
    st.info("\U0001F448 Click **Run Ranker on Sample Data** in the sidebar to get started!")

    with st.expander("\U0001F4D6 About the Ranking Algorithm"):
        st.markdown("""
        ### Scoring Components

        | Component | Weight | Description |
        |-----------|--------|-------------|
        | **Career Relevance** | 38% | Title tier, production AI evidence, industry fit, startup bonus |
        | **Production AI Evidence** | 18% | Keywords for retrieval, ranking, search, recommendation |
        | **Role Relevance** | 17% | Current title + headline match to AI/ML engineering |
        | **Behavioral Signals** | 12% | Redrob response rate, GitHub, profile completeness |
        | **Experience Fit** | 8% | Years of experience (peak 5\u20139 years) |
        | **Education** | 5% | Institution tier, field relevance, degree level |
        | **Skills Match** | 2% | Minimal weight \u2014 EDA confirmed skills are artificially distributed |

        ### Honeypot Detection (8 checks)
        - Timeline inconsistency, overlapping education, AI skills without background
        - Missing/short descriptions, job-hopping, summary mismatch
        - Endorsement/skill count mismatch, career history exceeds stated experience

        Runs in under 2 minutes for 100K candidates on CPU.
        """)

st.markdown("---")
st.caption("Built for the Redrob Hackathon \u2014 Intelligent Candidate Discovery & Ranking Challenge")
