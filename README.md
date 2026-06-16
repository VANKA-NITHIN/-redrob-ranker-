# Redrob Hackathon — Intelligent Candidate Discovery & Ranking System v3.0

Ranks **100,000 candidates** for a **Senior AI Engineer (Founding Team)** role using a multi-stage ranking pipeline with TF-IDF semantic matching, behavioral multipliers, and 20 honeypot detection checks. Runs entirely on CPU within **5 minutes** and **16 GB RAM**.

## 🏆 Key Innovations (v3.0)

| Innovation | Impact |
|-----------|--------|
| **TF-IDF Semantic Matcher** | Replaces keyword counting — learns term importance via IDF, reduces keyword-stuffer advantage with `sublinear_tf=True` |
| **3-Stage Pipeline** | Fast-filter (all 100K) → Deep analysis (top 500) → Final polish (top 100); frees compute for expensive features |
| **Behavioral Multiplier** | Redrob signals now MULTIPLY base score (0.80x–1.15x) instead of adding — prevents well-behaved non-engineers from outranking real engineers |
| **S-Curve NDCG Optimization** | Sigmoid transformation creates 0.15+ score gaps between top candidates for NDCG@10 advantage |
| **20 Honeypot Checks** | Comprehensive detection including: fictional companies, keyword density, ghost scores, temporal inversions, career progression coherence |
| **Negative Signal Detection** | Penalizes aspirant language, generic descriptions, keyword density, fictional/reused content |
| **Skill-Career Coherence** | Cross-references skills against career descriptions — keyword-stuffed skills without evidence get penalized |
| **Career Progression Signal** | Rewards intentional career moves toward AI/ML (e.g., SWE → ML Engineer) |
| **Company Quality Scoring** | Tier 1–3 company classification with startup bonus, consulting penalty |

## 🧠 Architecture

### Multi-Stage Pipeline

```
Phase 0: TF-IDF Fit ──▶ Phase 1: Fast Filter ──▶ Phase 2: Deep Analysis ──▶ Phase 3: Final Polish
(R build    )       (100K→500 candidates)  (500→100 deep-scored)    (S-curve + reasoning)
```

### Scoring Components (NDCG-optimized)

| Component | Weight | Description |
|-----------|--------|-------------|
| **Career Relevance** | 25% | Title tiers (A/B/C), industry fit, startup bonus, consulting penalty |
| **Retrieval & Ranking Exp** | **18%** | JD's #1 ask — dedicated scoring, not just sub-component |
| **Role Relevance** | 15% | Current title + headline match to AI/ML engineering |
| **Production AI Evidence** | 14% | General ML production experience (PyTorch, TF, MLflow, etc.) |
| **Career Progression** | +10% | Intentional career trajectory toward AI/ML roles |
| **Experience Fit** | 4% | Years of experience, peak at 5–9 years |
| **Education** | 2% | Institution tier, field relevance (CS/AI/ML), degree level |
| **Skills Match** | 1% | Minimal — EDA confirmed skills are artificially distributed |
| **Skill-Career Coherence** | +4% | Cross-reference skills against career descriptions |
| **Company Quality** | +3% | Tier 1–3 bonus with startup multiplier |
| **Negative Signal Penalty** | –7% max | Aspirant language, generic descriptions, keyword density |
| **Behavioral Multiplier** | 0.80x–1.15x | Multiplicative: profile engagement × recruiter signals × GitHub |
| **Location** | +3% | Pune/Noida preferred, relocation bonus |
| **Notice Period** | +2% | Sub-30 day notice preferred |

### Honeypot Detection (20 Checks)

**Fast Checks (Phase 1):**
1. **Timeline inconsistency** — graduated recently but has implausible years of experience
2. **No career history** — empty career history = immediate elimination
3. **Fictional company concentration** — >50% jobs at made-up companies (Dunder Mifflin, Initech, etc.)

**Deep Checks (Phase 2):**
4. **Overlapping education** — attended multiple institutions concurrently
5. **AI skills without AI background** — advanced AI skills but no AI education or career history
6. **Endorsement/skill mismatch** — very few skills but unusually high endorsements
7. **Career history exceeds stated experience** — sum of job durations exceeds stated YoE
8. **Missing/short descriptions** — empty or very short career descriptions
9. **Job-hopping / zero-duration jobs** — 5+ jobs with 0 reported duration or compressed timeline
10. **Summary mismatch** — many production AI keywords in summary but none in career history
11. **Salary range anomalies** — inverted (min > max) or single-point salary
12. **Signup/active date mismatch** — last active before signup date
13. **Offer acceptance without interviews** — >50% offer rate with 0% interview completion
14. **Skill-career mismatch** — 4+ AI skills not evidenced in career history
15. **Keyword density anomaly** — >10 AI keyword mentions per 1000 chars
16. **Impossible age/timeline** — started working before (or during early) education
17. **Ghost score** — no verifiable internet presence (GitHub, recruiter saves, email/phone verification)
18. **Skill count anomaly** — >20 skills or <3 skills with >5yr experience
19. **Temporal order inversion** — job end date before start date
20. **Education end year in future** — unrealistic graduation year

### Negative Signal Detection

- **Aspirant language** — "self-learner", "transitioning toward", "explored ChatGPT", "side project", etc.
- **Generic descriptions** — "business diagnostics", "stakeholder management", "process re-engineering"
- **Description reuse** — >70% overlap between different role descriptions
- **Fictional companies** — Dunder Mifflin, Initech, Pied Piper, etc.
- **Consulting-only background** — entire career at TCS/Infosys/Wipro/Accenture
- **Keyword density** — >10 AI keyword mentions per 1000 chars

## 📊 EDA Insights

Based on analysis of 10,000 candidates:

- **19.3% flagged** for honeypot indicators (timeline, overlapping education, etc.)
- **Skills are artificially distributed** — each top skill appears ~1,200 times (HTML, React, Databricks, etc.)
- **Very few AI-specific titles** — only 18 ML Engineers, 19 AI Specialists per 10K
- **75.6% from India**, 9.8% USA, rest from 20+ countries
- **35.4% have GitHub linked**, mean activity score of 29.4
- **Mean experience: 7.2 years** — perfect for the 5–9 year sweet spot

## 🚀 Usage

```bash
# Full pipeline (100K candidates)
python ranker.py

# Run on sample data only (50 candidates)
python ranker.py --sample

# Validate existing submission
python ranker.py --validate

# View TF-IDF debug terms
python ranker.py --debug-terms

# Or validate manually
python data/validate_submission.py output/submission.csv
```

### Output

Generates `output/submission.csv` with 100 ranked candidates:

```csv
candidate_id,rank,score,reasoning
CAND_0018499,1,0.9135,"Senior Machine Learning Engineer; 7yrs at Zomato; built retrieval, ranking, search embeddings systems; responsive; actively looking; short notice; based Noida (pref location)"
```

### Constraints

- ✅ CPU-only (no GPU)
- ✅ No network calls during ranking
- ✅ Under 5 minutes for 100K candidates
- ✅ Under 16 GB RAM
- ✅ No pre-computation required — run from scratch each time

## ⚙️ Configuration

All scoring parameters are in [`config.py`](config.py):

- `WEIGHTS` — component importance in final score
- `TIER_A/B/C_TITLES` — job title classification
- `PRODUCTION_AI_KEYWORDS` — search/ranking/retrieval system keywords
- `CONSULTING_FIRMS` — firms that trigger career penalty
- `FICTIONAL_COMPANIES` — known honeypot company names
- `ASPIRANT_PHRASES` — negative signal language patterns
- `JD_INTENT_TEXT` — query text for TF-IDF semantic matching
- `AI_CORE_SKILLS`, `RR_SPECIFIC_SKILLS` — skill relevance categories
- `COMPANY_TIER_1/2/3` — company quality tiers
- `SCURVE_STEEPNESS`, `SCURVE_MIDPOINT` — NDCG optimization parameters

## 🗂️ Project Structure

```
├── config.py                  # Scoring parameters & weights
├── ranker.py                  # Multi-stage ranking pipeline
├── app.py                     # Streamlit UI (HuggingFace Spaces)
├── eda.py                     # Basic EDA (sample data)
├── submission_metadata.yaml   # Hackathon submission metadata
├── tests/
│   ├── test_ranker.py         # 50 unit tests (all pass)
│   └── __init__.py
├── scripts/
│   ├── eda_deep.py            # Deep EDA (10K candidates)
│   ├── sweep.py               # Parameter sweep
│   ├── extract_docs.py        # Docx extraction tools
│   └── generate_pdf.py        # PDF generation
├── data/
│   ├── candidates.jsonl       # 100K candidate profiles
│   ├── sample_candidates.json # 50 sample candidates
│   ├── candidate_schema.json  # JSON schema
│   └── validate_submission.py # Submission validator
└── output/
    └── submission.csv         # Final ranked output
```

## 🔍 Methodology

1. **Phase 0: TF-IDF Semantic Matcher** — Fits TfidfVectorizer on all candidate corpora; uses JD intent text as query vector; cosine similarity = semantic intent match
2. **Phase 1: Fast Filter** — Cheap features (TF-IDF similarity + title tier + experience + location) + fast honeypot check; keeps top 500 via min-heap
3. **Phase 2: Deep Analysis** — Full scoring with all 9 dimensions, negative signal penalties, behavioral multiplier, and 20 honeypot checks
4. **Phase 3: Final Polish** — S-curve sigmoid transformation for NDCG@10 optimization + generative reasoning + honeypot ratio verification

### Key Design Decisions

- **Behavioral multiplier replaces additive** — Prevents non-engineers with good signals from outranking real engineers
- **TF-IDF replaces keyword counting** — Learned IDF weights naturally penalize common terms; `sublinear_tf=True` reduces keyword-stuffer advantage
- **Career history over skills** — JD explicitly warns against keyword-matching on skills; skills weight reduced to 1%
- **Retrieval & ranking dedicated component** — JD's explicit #1 ask; not a sub-score but a top-weighted dimension
- **Fictional companies** — 17 known honeypot companies with concentration penalty
- **S-curve only when scores warrant** — Adaptive: skips transformation if max score < 0.5 (low-quality pool)
