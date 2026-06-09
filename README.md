# Redrob Hackathon — Intelligent Candidate Discovery & Ranking System

Ranks **100,000 candidates** for a **Senior AI Engineer (Founding Team)** role using a multi-component rule-based scoring engine. Runs entirely on CPU in under **2 minutes**.

## 🏆 Performance

| Metric | Value |
|--------|-------|
| Candidates processed | 100,000 |
| Runtime (CPU only) | ~92 seconds |
| Top score | 0.9135 |
| Bottom score (rank 100) | 0.7526 |
| Honeypots detected | 13,135 (13.1%) |
| Honeypots in top 100 | **0** ✅ |
| Submission validation | ✅ Passed |
| Tests | 34/34 ✅ |

## 🧠 Architecture

### Scoring Components (Weighted)

| Component | Weight | Description |
|-----------|--------|-------------|
| **Career Relevance** | 35% | Title tiers (A/B/C), industry fit, startup bonus, consulting penalty |
| **Role Relevance** | 20% | Current title + headline match to AI/ML engineering |
| **Production AI Evidence** | 14% | General ML production experience (PyTorch, TF, MLflow, etc.) |
| **Retrieval & Ranking Exp** | **10%** | JD's #1 ask: search/ranking/retrieval/recommendation systems |
| **Behavioral Signals** | 10% | Response rate, GitHub, interview completion, profile engagement |
| **Experience Fit** | 5% | Years of experience, peak at 5–9 years |
| **Skills Match** | 3% | Minimal — EDA confirmed skills are artificially distributed (~1,200 each) |
| **Education** | 3% | Institution tier, field relevance (CS/AI/ML), degree level |
| **Location** | +3% | Pune/Noida preferred, relocation bonus per JD |
| **Notice Period** | +2% | Sub-30 day notice preferred per JD |

### Honeypot Detection (8 Checks)

1. **Timeline inconsistency** — graduated recently but has implausible years of experience
2. **Overlapping education** — attended multiple institutions concurrently (13% of candidates)
3. **AI skills without AI background** — advanced AI skills but no AI education or career history
4. **Endorsement/skill mismatch** — very few skills but unusually high endorsements
5. **Career history exceeds stated experience** — sum of job durations exceeds stated YoE
6. **Missing/short descriptions** — empty or very short (<30 chars) career descriptions
7. **Job-hopping / zero-duration jobs** — 5+ jobs with 0 reported duration or compressed timeline
8. **Summary mismatch** — many production AI keywords in summary but none in career history

## 📊 EDA Insights

Based on analysis of 10,000 candidates:

- **19.3% flagged** for honeypot indicators (timeline, overlapping education, etc.)
- **Skills are artificially distributed** — each top skill appears ~1,200 times (HTML, React, Databricks, etc.)
- **Very few AI-specific titles** — only 18 ML Engineers, 19 AI Specialists per 10K
- **75.6% from India**, 9.8% USA, rest from 20+ countries
- **35.4% have GitHub linked**, mean activity score of 29.4
- **Mean experience: 7.2 years** — perfect for the 5–9 year sweet spot
- **0.0% no career history**, 0.0% no education — dataset is structurally consistent

## 🚀 Usage

```bash
# Full pipeline (100K candidates)
python ranker.py

# Run on sample data only (50 candidates)
python ranker.py --sample

# Validate existing submission
python ranker.py --validate

# Or validate manually
python data/validate_submission.py output/submission.csv
```

### Output

Generates `output/submission.csv` with 100 ranked candidates:

```csv
candidate_id,rank,score,reasoning
CAND_0018499,1,0.9135,"Senior Machine Learning Engineer; 7yrs at Zomato; built retrieval, ranking, search, embeddings systems; responsive; actively looking; short notice; based Noida, Uttar Pradesh (pref location)"
```

### Constraints

- ✅ CPU-only (no GPU)
- ✅ No network calls during ranking
- ✅ Under 5 minutes for 100K candidates
- ✅ No pre-computation required
- ✅ Pure Python — no external ML dependencies

## ⚙️ Configuration

All scoring parameters are in [`config.py`](config.py):

- `WEIGHTS` — component importance in final score
- `TIER_A/B/C_TITLES` — job title classification
- `PRODUCTION_AI_KEYWORDS` — search/ranking/retrieval system keywords
- `CONSULTING_FIRMS` — firms that trigger career penalty
- `SIGNAL_WEIGHTS` — Redrob behavioral signal importance
- `AI_CORE_SKILLS`, `AI_INFRA_SKILLS` — skill relevance categories

## 🗂️ Project Structure

```
├── config.py                  # Scoring parameters & weights
├── ranker.py                  # Main ranking pipeline
├── app.py                     # Streamlit UI (HuggingFace Spaces)
├── eda.py                     # Basic EDA (sample data)
├── submission_metadata.yaml   # Hackathon submission metadata
├── pitch_deck.html            # Pitch deck (print to PDF)
├── tests/
│   ├── test_ranker.py         # 34 unit tests
│   └── __init__.py
├── scripts/
│   ├── eda_deep.py            # Deep EDA (10K candidates)
│   ├── sweep.py               # Parameter sweep
│   └── extract_docs.py        # Docx extraction tools
├── data/
│   ├── candidates.jsonl       # 100K candidate profiles (487 MB)
│   ├── sample_candidates.json # 50 sample candidates
│   ├── candidate_schema.json  # JSON schema
│   └── validate_submission.py # Submission validator
└── output/
    └── submission.csv         # Final ranked output
```

## 🔍 Methodology

1. **Streaming pipeline** — reads candidates line-by-line from JSONL (memory efficient)
2. **Multi-dimensional scoring** — combines 10 weighted components with exponential normalization
3. **Top-K heap** — maintains top 100 candidates via min-heap (O(n log k))
4. **Honeypot filtering** — 8 detection checks with multiplicative penalties
5. **Deterministic tie-breaking** — rounded scores + candidate_id ascending for reproducible rankings

### Key Design Decisions

- **Career history over skills** — JD explicitly warns against keyword-matching on skills; EDA confirmed skills are artificially distributed
- **Production AI focus** — highest signal for retrieval/ranking/search/recommendation system experience
- **Startup bonus** — product company + startup size = ideal for founding team role
- **Consulting penalty** — 50% score reduction if entire career is at TCS/Infosys/Accenture/etc.
