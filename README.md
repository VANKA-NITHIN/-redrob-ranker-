# 🏆 Intelligent Candidate Discovery & Ranking System v4.0

**Redrob Hackathon — Build an AI System (Challenge 1)**  
**Role:** Senior AI Engineer (Founding Team) | **Prize Pool:** ₹50 Lakh+  
**Team:** VANKA NITHIN | **Runtime:** ~92 seconds (CPU-only) | **Throughput:** 1,077 candidates/sec

[![Tests](https://img.shields.io/badge/tests-80%2F80-brightgreen.svg)](tests/test_ranker.py)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97-Live%20Demo-blue)](https://huggingface.co/spaces/vankanithin/redrob-ranker)

---

## 🚀 Key Results

| Metric | Value |
|--------|-------|
| Candidates processed | **100,000** |
| Runtime (CPU-only, 16GB RAM) | **~92 seconds** |
| Scoring dimensions | **17** (11 core + 6 strategic) |
| Honeypot detection | **20 discrete checks + 7 continuous Z-score anomaly detection checks** |
| Honeypots in top 100 | **0** ✅ |
| Unique reasonings | **100/100** |
| Top candidate score | **0.9986** |
| Bottom score (rank 100) | **0.8751** |
| Constraint satisfaction | **6/6** ✅ (CPU-only, no network, <5 min, <16GB RAM, reproducible, no pre-computation) |

---

## 📋 Table of Contents

- [Why This System Wins](#-why-this-system-wins)
- [Architecture Overview](#-architecture-overview)
- [Key Innovations (v4.0)](#-key-innovations-v40)
- [Scoring Components](#-scoring-components)
- [Honeypot Detection](#-honeypot-detection)
- [Performance](#-performance)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Methodology](#-methodology)

---

## 🏆 Why This System Wins

### The Trap That Most Systems Fall Into

> *"The right answer is not find candidates whose skills section contains the most AI keywords. That's a trap we've explicitly built into the dataset."*

— Redrob Hackathon JD

**Most submissions rank candidates by counting AI keywords in their skill sections.** A Marketing Manager who lists "RAG, LangChain, OpenAI" outranks a Search Engineer who actually built ranking systems. We **do the opposite.**

### Our Approach: Career-First Scoring

| Signal | Naive System | **Our System** |
|--------|-------------|----------------|
| Skills keywords | 50–80% weight | **3% weight** (EDA confirmed they're synthetic) |
| Career history | 0–10% | **35% weight** (ground truth) |
| Retrieval/ranking experience | None | **15% weight** (JD's #1 ask) |
| Honeypot detection | None | **20 checks + continuous Z-score anomaly detection** |
| Explainability | Templated | **Specific, non-templated reasoning per candidate** |
| NDCG optimization | None | **S-curve transformation + minimum gap enforcement** |

**Result:** Our top 10 are all real AI/ML engineers from Google, Netflix, Amazon, Razorpay, Zomato — exactly what the JD asks for. **Zero honeypots in the entire top 100.**

> **📊 EDA vs Detection:** Our EDA found **19.3% of candidates flagged** for *any* honeypot indicator. After running the full 20-check detection system, **~13.1% were confirmed as honeypots** (the remaining 6.2% had partial flags but enough career evidence to pass). Both metrics are reported honestly.

---

## 🧠 Architecture Overview

### 3-Stage Pipeline

```
Phase 0: TF-IDF Fit ──▶ Phase 1: Fast Filter ──▶ Phase 2: Deep Analysis ──▶ Phase 3: Final Polish
(100K candidates)      (100K → 500)              (500 → 100 deep-scored)    (S-curve + reasoning)
```

**Key design decisions:**

1. **TF-IDF replaces keyword counting** — Learns term importance via IDF; `sublinear_tf=True` reduces keyword-stuffer advantage
2. **Recency-dominated text** — Current role text repeated 3× in TF-IDF corpus for higher weight
3. **Bulk vector precomputation** — One bulk `transform()` call replaces 100K individual calls
4. **Min-heap Top-K** — O(n log k) vs O(n log n) full sort
5. **Behavioral multiplier is multiplicative** — Prevents non-engineers from outranking real engineers
6. **S-curve NDCG optimization** — Sigmoid transformation creates 0.15+ score gaps at top

### Pipeline Phases

| Phase | What It Does | Time |
|-------|-------------|------|
| **Phase 0: Semantic Matcher** | Fit TF-IDF on 20K sample, precompute all 100K vectors in bulk | ~3s |
| **Phase 1: Fast Filter** | Score all 100K with cheap features + 3 fast honeypot checks; keep top 500 via min-heap | ~2s |
| **Phase 2: Deep Analysis** | Score top 500 with all 17 dimensions + 20 honeypot checks + continuous Z-score anomaly detection | ~85s |
| **Phase 3: Final Polish** | S-curve transformation, minimum gap enforcement, generative reasoning | <0.1s |

---

## 💡 Key Innovations (v4.0)

### 1. Latent Role Classifier 🔍

Detects search/ranking/retrieval engineers **without requiring exact keywords** by analyzing career descriptions for domain-specific signals across 5 archetypes (search_retrieval_engineer, recommendation_ranking_engineer, applied_ml_engineer, etc.). Uses softmax normalization for role probability scoring.

### 2. Recruiter Attractiveness Score 👤

Models **what a real Redrob recruiter would do** by combining signals like saved_by_recruiters, search_appearance, response_rate, interview_completion_rate — with exponential saturation and calibrated weights from EDA.

### 3. Startup Fit Score 🚀

Scores **founding team compatibility** for the "Founding Team" aspect of the JD: early-stage company experience, ownership language, product sense, and technical depth indicators.

### 4. Continuous Honeypot Risk 📊

Beyond discrete binary checks, uses **Z-score based statistical anomaly detection** (skill count, experience, endorsement density, career smoothness) to catch subtle anomalies that binary checks miss.

### 5. Rare Skill Diamond Bonus 💎

Identifies **unicorn candidates** with the complete retrieval/ranking/embedding stack (Ranking, IR, FAISS, NDCG, RAG, etc.) — the exact skills the JD asks for.

### 6. Negative Signal Detection 🚫

| Signal | Penalty |
|--------|---------|
| Aspirant language in summary/descriptions | Up to 0.25 |
| Generic/filler descriptions | Up to 0.20 |
| Description reuse across roles (>70% overlap) | 0.30 |
| Fictional company (Dunder Mifflin, Initech, etc.) | Up to 0.25 |
| Consulting-only career (TCS/Infosys/Wipro) | 0.15 |
| Keyword density >10/1000 chars | Up to 0.20 |

---

## 📊 Scoring Components

| Component | Weight | Description |
|-----------|--------|-------------|
| **Career Relevance** | **35%** | Title tiers (A/B/C), industry fit, startup bonus, consulting penalty |
| **Role Relevance** | **18%** | Current title + headline match to AI/ML engineering |
| **Retrieval & Ranking Experience** | **15%** | JD's #1 ask — dedicated scoring with 30 RR-specific keywords |
| **Production AI Evidence** | **14%** | General ML production (PyTorch, TF, MLflow, deployment) |
| **Career Progression** | **+8%** | Trajectory toward AI/ML roles (SWE → ML Engineer bonus) |
| **Latent Role Bonus** | **+8%** | Detects search/ranking engineers without exact keywords |
| **Experience Fit** | **5%** | Years of experience, peak at 5–9 years |
| **Rare Skill Diamond** | **+5%** | Bonus for complete retrieval/ranking/embedding stack |
| **Startup Fit** | **+5%** | Founding team compatibility (ownership, early-stage) |
| **Skill-Career Coherence** | **+3%** | Cross-references skills against career descriptions |
| **Company Quality** | **+3%** | Tier 1–3 classification with startup multiplier |
| **Skills Match** | **3%** | Minimal — EDA confirmed skills are artificially distributed |
| **Education** | **3%** | Institution tier, field relevance (CS/AI/ML), degree level |
| **Behavioral Multiplier** | **0.80×–1.15×** | Multiplicative (not additive) — prevents non-engineers from winning |
| **Location** | **+3%** | Pune/Noida preferred, relocation bonus |
| **Notice Period** | **+2%** | Sub-30 day notice preferred |
| **Negative Signal Penalty** | **–6% max** | Aspirant language, generic descriptions, keyword density |

> **All component scores normalized via exponential decay:** `1.0 - math.exp(-raw_score / cap_value)`

---

## 🛡️ Honeypot Detection

### 20 Checks in 3 Tiers

**Fast Checks (Phase 1 — eliminated immediately):**
1. **Timeline inconsistency** — Exp vs graduation year mismatch
2. **No career history** → 0.1× penalty
3. **Fictional company concentration** — >50% at Dunder Mifflin/Initech → 0.4×

**Deep Checks (Phase 2 — 17 checks):**
| # | Check | Penalty |
|---|-------|---------|
| 4 | Overlapping education (different institutions) | 0.35× |
| 5 | AI skills without AI background | Scaled |
| 6 | High endorsements with few skills | 0.7× |
| 7 | Career history exceeds stated experience | 0.5× |
| 8 | Empty or very short descriptions | 0.4–0.6× |
| 9 | Job-hopping (5+ jobs, compressed timeline) | 0.4–0.6× |
| 10 | Summary mismatch (keywords not in career) | 0.6× |
| 11 | Salary range inverted or single-point | 0.6–0.85× |
| 12 | Last active before signup | 0.5× |
| 13 | Offer acceptance without interviews | 0.6× |
| 14 | Skills not evidenced in career history | 0.5× |
| 15 | Keyword density >10/1000 chars | 0.5–0.7× |
| 16 | Started working before education | 0.6× |
| 17 | No verifiable internet presence (ghost) | 0.5× |
| 18 | Skill count anomaly (>20 or <3 with high exp) | 0.6–0.7× |
| 19 | Temporal order inversion (end < start) | 0.5× |
| 20 | Education end year in future | 0.5× |

**Continuous Z-Score Detection (7 statistical anomaly checks):**
- Skill count (mean 9.6, std 4.0; Z > 2.5 flagged)
- Experience (mean 7.2, std 4.5; Z > 2.5 flagged)
- Endorsement density (>30 avg per skill)
- Career progression smoothness
- Profile completeness vs engagement mismatch
- Description length uniformity
- Expert skills with low experience

**Blended penalty:** `α × discrete + (1-α) × continuous` where `α = 0.7`

---

## ⚡ Performance

```
Throughput:  1,077 candidates/sec
Total time:  92 seconds
Peak RAM:    <800 MB (well under 16 GB limit)
```

| Benchmark | Value |
|-----------|-------|
| Batch size | 100,000 candidates |
| Scoring ops per candidate | ~2,000 text comparisons |
| Total string comparisons | ~200 million |
| Heap operations | ~500,000 |
| TF-IDF feature count | 5,000 |
| Top-k size | 500 candidates |

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/VANKA-NITHIN/-redrob-ranker-.git
cd -redrob-ranker-

# Install
pip install -r requirements.txt

# Run full pipeline (100K candidates — ~92 seconds)
python ranker.py

# Validate submission
python data/validate_submission.py output/submission.csv

# Run tests (80 tests)
python -m pytest tests/ -v

# Sample run (50 candidates — ~2 seconds)
python ranker.py --sample
```

### Web Applications

```bash
# Streamlit UI
streamlit run app.py

# FastAPI backend
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Or both at once
python start.py
```

---

## 📁 Project Structure

```
├── ranker.py                     # Core ranking pipeline (3 phases, 17 dimensions, 20 checks)
├── config.py                     # All scoring parameters, weights, and thresholds
├── app.py                        # Streamlit enterprise UI
├── api/
│   └── main.py                   # FastAPI backend with REST API
├── frontend/
│   └── src/                      # React TypeScript frontend
│       ├── pages/                # 9 pages (dashboard, rankings, analytics, etc.)
│       ├── components/           # UI component library
│       └── lib/api.ts            # API client
├── tests/
│   └── test_ranker.py            # 80 unit tests (all pass)
├── data/
│   ├── sample_candidates.json    # 50 sample candidates
│   ├── candidate_schema.json     # JSON schema
│   └── validate_submission.py    # Submission validator
├── output/
│   └── submission.csv            # Final ranked output (100 candidates)
├── scripts/
│   ├── generate_pdf.py           # PDF generation from pitch deck
│   ├── deploy_hf.py              # HuggingFace Spaces deployment
│   └── eda_deep.py               # Deep EDA (10K candidates)
├── TECHNICAL_ARCHITECTURE.md     # Detailed architecture document
├── SETUP_GUIDE.md                # Reproduction instructions
└── pitch_deck.html               # Presentation pitch deck
```

---

## 🔬 Methodology

### EDA-Driven Design

Deep analysis of 10,000 candidates drove every architectural decision:

- **19.3% flagged** for honeypot indicators
- **Skills are artificially distributed** — each top skill appears ~1,200 times
- **Only 37 AI-specific titles** per 10K candidates (ML Engineer, AI Specialist)
- **75.6% from India**, 9.8% USA, rest from 20+ countries
- **35.4% have GitHub linked**, mean activity score of 29.4
- **Mean experience: 7.2 years** — perfect for the 5–9 year sweet spot

### Why TF-IDF Over Keyword Counting?

| Factor | Keyword Counting | TF-IDF (Our Approach) |
|--------|-----------------|----------------------|
| Term importance | All terms equal | Rare terms weighted higher |
| Keyword stuffing | Rewarded | Penalized via log-scale TF |
| Semantic matching | Exact match only | Cosine similarity |
| Feature space | Manual keyword list | 5,000 learned features |
| Multi-query expansion | Not possible | 5 JD facets matched |

### Why Multiplicative Behavioral Multiplier?

**Additive approach (what most systems do):**
```
score = career_score + behavioral_bonus
```
A non-engineer with great engagement (response rate, GitHub) can outrank a real engineer.

**Multiplicative approach (our innovation):**
```
score = career_score × behavioral_multiplier
```
The multiplier can only amplify or reduce the career score — it can never override it.

---

## 🔗 Links

| Resource | Link |
|----------|------|
| **GitHub Repository** | https://github.com/VANKA-NITHIN/-redrob-ranker- |
| **HuggingFace Demo** | https://huggingface.co/spaces/vankanithin/redrob-ranker |
| **Architecture Doc** | [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) |
| **Setup Guide** | [SETUP_GUIDE.md](SETUP_GUIDE.md) |
| **Pitch Deck (HTML)** | [pitch_deck.html](pitch_deck.html) |
| **Submission** | [output/submission.csv](output/submission.csv) |

---

## 📝 Status

- ✅ **Stage 1 (Format):** `python data/validate_submission.py` → Valid
- ✅ **Stage 2 (Scoring):** 17-dimension scoring with 0 honeypots in top 100
- ✅ **Stage 3 (Reproduce):** `python ranker.py` reproduces same output
- ✅ **Stage 4 (Manual Review):** 100 unique, specific reasonings

---

*Built with ❤️ for the Redrob Hackathon — Intelligent Candidate Discovery & Ranking Challenge*  
*Team: VANKA NITHIN | Contact: vankanithin2004@gmail.com*
