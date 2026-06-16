"""
FastAPI backend for Redrob Enterprise AI Ranking Platform.
Serves ranking data from the Python ranker module via REST API.
"""
import json
import os
import sys
import time
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ranker import (
    process_candidates,
    compute_total_score,
    generate_reasoning,
    SemanticMatcher,
    build_candidate_text,
    detect_honeypot_fast,
    compute_cheap_score,
    latent_role_bonus,
    recruiter_attractiveness_score,
    startup_fit_score,
    FAST_FILTER_TOP_K,
    FINAL_TOP_K,
    s_curve_transform,
)

app = FastAPI(
    title="Redrob AI Talent Intelligence API",
    version="4.0.0",
    docs_url="/api/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")

# In-memory cache
_rankings_cache = None
_candidates_cache = None
_metrics_cache = None
_cache_timestamp = None


def _load_sample():
    """Load sample candidates for development/demo."""
    path = os.path.join(DATA_DIR, "sample_candidates.json")
    with open(path, "r") as f:
        return json.load(f)


def _get_or_compute():
    """Get cached results or compute on first request."""
    global _rankings_cache, _candidates_cache, _metrics_cache, _cache_timestamp
    if _rankings_cache is not None:
        return _rankings_cache, _candidates_cache, _metrics_cache

    start = time.time()
    samples = _load_sample()
    rankings = process_candidates(samples)

    elapsed = time.time() - start
    total = len(samples)

    hon_count = sum(1 for r in rankings if r[3] < 0.3)
    susp_count = sum(1 for r in rankings if 0.3 <= r[3] < 0.8)
    verified_count = total - hon_count - susp_count

    _rankings_cache = [
        {
            "rank": i + 1,
            "score": r[0],
            "candidateId": r[1],
            "reasoning": r[2],
            "penalty": r[3],
            "issues": r[4],
        }
        for i, r in enumerate(rankings)
    ]

    _candidates_cache = {
        c.get("candidate_id", ""): _flatten_candidate(c)
        for c in samples
    }

    _metrics_cache = {
        "totalCandidates": total,
        "processingTime": elapsed,
        "topScore": rankings[0][0] if rankings else 0,
        "bottomScore": rankings[-1][0] if rankings else 0,
        "honeypotCount": hon_count,
        "suspiciousCount": susp_count,
        "verifiedCount": verified_count,
        "source": "Sample Data",
    }

    _cache_timestamp = time.time()
    return _rankings_cache, _candidates_cache, _metrics_cache


def _flatten_candidate(c):
    """Convert nested candidate dict to flat API format."""
    p = c.get("profile", {})
    sig = c.get("redrob_signals", {})
    salary = sig.get("expected_salary_range_inr_lpa", {})
    return {
        "candidateId": c.get("candidate_id", ""),
        "profile": {
            "anonymizedName": p.get("anonymized_name", ""),
            "headline": p.get("headline", ""),
            "summary": p.get("summary", ""),
            "location": p.get("location", ""),
            "country": p.get("country", ""),
            "yearsOfExperience": p.get("years_of_experience", 0) or 0,
            "currentTitle": p.get("current_title", ""),
            "currentCompany": p.get("current_company", ""),
            "currentCompanySize": p.get("current_company_size", ""),
            "currentIndustry": p.get("current_industry", ""),
        },
        "careerHistory": [
            {
                "company": j.get("company", ""),
                "title": j.get("title", ""),
                "startDate": j.get("start_date", ""),
                "endDate": j.get("end_date"),
                "durationMonths": j.get("duration_months", 0) or 0,
                "isCurrent": j.get("is_current", False),
                "industry": j.get("industry", ""),
                "companySize": j.get("company_size", ""),
                "description": j.get("description", ""),
            }
            for j in c.get("career_history", [])
        ],
        "education": [
            {
                "institution": e.get("institution", ""),
                "degree": e.get("degree", ""),
                "fieldOfStudy": e.get("field_of_study", ""),
                "startYear": e.get("start_year", 0) or 0,
                "endYear": e.get("end_year", 0) or 0,
                "grade": e.get("grade", ""),
                "tier": e.get("tier", "tier_4"),
            }
            for e in c.get("education", [])
        ],
        "skills": [
            {
                "name": s.get("name", ""),
                "proficiency": s.get("proficiency", "beginner"),
                "endorsements": s.get("endorsements", 0),
            }
            for s in c.get("skills", [])
        ],
        "redrobSignals": {
            "profileCompletenessScore": sig.get("profile_completeness_score", 0),
            "openToWorkFlag": sig.get("open_to_work_flag", False),
            "recruiterResponseRate": sig.get("recruiter_response_rate", 0),
            "connectionCount": sig.get("connection_count", 0),
            "noticePeriodDays": sig.get("notice_period_days", 90),
            "expectedSalaryRangeInrLpa": {
                "min": salary.get("min", 0),
                "max": salary.get("max", 0),
            },
            "willingToRelocate": sig.get("willing_to_relocate", False),
            "githubActivityScore": sig.get("github_activity_score", -1),
            "searchAppearance30d": sig.get("search_appearance_30d", 0),
            "savedByRecruiters30d": sig.get("saved_by_recruiters_30d", 0),
            "interviewCompletionRate": sig.get("interview_completion_rate", 0),
            "verifiedEmail": sig.get("verified_email", False),
            "verifiedPhone": sig.get("verified_phone", False),
            "linkedinConnected": sig.get("linkedin_connected", False),
        },
    }


# ====== API Endpoints ======


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "4.0.0", "timestamp": time.time()}


@app.get("/api/rankings")
async def get_rankings():
    rankings, _, metrics = _get_or_compute()
    return {"rankings": rankings, "metrics": metrics}


@app.get("/api/candidates/{candidate_id}")
async def get_candidate(candidate_id: str):
    _, candidates, _ = _get_or_compute()
    if candidate_id not in candidates:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidates[candidate_id]


@app.get("/api/candidates/{candidate_id}/breakdown")
async def get_breakdown(candidate_id: str):
    """Compute full score breakdown for a candidate."""
    _, candidates, _ = _get_or_compute()
    if candidate_id not in candidates:
        raise HTTPException(status_code=404, detail="Candidate not found")
    # Re-fetch from ranker functions
    samples = _load_sample()
    candidate = None
    for c in samples:
        if c.get("candidate_id") == candidate_id:
            candidate = c
            break
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found in sample")

    score, penalty, issues = compute_total_score(candidate)
    profile = candidate.get("profile", {})
    sig = candidate.get("redrob_signals", {})
    # Compute sub-scores using ranker functions directly
    career_text = build_candidate_text(candidate)
    lat_role = latent_role_bonus(career_text, candidate.get("skills", []), candidate.get("career_history", []))
    recruiter_attr = recruiter_attractiveness_score(sig)
    start_fit = startup_fit_score(career_text, candidate.get("career_history", []), profile.get("current_company", ""))
    return {
        "candidateId": candidate_id,
        "totalScore": round(score, 4),
        "honeypotPenalty": round(penalty, 4),
        "issues": issues,
        "latentRole": round(lat_role, 4),
        "recruiterAttractiveness": round(recruiter_attr, 4),
        "startupFit": round(start_fit, 4),
    }

@app.get("/api/honeypot")
async def get_honeypot():
    """Return honeypot detection statistics."""
    samples = _load_sample()
    hon_count = 0
    flags = 0
    clean = 0
    for c in samples:
        total_issues = 0
        # Run basic honeypot checks
        if c.get("profile", {}).get("years_of_experience", 0) > 15:
            total_issues += 1
        if len(c.get("career_history", [])) > 8:
            total_issues += 1
        if sum(1 for s in c.get("skills", []) if s.get("name", "") in {"Python", "Machine Learning", "NLP", "Deep Learning"}) > 6:
            total_issues += 1
        if total_issues >= 3:
            hon_count += 1
        elif total_issues >= 1:
            flags += total_issues
        else:
            clean += 1
    return {
        "totalDetected": hon_count,
        "totalFlags": flags,
        "cleanProfiles": clean,
        "detectionRate": round((hon_count / len(samples)) * 100, 1) if samples else 0,
        "violationBreakdown": [
            {"name": "Timeline Inconsistencies", "count": hon_count, "color": "#ef4444"},
            {"name": "Excessive Career Entries", "count": sum(1 for c in samples if len(c.get("career_history", [])) > 8), "color": "#f59e0b"},
            {"name": "Skill Count Anomalies", "count": sum(1 for c in samples if len(c.get("skills", [])) > 25), "color": "#eab308"},
            {"name": "High Experience Drought", "count": sum(1 for c in samples if c.get("profile", {}).get("years_of_experience", 0) > 20), "color": "#06b6d4"},
        ],
        "riskDistribution": [
            {"name": "Low Risk (0-10%)", "value": max(clean, 1), "color": "#10b981"},
            {"name": "Medium Risk (11-30%)", "value": max(flags, 1), "color": "#f59e0b"},
            {"name": "Critical (61-100%)", "value": max(hon_count, 1), "color": "#ef4444"},
        ],
        "multiHitDistribution": [
            {"hits": "0 flags", "count": max(clean, 1)},
            {"hits": "1-2 flags", "count": max(flags, 1)},
            {"hits": "3+ flags", "count": max(hon_count, 1)},
        ],
    }


@app.get("/api/analytics")
async def get_analytics():
    """Compute pool-wide analytics."""
    samples = _load_sample()
    skills = {}
    count = len(samples)
    for c in samples:
        for s in c.get("skills", []):
            name = s.get("name", "")
            skills[name] = skills.get(name, 0) + 1

    top_skills = sorted(skills.items(), key=lambda x: -x[1])[:15]
    return {
        "scoreDistribution": [],
        "penaltyDistribution": [],
        "experienceDistribution": [],
        "topSkills": [
            {"skill": k, "count": v} for k, v in top_skills
        ],
        "educationTiers": [],
        "issueBreakdown": [],
        "countryDistribution": [],
        "totalCandidates": count,
    }


@app.get("/api/run")
async def run_pipeline(source: Optional[str] = Query(None)):
    """Re-run the ranking pipeline and invalidate cache."""
    global _rankings_cache, _cache_timestamp
    _rankings_cache = None
    _cache_timestamp = None
    rankings, _, metrics = _get_or_compute()
    return {"rankings": rankings, "metrics": metrics}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
