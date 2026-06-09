"""
Redrob Hackathon — Intelligent Candidate Ranking
Polished Streamlit UI with custom CSS, charts, animations, and modern design.
"""
import json
import os
import sys
import time

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))
from ranker import process_candidates

st.set_page_config(
    page_title="Redrob Candidate Ranker",
    page_icon="\U0001F3C6",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────

CUSTOM_CSS = """
<style>
    /* ── Base theme ── */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }

    /* ── Main title ── */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .main-subtitle {
        color: #a0aec0;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* ── Metric cards ── */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(102, 126, 234, 0.4);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        color: #a0aec0;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.3rem;
    }

    /* ── Candidate cards ── */
    .candidate-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideIn 0.4s ease-out;
    }
    .candidate-card:hover {
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1);
        transform: translateX(4px);
    }

    .candidate-rank {
        font-size: 1.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .candidate-id {
        font-weight: 600;
        color: #e2e8f0;
    }
    .candidate-score {
        font-family: 'SF Mono', 'Fira Code', monospace;
        font-size: 0.95rem;
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-15px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Badges ── */
    .badge-clean {
        display: inline-block;
        background: rgba(72, 187, 120, 0.15);
        color: #48bb78;
        padding: 0.15rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .badge-suspicious {
        display: inline-block;
        background: rgba(237, 137, 54, 0.15);
        color: #ed8936;
        padding: 0.15rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .badge-honeypot {
        display: inline-block;
        background: rgba(245, 101, 101, 0.15);
        color: #f56565;
        padding: 0.15rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    .issues-text {
        color: #f56565;
        font-size: 0.8rem;
        font-style: italic;
    }

    /* ── Progress bar glow ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }

    /* ── Sidebar tweaks ── */
    .sidebar-section-header {
        color: #667eea;
        font-weight: 700;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.8rem;
    }

    /* ── Divider ── */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
        margin: 1.5rem 0;
    }

    /* ── Source label ── */
    .source-label {
        color: #718096;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }

    /* ── Chart container ── */
    .chart-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_candidates.json")


# ── Helper functions ────────────────────────────────────────────────────────

def run_ranker(candidates, source_label):
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


def make_metric(value, label, key=None):
    return f"""
    <div class="metric-card" {'id="' + key + '"' if key else ''}>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


def score_badge(penalty):
    if penalty < 0.3:
        return '<span class="badge-honeypot">HIGH-RISK HONEYPOT</span>'
    elif penalty < 0.8:
        return '<span class="badge-suspicious">SUSPICIOUS</span>'
    return '<span class="badge-clean">VERIFIED</span>'


# ── Header ──────────────────────────────────────────────────────────────────

col_logo, col_title = st.columns([0.1, 0.9])
with col_title:
    st.markdown('<div class="main-header">\U0001F3C6 Redrob Candidate Ranker</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">'
        'Multi-component rule-based ranking engine &bull; 10 dimensions &bull; 8 honeypot checks'
        '</div>',
        unsafe_allow_html=True
    )

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sidebar-section-header">\U0001F4E5 Custom Input</div>',
                unsafe_allow_html=True)

    # File upload
    uploaded_file = st.file_uploader(
        "Upload JSON",
        type=["json"],
        label_visibility="collapsed",
        help="Upload a .json file with an array of candidate objects.",
    )
    if uploaded_file is not None:
        try:
            raw = uploaded_file.read().decode("utf-8")
            candidates = parse_json_input(raw)
            st.success(f"\u2713 Loaded {len(candidates)} candidates")
            if st.button("\U0001F680 Run on Uploaded Data",
                         type="primary", use_container_width=True):
                with st.spinner("Ranking..."):
                    run_ranker(candidates, f"Upload: {len(candidates)} candidates")
        except Exception as e:
            st.error(f"Parse error: {e}")

    # Paste JSON
    with st.expander("\U0001F4DD Paste JSON", expanded=False):
        pasted_json = st.text_area(
            "", height=160,
            placeholder='[{"candidate_id": "CAND_0001", ...}]',
            label_visibility="collapsed",
        )
        if pasted_json.strip():
            try:
                candidates = parse_json_input(pasted_json)
                st.success(f"\u2713 Parsed {len(candidates)} candidates")
                if st.button("\U0001F680 Run on Pasted Data",
                             type="primary", use_container_width=True):
                    with st.spinner("Ranking..."):
                        run_ranker(candidates, f"Pasted: {len(candidates)} candidates")
            except Exception as e:
                st.error(f"Parse error: {e}")

    st.markdown('<hr style="border-color: rgba(255,255,255,0.05); margin: 1rem 0;">',
                unsafe_allow_html=True)

    # Sample data
    st.markdown('<div class="sidebar-section-header">\U0001F4CA Sample Data</div>',
                unsafe_allow_html=True)
    if st.button("\U0001F504 Run Sample (20 candidates)",
                 type="secondary", use_container_width=True):
        with st.spinner("Ranking sample data..."):
            if not os.path.exists(SAMPLE_PATH):
                st.error("Sample data not found")
                st.stop()
            with open(SAMPLE_PATH) as f:
                samples = json.load(f)
            run_ranker(samples, "Sample: 20 candidates")
            st.success("Done!")

    # Feature weights
    if "rankings" in st.session_state:
        import config as cfg
        st.markdown('<hr style="border-color: rgba(255,255,255,0.05); margin: 1rem 0;">',
                    unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-header">\u2696\uFE0F Weights</div>',
                    unsafe_allow_html=True)
        for name, weight in cfg.WEIGHTS.items():
            label = name.replace("_", " ").title()
            pct = weight * 100
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'color:#a0aec0;font-size:0.85rem;margin-bottom:0.2rem;">'
                f'<span>{label}</span><span>{pct:.0f}%</span></div>',
                unsafe_allow_html=True
            )
            st.progress(weight)

# ── Main content area ───────────────────────────────────────────────────────

if "rankings" in st.session_state:
    rankings = st.session_state["rankings"]
    total = st.session_state["total"]
    source = st.session_state.get("source", "")

    st.markdown(f'<div class="source-label">\U0001F4CC Source: {source}</div>',
                unsafe_allow_html=True)

    # ── Top-level metrics ──
    top_score = rankings[0][0]
    bottom_score = rankings[-1][0]
    honeypot_count = sum(1 for h in rankings if h[3] < 0.5)
    suspicious_count = sum(1 for h in rankings if 0.5 <= h[3] < 0.8)
    clean_count = total - honeypot_count - suspicious_count
    elapsed = st.session_state["elapsed"]

    metrics_html = f"""
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:0.8rem;margin-bottom:1.5rem;">
        {make_metric(f'{total:,}', 'Candidates')}
        {make_metric(f'{elapsed:.2f}s', 'Time')}
        {make_metric(f'{top_score:.4f}', 'Top Score')}
        {make_metric(f'{bottom_score:.4f}', 'Bottom Score')}
        {make_metric(f'{honeypot_count}', '\U0001F534 Honeypots', 'honeypot-metric')}
        {make_metric(f'{suspicious_count}', '\U0001F7E1 Suspicious', 'suspicious-metric')}
        {make_metric(f'{clean_count}', '\u2705 Clean', 'clean-metric')}
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Score distribution chart ──
    scores = [r[0] for r in rankings]
    penalties = [r[3] for r in rankings]

    fig = go.Figure()

    # Histogram with gradient
    fig.add_trace(go.Histogram(
        x=scores,
        nbinsx=25,
        name="Candidates",
        marker=dict(
            color=scores,
            colorscale=[[0, '#f56565'], [0.5, '#ed8936'], [1, '#48bb78']],
            line=dict(color='rgba(255,255,255,0.1)', width=1),
        ),
        hovertemplate="Score: %{x:.4f}<br>Count: %{y}<extra></extra>",
    ))

    # Vertical line for top score
    fig.add_vline(
        x=top_score,
        line_dash="dash",
        line_color="#667eea",
        annotation_text=f"Top: {top_score:.4f}",
        annotation_position="top left",
        annotation_font=dict(color="#667eea", size=11),
    )

    fig.update_layout(
        title=dict(
            text="<b>Score Distribution</b>",
            font=dict(color="#e2e8f0", size=16),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#a0aec0", size=12),
        xaxis=dict(
            title="Score",
            gridcolor="rgba(255,255,255,0.05)",
            zeroline=False,
        ),
        yaxis=dict(
            title="Candidates",
            gridcolor="rgba(255,255,255,0.05)",
            zeroline=False,
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        hovermode="x",
        bargap=0.06,
    )

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Honeypot pie chart ──
    labels = ["Clean", "Suspicious", "Honeypot"]
    values = [clean_count, suspicious_count, honeypot_count]
    colors = ["#48bb78", "#ed8936", "#f56565"]

    fig2 = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors, line=dict(color="#1a1a2e", width=2)),
        textinfo="label+percent",
        textfont=dict(color="#e2e8f0", size=13),
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
        hole=0.55,
    )])

    fig2.update_layout(
        title=dict(
            text="<b>Candidate Integrity</b>",
            font=dict(color="#e2e8f0", size=16),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#a0aec0", size=12),
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
        annotations=[dict(
            text=f"{clean_count}<br>Clean",
            x=0.5, y=0.5,
            font=dict(size=18, color="#48bb78"),
            showarrow=False,
        )],
    )

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Rankings list ──
    st.markdown(f'<h3 style="color:#e2e8f0;margin-bottom:1rem;">'
                f'\U0001F3C5 Rankings (Top {len(rankings)})</h3>',
                unsafe_allow_html=True)

    for rank, (score, cid, reasoning, penalty, issues) in enumerate(rankings, 1):
        badge = score_badge(penalty)
        pct = min(score * 100, 100)

        # Determine accent color for progress bar
        if penalty < 0.3:
            bar_color = "#f56565"
        elif penalty < 0.8:
            bar_color = "#ed8936"
        else:
            bar_color = "#48bb78"

        issues_html = ""
        if issues:
            issues_list = "; ".join(issues[:3])
            issues_html = f'<div class="issues-text">\u26A0\uFE0F {issues_list}</div>'

        card_html = f"""
        <div class="candidate-card" style="animation-delay:{rank * 0.03}s">
            <div style="display:flex;align-items:center;gap:1.2rem;flex-wrap:wrap;">
                <div class="candidate-rank">#{rank}</div>
                <div style="flex:1;min-width:120px;">
                    <div class="candidate-id">{cid}</div>
                    <div class="candidate-score" style="color:#a0aec0;font-size:0.85rem;">
                        Score: {score:.4f} &bull; Pen: {penalty:.2f}
                    </div>
                </div>
                <div>{badge}</div>
            </div>
            <div style="margin:0.5rem 0 0.3rem 0;height:4px;background:rgba(255,255,255,0.06);
                        border-radius:4px;overflow:hidden;">
                <div style="height:100%;width:{pct:.1f}%;background:{bar_color};
                            border-radius:4px;transition:width 1s ease;"></div>
            </div>
            <div style="color:#cbd5e0;font-size:0.9rem;line-height:1.4;margin-top:0.4rem;">
                {reasoning}
            </div>
            {issues_html}
        </div>
        """

        animation_delay = rank * 0.03
        card_html = card_html.replace("animation-delay:{rank * 0.03}s",
                                      f"animation-delay:{animation_delay}s")
        st.markdown(card_html.replace("animation-delay:{rank * 0.03}s",
                                      f"animation-delay:{animation_delay}s"),
                    unsafe_allow_html=True)

    # Clear button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("\U0001F5D1 Clear & Start Over",
                     type="secondary", use_container_width=True):
            for key in ["rankings", "elapsed", "total", "source"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

else:
    # ── Welcome state ──
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
                    border-radius:16px;padding:2rem;margin-bottom:1.5rem;">
            <h3 style="color:#e2e8f0;margin-top:0;">\U0001F44B Welcome!</h3>
            <p style="color:#a0aec0;font-size:1.05rem;line-height:1.6;">
            This tool ranks candidates for a <strong style="color:#e2e8f0;">Senior AI Engineer
            (Founding Team)</strong> role using a 10-component rule-based scoring engine.
            </p>
            <p style="color:#718096;font-size:0.95rem;">
            Choose one of the options in the <strong>sidebar</strong>:
            </p>
            <ul style="color:#a0aec0;line-height:1.8;padding-left:1.2rem;">
                <li>\U0001F4E5 <strong>Upload</strong> a JSON file of candidates</li>
                <li>\U0001F4DD <strong>Paste</strong> JSON data directly</li>
                <li>\U0001F4CA <strong>Run sample</strong> data (20 pre-loaded candidates)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        # Sample preview
        if os.path.exists(SAMPLE_PATH):
            with open(SAMPLE_PATH) as f:
                samples = json.load(f)
            st.markdown("""
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
                        border-radius:16px;padding:1.5rem;">
                <h4 style="color:#e2e8f0;margin-top:0;font-size:0.95rem;">
                    \U0001F4CB Candidate Preview
                </h4>
            """, unsafe_allow_html=True)
            for s in samples[:4]:
                p = s.get("profile", {})
                st.markdown(
                    f'<div style="color:#a0aec0;font-size:0.85rem;padding:0.3rem 0;'
                    f'border-bottom:1px solid rgba(255,255,255,0.04);">'
                    f'<strong style="color:#e2e8f0;">{p.get("anonymized_name", "?")}</strong>'
                    f' &mdash; {p.get("current_title", "?")} @ {p.get("current_company", "?")}'
                    f'<br><span style="color:#718096;">{p.get("location", "?")}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            st.markdown(
                f'<div style="color:#718096;font-size:0.8rem;padding-top:0.5rem;">'
                f'... and {len(samples) - 4} more</div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Algorithm details ──
    with st.expander("\U0001F4D6 About the Ranking Algorithm", expanded=False):
        col_tab1, col_tab2 = st.columns(2)
        with col_tab1:
            st.markdown("""
            ### Scoring Components
            | Component | Weight | Description |
            |---|---|---|
            | **Career Relevance** | 35% | Title tier, industry, startup bonus |
            | **Role Relevance** | 20% | Current title + headline match |
            | **Prod AI Evidence** | 14% | ML deployment + retrieval exp |
            | **Retrieval & Ranking** | 10% | Search/ranking systems |
            | **Behavioral Signals** | 10% | Response rate, GitHub activity |
            | **Experience Fit** | 5% | Peak 5–9 years |
            | **Skills Match** | 3% | Keyword coverage |
            | **Education** | 3% | Tier + field relevance |
            | **Location Bonus** | +3% | Pune/Noida preference |
            | **Notice Period** | +2% | Sub-30 day preference |
            """)
        with col_tab2:
            st.markdown("""
            ### Honeypot Detection
            8 checks to filter out low-quality profiles:
            - Timeline inconsistency
            - Overlapping education periods
            - AI skills without background
            - Missing/short descriptions
            - Job-hopping patterns
            - Summary mismatch
            - Career exceeds stated experience
            - Endorsement mismatch
            ### Performance
            **100K candidates** in ~92s (CPU-only)
            **13,135 honeypots** detected
            **0 honeypots** in top 100
            """)

st.markdown("""
<div style="margin-top:2rem;padding:1rem 0;border-top:1px solid rgba(255,255,255,0.05);
            text-align:center;color:#4a5568;font-size:0.8rem;">
    Built for the Redrob Hackathon &mdash; Intelligent Candidate Discovery &amp; Ranking Challenge
</div>
""", unsafe_allow_html=True)
