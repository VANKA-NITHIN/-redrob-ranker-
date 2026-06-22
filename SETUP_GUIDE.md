# Setup & Reproducibility Guide

## Redrob Hackathon — Intelligent Candidate Discovery & Ranking System

This guide provides step-by-step instructions for judges to reproduce the ranking results, run the system, and verify all constraints.

---

## Quick Start (3 Minutes)

```bash
# 1. Clone the repository
git clone https://github.com/VANKA-NITHIN/-redrob-ranker-.git
cd -redrob-ranker-

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the ranking pipeline (CPU-only, ~92 seconds)
python ranker.py

# 4. Validate the submission
python data/validate_submission.py output/submission.csv
```

**Expected output:** `Submission is valid.` ✅

---

## Detailed Setup

### Prerequisites

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| Python | 3.11 | 3.11+ |
| RAM | 8 GB | 16 GB |
| CPU | 4 cores | 8 cores |
| Disk | 500 MB | 1 GB |
| OS | Any (tested on Windows) | Linux/macOS/Windows |
| GPU | ❌ Not required | N/A |
| Network | ❌ Not required during ranking | N/A |

### Step 1: Clone the Repository

```bash
git clone https://github.com/VANKA-NITHIN/-redrob-ranker-.git
cd -redrob-ranker-
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` file contains:
```
python-docx>=1.2.0
streamlit>=1.30.0
plotly>=5.18.0
pandas>=2.0.0
openpyxl>=3.1.0
scikit-learn>=1.3.0
numpy>=1.24.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
```

All packages are CPU-only and widely available. No proprietary libraries.

### Step 3: Run the Ranking Pipeline

**Full run (100K candidates — generates submission):**
```bash
python ranker.py
```

**Run on sample data only (50 candidates — faster):**
```bash
python ranker.py --sample
```

**Validate existing submission:**
```bash
python ranker.py --validate
```

**View TF-IDF debug terms:**
```bash
python ranker.py --debug-terms
```

### Step 4: Validate the Output

```bash
python data/validate_submission.py output/submission.csv
```

Expected response:
```
Submission is valid.
```

---

## Running the Web Applications

### Option A: Streamlit UI (Full-Featured)

```bash
streamlit run app.py
```

Opens at `http://localhost:8501` with:
- File upload (JSON, CSV, Excel)
- Interactive rankings with search, filter, pagination
- Candidate profile viewer
- Candidate comparison tool
- Insight charts (score distribution, penalty analysis, skills)
- Dark/light theme toggle
- CSV/JSON export
- Bookmark candidates with notes

### Option B: FastAPI Backend + React Frontend

**Backend:**
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API docs at `http://localhost:8000/api/docs`

**Frontend (dev mode):**
```bash
cd frontend
npm install
npm run dev
```

**Frontend (production build — served by FastAPI):**
```bash
cd frontend
npm run build
# FastAPI automatically serves the built files at http://localhost:8000
```

### Option C: One-Command Launcher

```bash
python start.py
```

This starts the backend (port 8000) and frontend (port 5173) simultaneously.

---

## Running Tests

```bash
# Run all 80 unit tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=ranker --cov-report=term-missing
```

All 80 tests should pass.

---

## Submission Structure

```
├── ranker.py                     # Core ranking pipeline (3 phases, 20 checks, 17 dimensions)
├── config.py                     # All scoring weights and thresholds
├── app.py                        # Streamlit UI
├── api/
│   └── main.py                   # FastAPI backend
├── frontend/
│   └── src/                      # React frontend (TypeScript)
├── tests/
│   └── test_ranker.py            # 80 unit tests
├── data/
│   ├── sample_candidates.json    # 50 sample candidates
│   ├── candidate_schema.json     # JSON schema
│   └── validate_submission.py    # Submission validator
├── output/
│   └── submission.csv            # Final ranked output
├── TECHNICAL_ARCHITECTURE.md     # Architecture document
├── SETUP_GUIDE.md                # This file
└── pitch_deck.html               # Presentation pitch deck
```

---

## Verification Checklist

Judges can verify the following:

- [x] **Reproducibility:** `python ranker.py` produces the same `output/submission.csv`
- [x] **Format validation:** `python data/validate_submission.py output/submission.csv` returns "Valid"
- [x] **No honeypots in top 100:** Check `grep -i honeypot output/submission.csv` returns empty
- [x] **Unique reasonings:** All 100 candidates have different reasoning strings
- [x] **CPU-only:** No GPU used during ranking
- [x] **No network calls:** Runs offline, no API dependencies
- [x] **Under 5 minutes:** Full pipeline completes in ~92 seconds
- [x] **Under 16 GB RAM:** Peak memory <1 GB
- [x] **All tests pass:** `python -m pytest tests/ -v` — 80/80 pass

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Slow ranking | Ensure at least 8 GB RAM available. Close other applications. |
| Tests fail | Check Python version (3.11+ required). Reinstall dependencies. |
| `candidates.jsonl` not found | This file must be placed in the `data/` directory (not included in repo — download from hackathon platform). |
| Frontend build fails | Run `npm install` in the `frontend/` directory first. |

---

## Contact

**Team:** VANKA NITHIN  
**Repository:** https://github.com/VANKA-NITHIN/-redrob-ranker-  
**HuggingFace Space:** https://huggingface.co/spaces/vankanithin/redrob-ranker  
**Email:** vankanithin2004@gmail.com  
**Phone:** +91-7416234130  

---

*Built for the Redrob Hackathon — Intelligent Candidate Discovery & Ranking Challenge*  
*Challenge 1: Build an AI System*
