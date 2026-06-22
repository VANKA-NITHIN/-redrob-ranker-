"""
FastAPI backend for Redrob Enterprise AI Ranking Platform.
Serves ranking data from the Python ranker module via REST API.
Also serves the built React frontend as static files.
"""
import json
import os
import sys
import time
from collections import Counter
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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
    behavioral_multiplier,
    career_history_score,
    role_relevance_score,
    production_ai_evidence_score,
    retrieval_ranking_experience_score,
    skills_match_score,
    experience_fit_score,
    education_score,
    negative_signal_penalty,
    skill_career_coherence_score,
    career_progression_score,
    company_quality_score,
    location_preference_score,
    notice_period_score,
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
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

# In-memory cache
_rankings_cache = None
_candidates_cache = None
_metrics_cache = None
_raw_samples_cache = None
_cache_timestamp = None


def _load_sample():
    """Load sample candidates for development/demo."""
    global _raw_samples_cache
    if _raw_samples_cache is not None:
        return _raw_samples_cache
    path = os.path.join(DATA_DIR, "sample_candidates.json")
    with open(path, "r", encoding="utf-8") as f:
        _raw_samples_cache = json.load(f)
    return _raw_samples_cache


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

    # Build candidate lookup
    candidate_map = {}
    for c in samples:
        candidate_map[c.get("candidate_id", "")] = c

    hon_count = sum(1 for r in rankings if r[3] < 0.3)
    susp_count = sum(1 for r in rankings if 0.3 <= r[3] < 0.8)
    verified_count = total - hon_count - susp_count

    _rankings_cache = []
    for i, r in enumerate(rankings):
        cid = r[1]
        raw = candidate_map.get(cid, {})
        profile = raw.get("profile", {})
        sig = raw.get("redrob_signals", {})
        badge = "honeypot" if r[3] < 0.3 else ("suspicious" if r[3] < 0.8 else "verified")
        _rankings_cache.append({
            "rank": i + 1,
            "score": r[0],
            "candidateId": cid,
            "reasoning": r[2],
            "penalty": r[3],
            "issues": r[4],
            "badge": badge,
            # Enriched fields for display
            "name": profile.get("anonymized_name", ""),
            "title": profile.get("current_title", ""),
            "company": profile.get("current_company", ""),
            "location": profile.get("location", ""),
            "country": profile.get("country", ""),
            "experience": profile.get("years_of_experience", 0) or 0,
            "headline": profile.get("headline", ""),
            "skills": [s.get("name", "") for s in raw.get("skills", [])[:8]],
            "education": raw.get("education", [{}])[0].get("institution", "") if raw.get("education") else "",
            "openToWork": sig.get("open_to_work_flag", False),
            "noticePeriod": sig.get("notice_period_days", 90),
        })

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


def _compute_full_breakdown(candidate):
    """Compute all 17 score dimensions for a candidate."""
    profile = candidate.get("profile", {})
    sig = candidate.get("redrob_signals", {})
    yoe = profile.get("years_of_experience", 0) or 0

    career = career_history_score(candidate)
    role = role_relevance_score(candidate)
    prod_ai = production_ai_evidence_score(candidate)
    rr_exp = retrieval_ranking_experience_score(candidate)
    exp_fit = experience_fit_score(yoe)
    skills = skills_match_score(candidate)
    edu = education_score(candidate)
    progression = career_progression_score(candidate)
    coherence = skill_career_coherence_score(candidate)
    company = company_quality_score(candidate)
    neg_penalty = negative_signal_penalty(candidate)

    lat_role = latent_role_bonus(candidate)
    recruiter_attr = recruiter_attractiveness_score(candidate)
    start_fit = startup_fit_score(candidate)
    beh_mult = behavioral_multiplier(candidate)

    loc = location_preference_score(candidate)
    notice = notice_period_score(candidate)

    # Honeypot penalty from compute_total_score
    _, penalty, issues = compute_total_score(candidate)

    # Normalize scores to 0-1 range for display
    def norm(v, mx=10.0):
        return max(0.0, min(1.0, v / mx))

    return {
        "careerRelevance": norm(career, 20),
        "roleRelevance": norm(role, 8),
        "productionAiEvidence": norm(prod_ai, 15),
        "retrievalRankingExperience": norm(rr_exp, 20),
        "experienceFit": exp_fit,
        "skillsMatch": norm(skills, 20),
        "educationScore": norm(edu, 5),
        "careerProgression": progression,
        "coherence": coherence,
        "companyQuality": company,
        "latentRole": norm(lat_role, 3),
        "recruiterAttractiveness": recruiter_attr,
        "startupFit": norm(start_fit, 1),
        "behavioralMultiplier": beh_mult,
        "locationBonus": norm(loc, 1.3),
        "noticeBonus": norm(notice, 1),
        "negativePenalty": neg_penalty,
        "honeypotPenalty": penalty,
        "issues": issues,
    }


# ====== API Endpoints ======

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "4.0.0", "timestamp": time.time()}


@app.get("/api/rankings")
async def get_rankings():
    try:
        rankings, _, metrics = _get_or_compute()
        return {"rankings": rankings, "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ranking computation failed: {str(e)}")


@app.get("/api/candidates/{candidate_id}")
async def get_candidate(candidate_id: str):
    try:
        _, candidates, _ = _get_or_compute()
        if candidate_id not in candidates:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return candidates[candidate_id]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load candidate: {str(e)}")


@app.get("/api/candidates/{candidate_id}/breakdown")
async def get_breakdown(candidate_id: str):
    """Compute full score breakdown for a candidate with all 17 dimensions."""
    try:
        _, candidates, _ = _get_or_compute()
        if candidate_id not in candidates:
            raise HTTPException(status_code=404, detail="Candidate not found")

        samples = _load_sample()
        candidate = None
        for c in samples:
            if c.get("candidate_id") == candidate_id:
                candidate = c
                break
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found in sample")

        breakdown = _compute_full_breakdown(candidate)
        breakdown["candidateId"] = candidate_id
        return breakdown
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Breakdown computation failed: {str(e)}")


@app.get("/api/search")
async def search_candidates(
    q: Optional[str] = Query(None, description="Free-text search"),
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    location: Optional[str] = Query(None, description="Location filter"),
    title: Optional[str] = Query(None, description="Title filter"),
    min_score: float = Query(0, description="Minimum score (0-1)"),
    min_experience: int = Query(0, description="Minimum years of experience"),
    sort: str = Query("score", description="Sort by: score, experience, name"),
):
    """Search candidates with multi-dimensional filtering."""
    try:
        rankings, _, _ = _get_or_compute()

        results = list(rankings)

        # Free text search
        if q:
            ql = q.lower()
            results = [r for r in results if (
                ql in r["candidateId"].lower() or
                ql in r["title"].lower() or
                ql in r["company"].lower() or
                ql in r["location"].lower() or
                ql in r["reasoning"].lower() or
                any(ql in s.lower() for s in r.get("skills", []))
            )]

        # Skills filter
        if skills:
            skill_list = [s.strip().lower() for s in skills.split(",")]
            results = [r for r in results if
                any(any(sl in sk.lower() for sl in skill_list) for sk in r.get("skills", []))]

        # Location filter
        if location:
            loc_lower = location.lower()
            results = [r for r in results if loc_lower in r.get("location", "").lower()]

        # Title filter
        if title:
            title_lower = title.lower()
            results = [r for r in results if title_lower in r.get("title", "").lower()]

        # Score filter
        if min_score > 0:
            results = [r for r in results if r["score"] >= min_score]

        # Experience filter
        if min_experience > 0:
            results = [r for r in results if r.get("experience", 0) >= min_experience]

        # Sort
        if sort == "experience":
            results.sort(key=lambda x: x.get("experience", 0), reverse=True)
        elif sort == "name":
            results.sort(key=lambda x: x["candidateId"])
        else:
            results.sort(key=lambda x: x["score"], reverse=True)

        return {"results": results, "totalResults": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/api/compare")
async def compare_candidates(ids: str = Query(..., description="Comma-separated candidate IDs")):
    """Compare multiple candidates side by side."""
    try:
        id_list = [i.strip() for i in ids.split(",")]
        rankings, candidates, _ = _get_or_compute()
        samples = _load_sample()

        results = []
        for cid in id_list:
            if cid not in candidates:
                continue
            # Get ranking info
            rank_info = next((r for r in rankings if r["candidateId"] == cid), None)
            # Get raw candidate for breakdown
            raw = next((c for c in samples if c.get("candidate_id") == cid), None)
            if not raw or not rank_info:
                continue

            breakdown = _compute_full_breakdown(raw)
            results.append({
                "candidateId": cid,
                "rank": rank_info["rank"],
                "score": rank_info["score"],
                "badge": rank_info["badge"],
                "title": rank_info["title"],
                "company": rank_info["company"],
                "location": rank_info["location"],
                "experience": rank_info["experience"],
                "skills": rank_info["skills"],
                "breakdown": breakdown,
                "profile": candidates[cid]["profile"],
            })

        return {"candidates": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@app.get("/api/honeypot")
async def get_honeypot():
    """Return honeypot detection statistics computed from the ranking results."""
    try:
        rankings, _, _ = _get_or_compute()
        samples = _load_sample()

        # Count from actual ranking results
        hon_count = sum(1 for r in rankings if r["badge"] == "honeypot")
        susp_count = sum(1 for r in rankings if r["badge"] == "suspicious")
        clean_count = sum(1 for r in rankings if r["badge"] == "verified")

        total = len(samples)
        total_flags = 0

        # Gather issues from ranking results
        issue_counter = Counter()
        for r in rankings:
            issues = r.get("issues", [])
            total_flags += len(issues)
            for issue in issues:
                issue_counter[issue] += 1

        # Build violation breakdown from actual issues
        colors = ["#ef4444", "#f97316", "#f59e0b", "#eab308", "#06b6d4", "#8b5cf6", "#6366f1", "#3b82f6"]
        violation_items = []
        for idx, (name, count) in enumerate(issue_counter.most_common(8)):
            violation_items.append({
                "name": name[:40],
                "count": count,
                "color": colors[idx % len(colors)],
            })

        # If no issues detected from ranker, provide basic stats from raw data
        if not violation_items:
            timeline_issues = sum(1 for c in samples
                if (c.get("profile", {}).get("years_of_experience", 0) or 0) > 20)
            career_issues = sum(1 for c in samples if len(c.get("career_history", [])) > 8)
            skill_issues = sum(1 for c in samples if len(c.get("skills", [])) > 25)
            exp_issues = sum(1 for c in samples
                if (c.get("profile", {}).get("years_of_experience", 0) or 0) > 15)
            violation_items = [
                {"name": "Timeline Inconsistencies", "count": max(timeline_issues, 1), "color": "#ef4444"},
                {"name": "Excessive Career Entries", "count": max(career_issues, 1), "color": "#f59e0b"},
                {"name": "Skill Count Anomalies", "count": max(skill_issues, 1), "color": "#eab308"},
                {"name": "High Experience Outliers", "count": max(exp_issues, 1), "color": "#06b6d4"},
            ]

        return {
            "totalDetected": hon_count,
            "totalFlags": total_flags,
            "cleanProfiles": clean_count,
            "detectionRate": round((hon_count / max(total, 1)) * 100, 1),
            "violationBreakdown": violation_items,
            "riskDistribution": [
                {"name": "Low Risk (Verified)", "value": max(clean_count, 1), "color": "#10b981"},
                {"name": "Medium Risk (Suspicious)", "value": max(susp_count, 1), "color": "#f59e0b"},
                {"name": "Critical (Honeypot)", "value": max(hon_count, 1), "color": "#ef4444"},
            ],
            "multiHitDistribution": [
                {"hits": "0 flags", "count": max(clean_count, 1)},
                {"hits": "1-2 flags", "count": max(susp_count, 1)},
                {"hits": "3+ flags", "count": max(hon_count, 1)},
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Honeypot analysis failed: {str(e)}")


@app.get("/api/analytics")
async def get_analytics():
    """Compute pool-wide analytics from real data."""
    try:
        rankings, _, _ = _get_or_compute()
        samples = _load_sample()

        # Score distribution
        score_buckets = Counter()
        for r in rankings:
            bucket = min(9, int(r["score"] * 10)) / 10
            key = f"{bucket:.1f}-{bucket + 0.1:.1f}"
            score_buckets[key] += 1
        score_dist = [{"range": k, "count": v} for k, v in sorted(score_buckets.items())]

        # Experience distribution
        exp_buckets = Counter()
        for c in samples:
            yoe = c.get("profile", {}).get("years_of_experience", 0) or 0
            if yoe < 2:
                exp_buckets["0-2 yrs"] += 1
            elif yoe < 5:
                exp_buckets["2-5 yrs"] += 1
            elif yoe < 10:
                exp_buckets["5-10 yrs"] += 1
            elif yoe < 15:
                exp_buckets["10-15 yrs"] += 1
            else:
                exp_buckets["15+ yrs"] += 1
        exp_dist = [{"range": k, "count": v} for k, v in exp_buckets.items()]

        # Skills distribution
        skill_counter = Counter()
        for c in samples:
            for s in c.get("skills", []):
                skill_counter[s.get("name", "")] += 1
        top_skills = [{"skill": k, "count": v} for k, v in skill_counter.most_common(15)]

        # Country distribution
        country_counter = Counter()
        for c in samples:
            country = c.get("profile", {}).get("country", "Unknown") or "Unknown"
            country_counter[country] += 1
        country_dist = [{"country": k, "count": v} for k, v in country_counter.most_common(10)]

        # Education tier distribution
        tier_counter = Counter()
        for c in samples:
            for e in c.get("education", []):
                tier = e.get("tier", "tier_4")
                tier_counter[tier] += 1
        edu_tiers = [{"tier": k.replace("_", " ").title(), "count": v} for k, v in tier_counter.most_common()]

        # Penalty distribution
        penalty_buckets = Counter()
        for r in rankings:
            p = r.get("penalty", 1.0)
            if p >= 0.8:
                penalty_buckets["Clean (0.8-1.0)"] += 1
            elif p >= 0.5:
                penalty_buckets["Suspicious (0.5-0.8)"] += 1
            elif p >= 0.3:
                penalty_buckets["Warning (0.3-0.5)"] += 1
            else:
                penalty_buckets["Honeypot (0-0.3)"] += 1
        penalty_dist = [{"range": k, "count": v} for k, v in penalty_buckets.items()]

        # Issue breakdown
        issue_counter = Counter()
        for r in rankings:
            for issue in r.get("issues", []):
                issue_counter[issue] += 1
        issue_breakdown = [{"issue": k[:50], "count": v} for k, v in issue_counter.most_common(10)]

        # Experience vs Score scatter data
        scatter_data = []
        for r in rankings:
            scatter_data.append({
                "experience": r.get("experience", 0),
                "score": round(r["score"], 4),
            })

        return {
            "scoreDistribution": score_dist,
            "penaltyDistribution": penalty_dist,
            "experienceDistribution": exp_dist,
            "topSkills": top_skills,
            "educationTiers": edu_tiers,
            "issueBreakdown": issue_breakdown,
            "countryDistribution": country_dist,
            "scatterData": scatter_data,
            "totalCandidates": len(samples),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics computation failed: {str(e)}")


@app.get("/api/run")
async def run_pipeline(source: Optional[str] = Query(None)):
    """Re-run the ranking pipeline and invalidate cache."""
    global _rankings_cache, _candidates_cache, _metrics_cache, _raw_samples_cache, _cache_timestamp
    _rankings_cache = None
    _candidates_cache = None
    _metrics_cache = None
    _raw_samples_cache = None
    _cache_timestamp = None
    try:
        rankings, _, metrics = _get_or_compute()
        return {"rankings": rankings, "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


# ====== Static file serving for frontend ======

# Mount static assets if the frontend is built
if os.path.isdir(FRONTEND_DIST):
    # Serve static assets (JS, CSS, images)
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Serve other static files (favicon, etc)
    @app.get("/favicon.svg")
    async def favicon():
        fpath = os.path.join(FRONTEND_DIST, "favicon.svg")
        if os.path.exists(fpath):
            return FileResponse(fpath)
        raise HTTPException(status_code=404)

    # SPA fallback — catch all non-API routes and serve index.html
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't serve index.html for API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)

        # Try to serve the exact file
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # Fall back to index.html for SPA routing
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

        raise HTTPException(status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
