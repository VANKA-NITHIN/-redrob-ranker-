"""
Redrob Hackathon - Intelligent Candidate Discovery & Ranking System
Ranks 100k candidates for a Senior AI Engineer role using feature-weighted scoring.
CPU-only, 5-min constraint compliant.

Usage:
    python ranker.py                     # Full run
    python ranker.py --validate          # Validate submission only
    python ranker.py --sample            # Run on sample data only
"""
import json
import math
import os
import sys
import time
import heapq

from config import (
    TIER_A_TITLES, TIER_B_TITLES, TIER_C_TITLES,
    PRODUCTION_AI_KEYWORDS, RETRIEVAL_RANKING_KEYWORDS, GENERAL_AI_KEYWORDS,
    CONSULTING_FIRMS, PRODUCT_COMPANY_KEYWORDS, STARTUP_SIZE_KEYWORDS,
    AI_CORE_SKILLS, AI_INFRA_SKILLS, GENERAL_TECH_SKILLS,
    IDEAL_EXPERIENCE_YEARS, EXPERIENCE_MIN, EXPERIENCE_MAX,
    TIER_WEIGHTS, RELEVANT_FIELDS, SIGNAL_WEIGHTS, WEIGHTS,
    PREFERRED_LOCATIONS,
)

DATA_DIR = "data"
OUTPUT_DIR = "output"

TOP_K = 100


def _title_tier(title: str) -> int:
    """Classify a job title into Tier A (2), Tier B (1), or Tier C (-1)."""
    tl = title.lower()
    if any(kw in tl for kw in TIER_A_TITLES):
        return 2
    elif any(kw in tl for kw in TIER_B_TITLES):
        return 1
    elif any(kw in tl for kw in TIER_C_TITLES):
        return -1
    return 0  # Neutral


def production_ai_evidence_score(candidate: dict) -> float:
    """Score evidence of building production AI/ranking/search/recommendation systems.
    This is the CORE signal the JD asks for."""
    history = candidate.get("career_history", [])
    profile = candidate.get("profile", {})

    score = 0.0

    # Check all career descriptions for production AI keywords
    for job in history:
        desc = (job.get("description") or "").lower()
        title = (job.get("title") or "").lower()

        # Count production AI keyword matches (excluding retrieval/ranking which has its own component)
        match_count = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in desc and kw not in RETRIEVAL_RANKING_KEYWORDS)
        score += match_count * 0.4

        # Extra weight if the title itself signals production AI work
        if _title_tier(title) == 2 and match_count > 0:
            score += 0.8

    # Also check summary
    summary = (profile.get("summary") or "").lower()
    summary_matches = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in summary and kw not in RETRIEVAL_RANKING_KEYWORDS)
    score += summary_matches * 0.2

    # Check skills for production-relevant skills
    skills = candidate.get("skills", [])
    skill_names = set(s["name"] for s in skills)
    prod_skills = {"PyTorch", "TensorFlow", "Transformers", "MLflow",
                    "Weights & Biases", "WandB", "Docker", "Kubernetes",
                    "AWS", "GCP", "Azure", "Airflow", "Spark",
                    "Fine-tuning LLMs", "LLM", "RAG", "LoRA", "PEFT",
                    "XGBoost", "scikit-learn"}
    prod_skill_count = len(skill_names & prod_skills)
    score += prod_skill_count * 0.3

    return score  # Raw score, will be normalized in compute_total_score


def retrieval_ranking_experience_score(candidate: dict) -> float:
    """Dedicated scoring for retrieval, ranking, search, and recommendation systems.
    The JD's #1 specific signal — separate weight per winning strategy."""
    history = candidate.get("career_history", [])
    profile = candidate.get("profile", {})
    score = 0.0

    # Scan all career descriptions for retrieval/ranking keywords
    for job in history:
        desc = (job.get("description") or "").lower()
        title = (job.get("title") or "").lower()
        industry = (job.get("industry") or "").lower()
        is_current = job.get("is_current", False)
        duration = job.get("duration_months", 0) or 0

        match_count = sum(1 for kw in RETRIEVAL_RANKING_KEYWORDS if kw in desc)

        recency_mult = 2.0 if is_current else max(1.0, duration / 12)
        job_score = match_count * 0.8 * recency_mult

        # Title bonus: Search Engineer, Recommendation Engineer, Relevance Engineer
        title_lower = title.lower()
        if any(kw in title_lower for kw in ["search", "recommendation", "relevance", "retrieval", "ranking"]):
            job_score += 2.0 * recency_mult

        # Industry bonus: specifically recruiting/HR-tech/talent
        if "recruit" in industry or "talent" in industry or "hr" in industry or "hiring" in industry:
            job_score += 1.0

        score += job_score

    # Summary bonus
    summary = (profile.get("summary") or "").lower()
    summary_matches = sum(1 for kw in RETRIEVAL_RANKING_KEYWORDS if kw in summary)
    score += summary_matches * 0.5

    # Skills bonus for retrieval/ranking specific tools
    skills = candidate.get("skills", [])
    skill_names = set(s["name"] for s in skills)
    rr_skills = {"FAISS", "Pinecone", "Milvus", "Weaviate", "ChromaDB", "Qdrant",
                  "Elasticsearch", "OpenSearch", "Solr",
                  "Information Retrieval", "Ranking", "Learning to Rank",
                  "Semantic Search", "Vector Search", "Embeddings",
                  "NDCG", "MRR", "Evaluation", "A/B Testing"}
    rr_skill_count = len(skill_names & rr_skills)
    score += rr_skill_count * 0.8

    return score


def location_preference_score(candidate: dict) -> float:
    """Score location match against JD preferences.
    JD: Pune/Noida preferred, Tier-1 Indian cities OK, willing to relocate."""
    profile = candidate.get("profile", {})
    location = (profile.get("location") or "").lower()
    country = (profile.get("country") or "").lower()
    signals = candidate.get("redrob_signals", {})
    willing_relocate = signals.get("willing_to_relocate", False)

    score = 0.0

    if country != "india":
        # Outside India: case-by-case per JD, no work visa sponsorship
        score += 0.15
        return score

    # Preferred locations: Pune or Noida (using config PREFERRED_LOCATIONS)
    if any(city in location for city in PREFERRED_LOCATIONS):
        score += 1.0
    # Delhi NCR
    elif any(city in location for city in ["delhi", "gurgaon", "gurugram"]):
        score += 0.8
    # Other Tier-1 Indian cities
    elif any(city in location for city in ["mumbai", "hyderabad", "bangalore", "bengaluru", "chennai"]):
        score += 0.6
    # Other Indian cities
    else:
        score += 0.3

    # Relocation bonus
    if willing_relocate:
        score += 0.3

    return score


def notice_period_score(candidate: dict) -> float:
    """Score notice period. JD prefers sub-30 day notice."""
    signals = candidate.get("redrob_signals", {})
    notice = signals.get("notice_period_days", 90) or 90

    if notice <= 15:
        return 1.0
    elif notice <= 30:
        return 0.8
    elif notice <= 60:
        return 0.5
    elif notice <= 90:
        return 0.3
    else:
        return 0.1


def career_history_score(candidate: dict) -> float:
    """Score career history for AI/ML engineering relevance.
    This is the MOST important signal (35% of final weight)."""
    history = candidate.get("career_history", [])
    if not history:
        return 0.0

    total_score = 0.0
    has_current_ai_role = False
    consulting_only = True  # Assume true unless proven otherwise

    for i, job in enumerate(history):
        title = (job.get("title") or "")
        desc = (job.get("description") or "").lower()
        company = (job.get("company") or "").lower()
        industry = (job.get("industry") or "").lower()
        company_size = (job.get("company_size") or "")
        is_current = job.get("is_current", False)
        duration = job.get("duration_months", 0) or 0

        # Weight: current/recent jobs matter more
        recency_weight = 2.5 if is_current else max(1.0, duration / 12)

        job_score = 0.0

        # --- Title tier scoring ---
        tier = _title_tier(title)
        if tier == 2:
            job_score += 4.0  # Tier A: directly relevant
            if is_current:
                has_current_ai_role = True
        elif tier == 1:
            job_score += 2.0  # Tier B: adjacent
        elif tier == -1:
            job_score -= 1.0  # Tier C: penalize

        # --- Production AI evidence in description ---
        prod_matches = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in desc)
        job_score += prod_matches * 0.5

        # --- General AI/ML experience ---
        gen_ai_matches = sum(1 for kw in GENERAL_AI_KEYWORDS if kw in desc)
        job_score += gen_ai_matches * 0.2

        # --- Industry relevance ---
        is_product_co = any(kw in industry for kw in PRODUCT_COMPANY_KEYWORDS)
        if is_product_co:
            job_score += 0.5

        # --- Company size for startup fit ---
        is_startup = any(sz in company_size for sz in STARTUP_SIZE_KEYWORDS)
        if is_startup and is_product_co:
            job_score += 0.5  # Startup + product = ideal

        # --- Check if non-consulting ---
        if company not in CONSULTING_FIRMS:
            consulting_only = False

        total_score += job_score * recency_weight

    # --- Consulting penalty (only if ENTIRE career is at consulting firms) ---
    if consulting_only and len(history) >= 1:
        total_score *= 0.5  # 50% penalty for pure consulting background

    return max(total_score, 0.0)


def role_relevance_score(candidate: dict) -> float:
    """Score the current role for direct relevance to Senior AI Engineer."""
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "") or ""
    headline = profile.get("headline", "") or ""
    summary = profile.get("summary", "") or ""

    score = 0.0

    # Current title tier
    tier = _title_tier(title)
    if tier == 2:
        score += 3.0
    elif tier == 1:
        score += 1.0
    elif tier == -1:
        score -= 1.0

    # Headline relevance
    hl = headline.lower()
    prod_matches = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in hl)
    score += prod_matches * 0.5

    gen_ai_matches = sum(1 for kw in GENERAL_AI_KEYWORDS if kw in hl)
    score += gen_ai_matches * 0.2

    return max(score, 0.0)


def skills_match_score(candidate: dict) -> float:
    """Score candidates skills against JD requirements.
    MINIMAL weight per JD warning - don't keyword-match on skills."""
    skills = candidate.get("skills", [])
    if not skills:
        return 0.0

    score = 0.0
    skill_names = set(s["name"] for s in skills)

    # Only count production-relevant AI skills (not generic AI keywords)
    for s in skills:
        name = s["name"]
        prof = s.get("proficiency", "beginner")
        endorsements = s.get("endorsements", 0)
        prof_mult = {"beginner": 0.5, "intermediate": 1.0, "advanced": 1.5, "expert": 2.0}.get(prof, 1.0)
        end_mult = 1 + min(endorsements, 30) / 100

        # Production AI skills get highest weight
        if name in {"FAISS", "Pinecone", "Milvus", "Weaviate", "ChromaDB",
                     "Information Retrieval", "Ranking", "Learning to Rank",
                     "Semantic Search", "Vector Search", "Embeddings",
                     "NDCG", "MRR", "Evaluation"}:
            score += 2.0 * prof_mult * end_mult
        elif name in AI_CORE_SKILLS:
            score += 0.8 * prof_mult * end_mult
        elif name in AI_INFRA_SKILLS:
            score += 0.5 * prof_mult * end_mult

    return score


def experience_fit_score(years: float) -> float:
    """Score years of experience. Ideal is 5-9 years, peak at 7."""
    if years <= 0:
        return 0.0

    if years < 2:
        return 0.1
    elif years < 4:
        return 0.3 + 0.2 * (years - 2) / 2
    elif years <= 9:
        # Peak between 5-9 years
        if years <= 5:
            return 0.5 + 0.4 * (years - 4) / 1
        elif years <= 7:
            return 0.9 + 0.1 * (years - 5) / 2
        else:
            return 1.0 - 0.1 * (years - 7) / 2
    elif years <= 12:
        return 0.8 - 0.15 * (years - 9) / 3
    elif years <= 15:
        return 0.5 - 0.15 * (years - 12) / 3
    else:
        return max(0.1, 0.35 - 0.05 * (years - 15))


def education_score(candidate: dict) -> float:
    """Score education background."""
    edus = candidate.get("education", [])
    if not edus:
        return 0.0

    score = 0.0
    max_tier_score = 0
    has_relevant_field = False

    for edu in edus:
        tier = edu.get("tier", "tier_4")
        field = (edu.get("field_of_study") or "").lower()
        degree = (edu.get("degree") or "").lower()
        grade = (edu.get("grade") or "")

        tier_score = TIER_WEIGHTS.get(tier, 1.0)
        max_tier_score = max(max_tier_score, tier_score)

        # Field relevance
        field_score = 0.0
        if any(rf in field for rf in RELEVANT_FIELDS):
            field_score = 2.0
            has_relevant_field = True

        # Degree level bonus
        degree_score = 0.0
        if any(d in degree for d in ["ph.d", "phd", "doctorate"]):
            degree_score = 2.0
        elif any(d in degree for d in ["m.tech", "m.e.", "m.sc", "master", "ms"]):
            degree_score = 1.5
        elif any(d in degree for d in ["b.tech", "b.e.", "b.sc", "bachelor"]):
            degree_score = 1.0

        # Grade bonus
        grade_score = 0.0
        try:
            if "cgpa" in grade.lower():
                val = float(grade.split()[0])
                if val >= 8.0:
                    grade_score = 0.5
                elif val >= 7.0:
                    grade_score = 0.3
            elif "%" in grade:
                val = float(grade.replace("%", ""))
                if val >= 85:
                    grade_score = 0.5
                elif val >= 75:
                    grade_score = 0.3
        except (ValueError, IndexError):
            pass

        score += (tier_score * 0.3 + field_score * 0.4 + degree_score * 0.2 + grade_score * 0.1)

    # Normalize by number of educations
    if edus:
        score = score / len(edus)

    # Bonus for having relevant field at a good institution
    if has_relevant_field and max_tier_score >= 2.0:
        score *= 1.2

    return min(score, 5.0)


def redrob_signals_score(candidate: dict) -> float:
    """Score Redrob behavioral signals."""
    signals = candidate.get("redrob_signals", {})
    if not signals:
        return 0.0

    score = 0.0

    # Profile completeness (0-100)
    completeness = signals.get("profile_completeness_score", 0)
    score += (completeness / 100) * 0.10

    # Recruiter response rate (0-1)
    resp_rate = signals.get("recruiter_response_rate", 0)
    if resp_rate >= 0:
        score += resp_rate * 0.20

    # Interview completion rate (0-1)
    interview_rate = signals.get("interview_completion_rate", 0)
    if interview_rate >= 0:
        score += interview_rate * 0.15

    # Search appearance (normalized, capped)
    search_app = signals.get("search_appearance_30d", 0)
    score += min(search_app / 200, 1.0) * 0.10

    # Saved by recruiters
    saved = signals.get("saved_by_recruiters_30d", 0)
    score += min(saved / 20, 1.0) * 0.15

    # GitHub activity score (-1 = no GitHub)
    github = signals.get("github_activity_score", -1)
    if github >= 0:
        score += (github / 100) * 0.10

    # Connection count (normalized)
    connections = signals.get("connection_count", 0)
    score += min(connections / 500, 1.0) * 0.05

    # Endorsements
    endorsements = signals.get("endorsements_received", 0)
    score += min(endorsements / 50, 1.0) * 0.05

    # Willing to relocate
    if signals.get("willing_to_relocate", False):
        score += 0.05

    # Verified email & phone
    if signals.get("verified_email", False):
        score += 0.03
    if signals.get("verified_phone", False):
        score += 0.02

    # Open to work bonus
    if signals.get("open_to_work_flag", False):
        score += 0.05

    # Notice period penalty (shorter = better)
    notice = signals.get("notice_period_days", 90)
    if notice <= 30:
        score += 0.05
    elif notice <= 60:
        score += 0.03
    elif notice >= 120:
        score -= 0.02

    # Salary expectations reasonableness check
    salary = signals.get("expected_salary_range_inr_lpa", {})
    s_min = salary.get("min", 0) if salary else 0
    s_max = salary.get("max", 0) if salary else 0
    if s_max > 0 and s_min > 0:
        # For Senior AI Engineer, reasonable range is 15-50 LPA
        if 15 <= s_min <= 50 and 20 <= s_max <= 80:
            score += 0.03

    return max(0.0, min(score, 1.0))


def detect_honeypot(candidate: dict) -> tuple:
    """
    Detect honeypot (impossible) candidates.
    Returns (penalty_multiplier, issues_list).
    1.0 = clean, 0.0 = certain honeypot.
    """
    penalty = 1.0
    issues = []

    profile = candidate.get("profile", {})
    edus = candidate.get("education", [])
    skills = candidate.get("skills", [])
    history = candidate.get("career_history", [])
    signals = candidate.get("redrob_signals", {})
    years_exp = profile.get("years_of_experience", 0)
    summary = (profile.get("summary") or "").lower()

    # --- Check 1: Timeline inconsistency ---
    if edus:
        edu_end_years = [e.get("end_year", 0) or 0 for e in edus]
        latest_edu_end = max(edu_end_years) if edu_end_years else 0
        edu_start_years = [e.get("start_year", 0) or 0 for e in edus]
        earliest_edu_start = min(edu_start_years) if edu_start_years else 0

        if latest_edu_end > 0 and years_exp > 0:
            # If they graduated recently but have way too much experience
            years_since_graduation = 2026 - latest_edu_end
            if years_exp > years_since_graduation + 5 and years_since_graduation >= 0:
                severity = (years_exp - years_since_graduation - 5) / 10
                penalty *= max(0.0, 1.0 - severity)
                issues.append(f"timeline: {years_exp}yrs exp but graduated {latest_edu_end} ({years_since_graduation}yrs ago)")

    # --- Check 2: Overlapping education from different institutions ---
    if len(edus) >= 2:
        for i in range(len(edus)):
            for j in range(i + 1, len(edus)):
                e1 = edus[i]
                e2 = edus[j]
                if e1.get("institution") != e2.get("institution"):
                    s1, e1_end = e1.get("start_year", 0) or 0, e1.get("end_year", 0) or 0
                    s2, e2_end = e2.get("start_year", 0) or 0, e2.get("end_year", 0) or 0
                    if s1 and s2 and e1_end and e2_end:
                        # Check if they overlap
                        if not (e1_end <= s2 or e2_end <= s1):
                            # EDA: 13% of candidates have this pattern - clear honeypot signal
                            penalty *= 0.35
                            issues.append(f"overlapping education: {e1['degree']}@{e1['institution']}({s1}-{e1_end}) & {e2['degree']}@{e2['institution']}({s2}-{e2_end})")

    # --- Check 3: AI skills but no AI background ---
    skill_names = set(s["name"] for s in skills)
    ai_skill_overlap = len(skill_names & AI_CORE_SKILLS)

    if ai_skill_overlap >= 2:
        has_ai_edu = any(
            "intelligence" in (e.get("field_of_study", "") or "").lower() or
            "learning" in (e.get("field_of_study", "") or "").lower() or
            "data science" in (e.get("field_of_study", "") or "").lower() or
            "computer science" in (e.get("field_of_study", "") or "").lower()
            for e in edus
        )
        has_ai_role = any(
            "ai" in (h.get("title", "") or "").lower() or
            "ml" in (h.get("title", "") or "").lower() or
            "machine learning" in (h.get("title", "") or "").lower() or
            "data scientist" in (h.get("title", "") or "").lower()
            for h in history
        )
        # EDA: mean skills = 9.6, threshold=4 balances catching honeypots vs false positives
        if not has_ai_edu and not has_ai_role and ai_skill_overlap >= 4:
            severity = min(1.0, ai_skill_overlap / 10)
            penalty *= (1.0 - severity * 0.5)
            issues.append(f"suspicious: {ai_skill_overlap} AI skills but no AI edu/role")

    # --- Check 4: Skill endorsements vs skill count mismatch ---
    high_endorsements = any(s.get("endorsements", 0) >= 50 for s in skills)
    low_skill_count = len(skills) <= 3
    if high_endorsements and low_skill_count:
        penalty *= 0.7
        issues.append(f"suspicious: high endorsements but only {len(skills)} skills")

    # --- Check 5: Career history exceeds stated experience ---
    if len(history) >= 2:
        total_career_months = sum(h.get("duration_months", 0) or 0 for h in history)
        total_career_years = total_career_months / 12
        if total_career_years > years_exp + 3 and years_exp > 0:
            penalty *= 0.5
            issues.append(f"career history ({total_career_years:.0f}yrs) exceeds stated exp ({years_exp}yrs)")

    # --- Check 6: Missing or very short career descriptions (suspicious) ---
    min_desc_length = float('inf')
    all_empty = True
    for job in history:
        desc = job.get("description") or ""
        if desc:
            all_empty = False
            min_desc_length = min(min_desc_length, len(desc))
    if history and all_empty:
        penalty *= 0.4
        issues.append("all career descriptions are empty")
    elif history and min_desc_length < 30:
        penalty *= 0.6
        issues.append(f"career description too short ({min_desc_length} chars)")

    # --- Check 7: Job-hopping pattern (5+ jobs with very short durations) ---
    if len(history) >= 5:
        total_months = sum(job.get("duration_months", 0) or 0 for job in history)
        total_years = total_months / 12
        zero_duration = sum(1 for job in history if (job.get("duration_months", 0) or 0) == 0)
        if zero_duration >= 3:
            penalty *= 0.5
            issues.append(f"{zero_duration}/{len(history)} jobs have 0 duration")
        elif total_years < 6 and total_years > 0:
            severity = min(1.0, (5 - total_years) / 5)
            penalty *= (1.0 - severity * 0.4)
            issues.append(f"job hopping: {len(history)} jobs in {total_years:.1f}yrs")

    # --- Check 8: Summary has production AI keywords but zero career history matches ---
    if summary:
        prod_keywords_in_summary = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in summary)
        if prod_keywords_in_summary >= 8:
            hist_desc = " ".join([(h.get("description") or "").lower() for h in history])
            prod_in_hist = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in hist_desc)
            if prod_in_hist == 0:
                penalty *= 0.6
                issues.append(f"summary has {prod_keywords_in_summary} prod AI keywords but no career matches")

    # --- Check 9: Salary range min > max (impossible salary) ---
    salary = signals.get("expected_salary_range_inr_lpa", {})
    if salary:
        s_min = salary.get("min", 0) or 0
        s_max = salary.get("max", 0) or 0
        if s_min > s_max and s_max > 0:
            penalty *= 0.6
            issues.append(f"salary range inverted: min={s_min}L > max={s_max}L")
        elif s_min == s_max and s_min > 0:
            # Single-point salary is suspicious unless consulting
            penalty *= 0.85
            issues.append(f"salary range single point: {s_min}L")

    # --- Check 10: Signup date after last active date ---
    signup = signals.get("signup_date", "")
    last_active = signals.get("last_active_date", "")
    if signup and last_active:
        try:
            signup_parts = signup.split("-")
            active_parts = last_active.split("-")
            if len(signup_parts) == 3 and len(active_parts) == 3:
                signup_tuple = tuple(int(p) for p in signup_parts)
                active_tuple = tuple(int(p) for p in active_parts)
                if active_tuple < signup_tuple:
                    penalty *= 0.5
                    issues.append(f"last active {last_active} before signup {signup}")
        except (ValueError, IndexError):
            pass

    # --- Check 11: Offer acceptance rate with zero interview history ---
    offer_rate = signals.get("offer_acceptance_rate", -1)
    interview_rate = signals.get("interview_completion_rate", 0)
    if offer_rate > 0.5 and interview_rate == 0:
        penalty *= 0.6
        issues.append(f"offer acceptance {offer_rate:.0%} but 0% interview completion")

    return penalty, issues


def compute_total_score(candidate: dict) -> tuple:
    """Compute final composite score for a candidate.
    Strategy: Career History >> Skills; JD warns against keyword-matching on skills.
    Multi-component: career, role, production AI, retrieval/ranking, behavioral, exp, skills, education.
    """
    profile = candidate.get("profile", {})
    years_exp = profile.get("years_of_experience", 0) or 0

    # 1. Career History (35%) - MOST IMPORTANT (JD: career history > skills)
    career_score = career_history_score(candidate)
    career_normalized = 1.0 - math.exp(-career_score / 15)

    # 2. Role Relevance (20%) - Current title match (advice: 20%, surface AI titles in sea of non-AI)
    role_score = role_relevance_score(candidate)
    role_normalized = 1.0 - math.exp(-role_score / 5)

    # 3. Production AI Evidence (14%) - General AI/ML production experience
    prod_ai_score = production_ai_evidence_score(candidate)
    prod_ai_normalized = 1.0 - math.exp(-prod_ai_score / 10)

    # 4. Retrieval & Ranking Experience (10%) - DEDICATED component per winning strategy
    rr_score = retrieval_ranking_experience_score(candidate)
    rr_normalized = 1.0 - math.exp(-rr_score / 12)

    # 5. Behavioral Signals (10%) - Redrob signals (JD: inactive candidates = not hireable)
    redrob_score = redrob_signals_score(candidate)

    # 6. Experience Fit (5%) - Years of experience (5-9yr sweet spot)
    exp_score = experience_fit_score(years_exp)

    # 7. Skills Match (3%) - MINIMAL (EDA: skills artificially distributed)
    skills_score = skills_match_score(candidate)
    skills_normalized = 1.0 - math.exp(-skills_score / 15)

    # 8. Education (3%) - Tier + field relevance
    edu_score = education_score(candidate)

    # 9. Location fit (bonus, not main weight) - JD: Pune/Noida preferred
    loc_score = location_preference_score(candidate)
    loc_normalized = loc_score / 1.6  # Normalize to ~0-1 range

    # 10. Notice period (small bonus) - JD: sub-30 day preferred
    notice_score = notice_period_score(candidate)

    # Honeypot detection
    hon_penalty, hon_issues = detect_honeypot(candidate)

    # Composite score using strategic weights
    total = (
        career_normalized * WEIGHTS["career_relevance"] +
        role_normalized * WEIGHTS["role_relevance"] +
        prod_ai_normalized * WEIGHTS["production_ai_evidence"] +
        rr_normalized * WEIGHTS["retrieval_ranking_experience"] +
        redrob_score * WEIGHTS["behavioral_signals"] +
        exp_score * WEIGHTS["experience_fit"] +
        skills_normalized * WEIGHTS["skills_match"] +
        edu_score * WEIGHTS["education_score"] +
        loc_normalized * 0.03 +  # Location bonus (not in main weights, ~3%)
        notice_score * 0.02      # Notice period bonus (~2%)
    )

    # Apply honeypot penalty
    total *= hon_penalty

    return total, hon_penalty, hon_issues


def generate_reasoning(candidate: dict, score: float, hon_penalty: float, hon_issues: list) -> str:
    """Generate varied, specific reasoning for each candidate.
    Stage 4 judges check: not templated, not identical, not hallucinated."""
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "")
    headline = profile.get("headline", "")
    years_exp = profile.get("years_of_experience", 0) or 0
    skills = candidate.get("skills", [])
    skill_names = [s["name"] for s in skills]
    signals = candidate.get("redrob_signals", {})
    history = candidate.get("career_history", [])
    location = profile.get("location", "")
    company = profile.get("current_company", "")
    industry = profile.get("current_industry", "")

    parts = []

    # Honeypot warning
    if hon_penalty < 0.3:
        parts.append("HIGH-RISK HONEYPOT CANDIDATE")
        if hon_issues:
            parts.append(f"({'; '.join(hon_issues[:2])})")
    elif hon_penalty < 0.8:
        parts.append("SUSPICIOUS PROFILE")
        if hon_issues:
            parts.append(f"({'; '.join(hon_issues[:2])})")

    # Title (always show)
    parts.append(f"{title}")

    # Experience + company
    exp_str = f"{years_exp:.0f}yrs"
    if company:
        exp_str += f" at {company}"
    parts.append(exp_str)

    # Production AI evidence - show specific systems built
    history_desc = " ".join([(h.get("description") or "").lower() for h in history])
    prod_signals = []
    for kw in ["retrieval", "ranking", "recommendation", "search", "embeddings",
               "vector", "faiss", "pinecone", "ndcg", "mrr", "production ml",
               "evaluation", "a/b testing"]:
        if kw in history_desc:
            prod_signals.append(kw)
    if prod_signals:
        # Vary phrasing based on what signals were found
        if len(prod_signals) >= 4:
            parts.append(f"built {', '.join(prod_signals[:4])} systems")
        elif len(prod_signals) >= 2:
            parts.append(f"experience in {', '.join(prod_signals[:3])}")
        else:
            parts.append(f"worked on {prod_signals[0]}")

    # Headline bonus if unique
    hl = headline.lower()
    if hl and title.lower() not in hl:
        if any(kw in hl for kw in ["ai", "ml", "machine learning", "deep learning"]):
            parts.append("headline signals AI focus")

    # Industry/product fit
    industry_lower = industry.lower()
    if any(kw in industry_lower for kw in ["ai", "software", "technology", "internet", "saas", "product"]):
        parts.append("product co")
    elif any(kw in industry_lower for kw in ["fintech", "healthtech", "edtech"]):
        parts.append(f"{industry_lower} sector")

    # Behavioral signals
    resp_rate = signals.get("recruiter_response_rate", -1)
    if resp_rate >= 0.7:
        parts.append("very responsive")
    elif resp_rate >= 0.5:
        parts.append("responsive")

    if signals.get("open_to_work_flag", False):
        parts.append("actively looking")

    github = signals.get("github_activity_score", -1)
    if github >= 50:
        parts.append("active on GitHub")

    # Notice period
    notice = signals.get("notice_period_days", 90)
    if notice <= 15:
        parts.append("immediate join")
    elif notice <= 30:
        parts.append("short notice")
    elif notice >= 120:
        parts.append(f"{notice}d notice")

    # Location
    if location:
        loc_lower = location.lower()
        if "pune" in loc_lower or "noida" in loc_lower:
            parts.append(f"based {location} (pref location)")
        else:
            parts.append(f"based {location}")

    reasoning = "; ".join(parts)
    return reasoning


def process_candidates(candidate_generator):
    """
    Process candidates and maintain a heap of top K.
    Returns list of (score, candidate_id, reasoning, hon_penalty, hon_issues) sorted by rank.
    """
    heap = []  # Min-heap of (score, candidate_id, ...)
    honeypot_count = 0
    total_processed = 0
    start_time = time.time()

    for candidate in candidate_generator:
        total_processed += 1

        score, hon_penalty, hon_issues = compute_total_score(candidate)

        if hon_penalty < 0.5:
            honeypot_count += 1

        cid = candidate.get("candidate_id", f"CAND_{total_processed:07d}")
        reasoning = generate_reasoning(candidate, score, hon_penalty, hon_issues)

        # Push to heap (maintains top 100 by highest scores)
        if len(heap) < TOP_K:
            heapq.heappush(heap, (score, cid, reasoning, hon_penalty, hon_issues))
        else:
            if score > heap[0][0]:
                heapq.heapreplace(heap, (score, cid, reasoning, hon_penalty, hon_issues))

        # Progress indicator
        if total_processed % 10000 == 0:
            elapsed = time.time() - start_time
            rate = total_processed / elapsed if elapsed > 0 else 0
            print(f"  Processed {total_processed} candidates ({rate:.0f}/sec, {elapsed:.0f}s elapsed)", file=sys.stderr)

    elapsed = time.time() - start_time
    print(f"  Processed {total_processed} candidates in {elapsed:.1f}s ({total_processed/elapsed:.0f}/sec)", file=sys.stderr)
    print(f"  Detected {honeypot_count} potential honeypots", file=sys.stderr)

    # Sort by score (rounded to 4dp) descending, then candidate_id ascending for deterministic tie-breaking
    # Using rounded scores ensures the validator sees the same precision for tie checks
    heap_sorted = sorted(heap, key=lambda x: (-round(x[0], 4), x[1]))

    # Check honeypot ratio in top 100
    hon_in_top100 = sum(1 for h in heap_sorted if h[3] < 0.5)
    hon_ratio = hon_in_top100 / min(len(heap_sorted), TOP_K)
    print(f"  Honeypots in top 100: {hon_in_top100}/{min(len(heap_sorted), TOP_K)} ({hon_ratio*100:.1f}%)", file=sys.stderr)
    if hon_ratio > 0.10:
        print(f"  WARNING: Honeypot ratio exceeds 10% threshold!", file=sys.stderr)

    return heap_sorted


def load_jsonl_line_by_line(path: str):
    """Generator to yield parsed JSON objects from JSONL file."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_submission(rankings, output_path: str):
    """Write submission CSV file."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("candidate_id,rank,score,reasoning\n")
        for rank, (score, cid, reasoning, hon_penalty, hon_issues) in enumerate(rankings, 1):
            # Format score with 4 decimal places
            score_str = f"{score:.4f}"
            # Escape quotes in reasoning for CSV
            reasoning_escaped = reasoning.replace('"', '""')
            f.write(f"{cid},{rank},{score_str},\"{reasoning_escaped}\"\n")

    print(f"Submission written to {output_path}", file=sys.stderr)


def run_pipeline(data_file: str, output_file: str):
    """Run the full ranking pipeline."""
    print("=" * 60, file=sys.stderr)
    print("Redrob Hackathon - Candidate Ranking Pipeline", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    start = time.time()

    print(f"\nStep 1: Loading and scoring candidates from {data_file}...", file=sys.stderr)
    candidate_gen = load_jsonl_line_by_line(data_file)
    rankings = process_candidates(candidate_gen)

    elapsed = time.time() - start
    print(f"\nStep 2: Ranking complete in {elapsed:.1f}s", file=sys.stderr)

    print(f"\nStep 3: Writing submission to {output_file}...", file=sys.stderr)
    write_submission(rankings, output_file)

    print(f"\n{'=' * 60}", file=sys.stderr)
    print(f"Total time: {time.time() - start:.1f}s", file=sys.stderr)
    print(f"Top score: {rankings[0][0]:.4f}, Bottom score: {rankings[-1][0]:.4f}", file=sys.stderr)
    print(f"{'=' * 60}", file=sys.stderr)

    return rankings


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Redrob Hackathon Ranker")
    parser.add_argument("--validate", action="store_true", help="Only validate existing submission")
    parser.add_argument("--sample", action="store_true", help="Run on sample data only")
    args = parser.parse_args()

    if args.validate:
        import subprocess
        result = subprocess.run(
            ["python", os.path.join(DATA_DIR, "validate_submission.py"),
             os.path.join(OUTPUT_DIR, "submission.csv")],
            capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        sys.exit(0)

    if args.sample:
        data_file = os.path.join(DATA_DIR, "sample_candidates.json")
        output_file = os.path.join(OUTPUT_DIR, "sample_submission.csv")
        with open(data_file, "r") as f:
            samples = json.load(f)
        rankings = process_candidates(samples)
        write_submission(rankings, output_file)

        # Print top 10
        print("\n=== Top 10 Candidates (Sample) ===")
        for rank, (score, cid, reasoning, hon_penalty, hon_issues) in enumerate(rankings[:10], 1):
            honeypot_tag = " [HONEYPOT]" if hon_penalty < 0.5 else (" [SUSPICIOUS]" if hon_penalty < 0.8 else "")
            print(f"  {rank}. {cid} (score={score:.4f}){honeypot_tag}")
            print(f"     {reasoning[:120]}")
    else:
        data_file = os.path.join(DATA_DIR, "candidates.jsonl")
        output_file = os.path.join(OUTPUT_DIR, "submission.csv")
        run_pipeline(data_file, output_file)
