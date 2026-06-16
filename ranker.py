"""
Redrob Hackathon - Intelligent Candidate Discovery & Ranking System v3.0
NDCG-optimized architecture with:
  - TF-IDF semantic intent matching (replaces keyword trap)
  - Multi-stage pipeline (fast-filter → deep-analysis → final-polish)
  - Negative signal detection (aspirants, generic descriptions, fictional companies)
  - Behavioral multiplier (not additive)
  - S-curve score transformation for NDCG@10
  - Skill-career coherence scoring
  - Career progression trajectory scoring
  - 20 honeypot detection checks

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

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    TIER_A_TITLES, TIER_B_TITLES, TIER_C_TITLES,
    PRODUCTION_AI_KEYWORDS, RETRIEVAL_RANKING_KEYWORDS, GENERAL_AI_KEYWORDS,
    CONSULTING_FIRMS, FICTIONAL_COMPANIES,
    COMPANY_TIER_1, COMPANY_TIER_2, COMPANY_TIER_3,
    AI_CORE_SKILLS, AI_INFRA_SKILLS, RR_SPECIFIC_SKILLS,
    TIER_WEIGHTS, RELEVANT_FIELDS, WEIGHTS,
    PREFERRED_LOCATIONS, ASPIRANT_PHRASES, GENERIC_DESCRIPTION_FRAGMENTS,
    JD_INTENT_TEXT, JD_QUERIES,
    DIAMOND_SKILL_SET, TALENT_PLATFORM_KEYWORDS,
    CONSISTENCY_CAREER_RATIO_MIN, CONSISTENCY_CAREER_RATIO_MAX,
    CONSISTENCY_MAX_SKILL_INCONSISTENCY_RATIO,
    FAST_FILTER_TOP_K, FINAL_TOP_K,
    TFIDF_MAX_FEATURES, TFIDF_NGRAM_RANGE, TFIDF_MAX_DF, TFIDF_MIN_DF, TFIDF_SAMPLE_SIZE,
    SCURVE_STEEPNESS, SCURVE_MIDPOINT,
    BEHAVIORAL_MULTIPLIER_MIN, BEHAVIORAL_MULTIPLIER_MAX,
)

DATA_DIR = "data"
OUTPUT_DIR = "output"


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 0: SEMANTIC MATCHER
# ═══════════════════════════════════════════════════════════════════════════════

class SemanticMatcher:
    """Optimized TF-IDF based semantic intent matcher.
    
    - Fits on a SAMPLE of the corpus (IDF stabilizes fast)
    - Precomputes ALL candidate vectors in BULK (one transform call)
    - Returns similarity from precomputed vectors (O(1) lookup)
    
    Replaces keyword counting with learned term importance (IDF).
    JD = query vector, candidate text = document vectors.
    Cosine similarity = semantic intent match score.
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            stop_words='english',
            ngram_range=TFIDF_NGRAM_RANGE,
            max_df=TFIDF_MAX_DF,
            min_df=TFIDF_MIN_DF,
            sublinear_tf=True,        # Log-scale TF: reduces keyword-stuffer advantage
            norm='l2',
        )
        self.jd_vectors = None       # Shape: (n_queries, n_features)
        self._all_similarities = None  # Shape: (n_queries, n_candidates) — precomputed
        self._is_fitted = False
    
    def fit(self, corpus_texts):
        """Build vocabulary from candidate corpus, compute all JD query vectors.
        
        Fits on all corpus_texts (typically first 20K sample).
        Uses all JD_QUERIES (5 facets) for multi-query expansion.
        """
        self.vectorizer.fit(corpus_texts)
        self.jd_vectors = self.vectorizer.transform(JD_QUERIES)
        self._is_fitted = True
    
    def precompute_all_vectors(self, all_texts):
        """Precompute ALL similarities across ALL JD queries in ONE vectorized call.
        
        - One bulk transform() call for all 100K docs
        - One cosine_similarity() call with shape (n_queries, n_candidates)
        - get_similarity(idx) takes max across all queries (O(1) — array index + max)
        """
        if not self._is_fitted:
            raise RuntimeError("SemanticMatcher not fitted — call .fit() first")
        all_vectors = self.vectorizer.transform(all_texts)
        # Shape: (n_queries, n_candidates) — each row is a JD query's sim with all candidates
        self._all_similarities = cosine_similarity(self.jd_vectors, all_vectors)
    
    def get_similarity(self, idx):
        """Return max cosine similarity across all JD queries for candidate at index.
        
        O(1) — array index into precomputed (n_queries, n_candidates) matrix.
        Takes max across queries to capture the best semantic facet match.
        """
        if self._all_similarities is None:
            raise RuntimeError("Similarities not precomputed — call precompute_all_vectors() first")
        return float(np.max(self._all_similarities[:, idx]))
    
    def similarity(self, candidate_text):
        """Return max cosine similarity across all JD queries for a single candidate.
        
        Single-candidate version — kept for backward compat with process_candidates().
        """
        if not self._is_fitted:
            raise RuntimeError("SemanticMatcher not fitted — call .fit() first")
        cv = self.vectorizer.transform([candidate_text])
        sims = cosine_similarity(self.jd_vectors, cv)
        return float(np.max(sims))
    
    def top_terms(self, n=20):
        """Debug: show highest-weighted terms across all JD vectors."""
        if not self._is_fitted:
            return []
        # Aggregate TF-IDF weights from all queries (sum across queries)
        aggregated = np.asarray(self.jd_vectors.sum(axis=0)).flatten()
        indices = np.argsort(aggregated)[::-1][:n]
        return [(self.vectorizer.get_feature_names_out()[i], aggregated[i]) for i in indices if aggregated[i] > 0]


def build_candidate_text(candidate):
    """Build unified text for TF-IDF matching from all candidate fields.
    
    Features recency-dominated TF-IDF: current/recent role text is repeated
    3x to boost its TF weight in the TF-IDF model. This gives higher semantic
    importance to what the candidate is doing NOW vs. 5+ years ago.
    """
    profile = candidate.get("profile", {})
    parts = []
    
    # Summary (full weight)
    summary = profile.get("summary", "") or ""
    parts.append(summary)
    
    # Headline
    headline = profile.get("headline", "") or ""
    parts.append(headline)
    
    # Career descriptions (truncated to 250 chars each to speed up TF-IDF transform)
    current_role_text = None
    for job in candidate.get("career_history", []):
        desc = (job.get("description", "") or "")[:250]
        title = job.get("title", "") or ""
        industry = job.get("industry", "") or ""
        job_text = f"{title} {desc} {industry}"
        parts.append(job_text)
        
        # Save current role text for recency boosting
        if job.get("is_current", False):
            current_role_text = job_text
    
    # Recency boost: repeat current role text 3x for higher TF weight
    if current_role_text:
        parts.append(current_role_text)  # 2nd occurrence
        parts.append(current_role_text)  # 3rd occurrence
    elif len(candidate.get("career_history", [])) > 0:
        # No current role — repeat the most recent role
        most_recent = candidate["career_history"][0]
        desc = (most_recent.get("description", "") or "")[:250]
        title = most_recent.get("title", "") or ""
        industry = most_recent.get("industry", "") or ""
        recent_text = f"{title} {desc} {industry}"
        parts.append(recent_text)
        parts.append(recent_text)
    
    # Current title
    curr_title = profile.get("current_title", "") or ""
    parts.append(curr_title)
    
    return " ".join(parts)


# ═══════════════════════════════════════════════════════════════════════════════
# CORE TITLE CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

def _title_tier(title):
    """Classify a job title into Tier A (2), Tier B (1), or Tier C (-1)."""
    tl = title.lower()
    if any(kw in tl for kw in TIER_A_TITLES):
        return 2
    elif any(kw in tl for kw in TIER_B_TITLES):
        return 1
    elif any(kw in tl for kw in TIER_C_TITLES):
        return -1
    return 0


# ═══════════════════════════════════════════════════════════════════════════════
# SIGNAL SCORING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _title_tier_score(title):
    """Numeric score from title tier classification."""
    tier = _title_tier(title)
    if tier == 2:
        return 3.0
    elif tier == 1:
        return 1.0
    elif tier == -1:
        return -1.0
    return 0.0


def production_ai_evidence_score(candidate):
    """Score evidence of building production AI/ranking/search/recommendation systems."""
    history = candidate.get("career_history", [])
    profile = candidate.get("profile", {})
    score = 0.0
    
    for job in history:
        desc = (job.get("description") or "").lower()
        title = (job.get("title") or "").lower()
        match_count = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in desc and kw not in RETRIEVAL_RANKING_KEYWORDS)
        score += match_count * 0.4
        if _title_tier(title) == 2 and match_count > 0:
            score += 0.8
    
    summary = (profile.get("summary") or "").lower()
    summary_matches = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in summary and kw not in RETRIEVAL_RANKING_KEYWORDS)
    score += summary_matches * 0.2
    
    skills = candidate.get("skills", [])
    skill_names = set(s["name"] for s in skills)
    prod_skills = {"PyTorch", "TensorFlow", "Transformers", "MLflow",
                    "Weights & Biases", "WandB", "Docker", "Kubernetes",
                    "AWS", "GCP", "Azure", "Airflow", "Spark",
                    "Fine-tuning LLMs", "LLM", "RAG", "LoRA", "PEFT",
                    "XGBoost", "scikit-learn"}
    prod_skill_count = len(skill_names & prod_skills)
    score += prod_skill_count * 0.3
    
    return score


def retrieval_ranking_experience_score(candidate):
    """Dedicated scoring for retrieval, ranking, search, and recommendation systems."""
    history = candidate.get("career_history", [])
    profile = candidate.get("profile", {})
    score = 0.0
    
    for job in history:
        desc = (job.get("description") or "").lower()
        title = (job.get("title") or "").lower()
        industry = (job.get("industry") or "").lower()
        is_current = job.get("is_current", False)
        duration = job.get("duration_months", 0) or 0
        
        match_count = sum(1 for kw in RETRIEVAL_RANKING_KEYWORDS if kw in desc)
        recency_mult = 2.0 if is_current else max(1.0, duration / 12)
        job_score = match_count * 0.8 * recency_mult
        
        title_lower = title.lower()
        if any(kw in title_lower for kw in ["search", "recommendation", "relevance", "retrieval", "ranking"]):
            job_score += 2.0 * recency_mult
        
        if "recruit" in industry or "talent" in industry or "hr" in industry or "hiring" in industry:
            job_score += 1.0
        
        score += job_score
    
    summary = (profile.get("summary") or "").lower()
    summary_matches = sum(1 for kw in RETRIEVAL_RANKING_KEYWORDS if kw in summary)
    score += summary_matches * 0.5
    
    skills = candidate.get("skills", [])
    skill_names = set(s["name"] for s in skills)
    rr_skill_count = len(skill_names & RR_SPECIFIC_SKILLS)
    score += rr_skill_count * 0.8
    
    return score


def location_preference_score(candidate):
    """Score location match against JD preferences."""
    profile = candidate.get("profile", {})
    location = (profile.get("location") or "").lower()
    country = (profile.get("country") or "").lower()
    signals = candidate.get("redrob_signals", {})
    willing_relocate = signals.get("willing_to_relocate", False)
    
    if country != "india":
        return 0.15
    
    if any(city in location for city in PREFERRED_LOCATIONS):
        score = 1.0
    elif any(city in location for city in ["delhi", "gurgaon", "gurugram"]):
        score = 0.8
    elif any(city in location for city in ["mumbai", "hyderabad", "bangalore", "bengaluru", "chennai"]):
        score = 0.6
    else:
        score = 0.3
    
    if willing_relocate:
        score += 0.3
    
    return score


def notice_period_score(candidate):
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


def career_history_score(candidate):
    """Score career history for AI/ML engineering relevance."""
    history = candidate.get("career_history", [])
    if not history:
        return 0.0
    
    total_score = 0.0
    consulting_only = True
    
    for job in history:
        title = (job.get("title") or "")
        desc = (job.get("description") or "").lower()
        company = (job.get("company") or "").lower()
        industry = (job.get("industry") or "").lower()
        company_size = (job.get("company_size") or "")
        is_current = job.get("is_current", False)
        duration = job.get("duration_months", 0) or 0
        
        recency_weight = 2.5 if is_current else max(1.0, duration / 12)
        job_score = 0.0
        
        tier = _title_tier(title)
        if tier == 2:
            job_score += 4.0
        elif tier == 1:
            job_score += 2.0
        elif tier == -1:
            job_score -= 1.0
        
        prod_matches = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in desc)
        job_score += prod_matches * 0.5
        
        gen_ai_matches = sum(1 for kw in GENERAL_AI_KEYWORDS if kw in desc)
        job_score += gen_ai_matches * 0.2
        
        is_product_co = any(kw in industry for kw in ["ai", "software", "fintech", "technology", "internet", "saas", "product"])
        if is_product_co:
            job_score += 0.5
        
        is_startup = any(sz in company_size for sz in ["1-10", "11-50", "51-200", "201-500"])
        if is_startup and is_product_co:
            job_score += 0.5
        
        if company not in CONSULTING_FIRMS:
            consulting_only = False
        
        total_score += job_score * recency_weight
    
    if consulting_only and len(history) >= 1:
        total_score *= 0.5
    
    return max(total_score, 0.0)


def role_relevance_score(candidate):
    """Score current role for direct relevance to Senior AI Engineer."""
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "") or ""
    headline = profile.get("headline", "") or ""
    score = _title_tier_score(title)
    
    hl = headline.lower()
    prod_matches = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in hl)
    score += prod_matches * 0.5
    gen_ai_matches = sum(1 for kw in GENERAL_AI_KEYWORDS if kw in hl)
    score += gen_ai_matches * 0.2
    
    return max(score, 0.0)


def skills_match_score(candidate):
    """Minimal skills scoring — EDA confirms skills artificially distributed."""
    skills = candidate.get("skills", [])
    if not skills:
        return 0.0
    score = 0.0
    skill_names = set(s["name"] for s in skills)
    
    for s in skills:
        name = s["name"]
        prof = s.get("proficiency", "beginner")
        endorsements = s.get("endorsements", 0)
        prof_mult = {"beginner": 0.5, "intermediate": 1.0, "advanced": 1.5, "expert": 2.0}.get(prof, 1.0)
        end_mult = 1 + min(endorsements, 30) / 100
        
        if name in RR_SPECIFIC_SKILLS:
            score += 2.0 * prof_mult * end_mult
        elif name in AI_CORE_SKILLS:
            score += 0.8 * prof_mult * end_mult
        elif name in AI_INFRA_SKILLS:
            score += 0.5 * prof_mult * end_mult
    
    return score


def experience_fit_score(years):
    """Score years of experience. Peak at 5-9 years, ideal at 7."""
    if years <= 0:
        return 0.0
    if years < 2:
        return 0.1
    elif years < 4:
        return 0.3 + 0.2 * (years - 2) / 2
    elif years <= 9:
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


def education_score(candidate):
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
        
        field_score = 0.0
        if any(rf in field for rf in RELEVANT_FIELDS):
            field_score = 2.0
            has_relevant_field = True
        
        degree_score = 0.0
        if any(d in degree for d in ["ph.d", "phd", "doctorate"]):
            degree_score = 2.0
        elif any(d in degree for d in ["m.tech", "m.e.", "m.sc", "master", "ms"]):
            degree_score = 1.5
        elif any(d in degree for d in ["b.tech", "b.e.", "b.sc", "bachelor"]):
            degree_score = 1.0
        
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
    
    if edus:
        score = score / len(edus)
    if has_relevant_field and max_tier_score >= 2.0:
        score *= 1.2
    
    return min(score, 5.0)


# ═══════════════════════════════════════════════════════════════════════════════
# NEW SIGNALS: NEGATIVE DETECTION, COHERENCE, PROGRESSION
# ═══════════════════════════════════════════════════════════════════════════════

def negative_signal_penalty(candidate):
    """Detect and penalize negative signals: aspirants, generic descriptions, fictional companies.
    
    Returns a penalty score (0 = no penalty, higher = more penalized).
    This is used as a negative weight in the final score.
    """
    history = candidate.get("career_history", [])
    profile = candidate.get("profile", {})
    summary = (profile.get("summary") or "").lower()
    penalty = 0.0
    
    # Signal 1: Aspirant language in summary
    aspirant_count = sum(1 for phrase in ASPIRANT_PHRASES if phrase in summary)
    penalty += aspirant_count * 0.15
    
    # Signal 2: Aspirant language in career descriptions
    for job in history:
        desc = (job.get("description") or "").lower()
        aspirant_count_desc = sum(1 for phrase in ASPIRANT_PHRASES if phrase in desc)
        penalty += aspirant_count_desc * 0.10
    
    # Signal 3: Generic/filler descriptions
    for job in history:
        desc = (job.get("description") or "").lower()
        generic_count = sum(1 for frag in GENERIC_DESCRIPTION_FRAGMENTS if frag in desc)
        if generic_count >= 3:
            penalty += 0.20  # Multiple generic fragments = likely copied
    
    # Signal 4: Description reused across different roles
    # Apply at most one reuse penalty to prevent cascading over-penalization
    descriptions = [h.get("description", "") or "" for h in history]
    found_reuse = False
    if len(descriptions) >= 2:
        for i in range(len(descriptions)):
            if found_reuse:
                break
            for j in range(i + 1, len(descriptions)):
                d1, d2 = descriptions[i].lower(), descriptions[j].lower()
                if len(d1) > 50 and len(d2) > 50:
                    # Check if they share long substrings (copied descriptions)
                    overlap = len(set(d1.split()) & set(d2.split()))
                    total = len(set(d1.split()) | set(d2.split()))
                    if total > 0 and overlap / total > 0.7:
                        penalty += 0.30
                        found_reuse = True
                        break
    
    # Signal 5: Fictional company
    fictional_count = 0
    for job in history:
        company = (job.get("company") or "").lower().strip()
        if company in FICTIONAL_COMPANIES:
            fictional_count += 1
    if fictional_count >= 2:
        penalty += 0.25 * min(fictional_count, 5) / 5
    elif fictional_count == 1:
        penalty += 0.08
    
    # Signal 6: Company quality (penalize consulting-only)
    all_consulting = True
    for job in history:
        company = (job.get("company") or "").lower().strip()
        if company not in CONSULTING_FIRMS and company not in FICTIONAL_COMPANIES:
            all_consulting = False
            break
    if all_consulting and len(history) >= 2:
        penalty += 0.15
    
    # Signal 7: Keyword density too high (keyword stuffers)
    total_text = " ".join([(h.get("description") or "").lower() for h in history] + [summary])
    ai_keywords_in_text = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in total_text)
    total_chars = max(len(total_text), 1)
    density = ai_keywords_in_text / total_chars * 1000  # Per 1000 chars
    if density > 10.0:  # >10 AI keyword mentions per 1000 chars
        penalty += 0.20 * min((density - 10.0) / 5.0, 1.0)
    
    return min(penalty, 1.0)


def skill_career_coherence_score(candidate):
    """Cross-reference skills against career descriptions.
    
    High coherence = skills are evidenced in work history = genuine.
    Low coherence = skills are listed but never used = keyword stuffing.
    """
    skills = candidate.get("skills", [])
    history = candidate.get("career_history", [])
    
    if not skills:
        return 0.0
    
    # Build text corpus from all career descriptions
    career_text = " ".join([
        (h.get("description") or "").lower()
        for h in history
    ])
    summary = (candidate.get("profile", {}).get("summary") or "").lower()
    all_text = career_text + " " + summary
    
    # For each skill, check if it's mentioned in career history
    matched = 0
    total = 0
    for s in skills:
        name = s["name"].lower()
        prof = s.get("proficiency", "beginner")
        
        # Only check substantive skills (skip obvious ones like "Excel", "PowerPoint")
        if name in {"excel", "powerpoint", "photoshop", "seo", "content writing", "sales", "accounting"}:
            continue
        
        total += 1
        
        # Check exact match first
        if name in all_text:
            matched += 1
            continue
        
        # Check alias-based match
        aliases = {
            "nlp": ["natural language processing", "text classification", "sentiment"],
            "computer vision": ["object detection", "image classification", "yolo", "opencv"],
            "pytorch": ["torch", "deep learning"],
            "tensorflow": ["tf", "keras", "deep learning"],
            "llm": ["large language model", "gpt", "bert", "transformer"],
            "faiss": ["vector search", "similarity search", "ann"],
            "pinecone": ["vector database", "vector search"],
            "docker": ["container", "containerization"],
            "kubernetes": ["k8s", "container orchestration"],
            "airflow": ["orchestration", "pipeline"],
            "spark": ["pyspark", "spark streaming"],
        }
        found = False
        if name in aliases:
            found = any(a in all_text for a in aliases[name])
        if found:
            matched += 1
    
    if total == 0:
        return 0.0
    
    coherence = matched / total
    
    # Bonus: if RR-specific skills are all matched, extra signal
    rr_skill_names = set(s["name"] for s in skills if s["name"] in RR_SPECIFIC_SKILLS)
    if rr_skill_names:
        rr_matched = sum(1 for rn in rr_skill_names if rn.lower() in all_text)
        rr_ratio = rr_matched / len(rr_skill_names)
        coherence = coherence * 0.7 + rr_ratio * 0.3
    
    return coherence


def career_progression_score(candidate):
    """Score career trajectory: progression toward AI/ML roles over time.
    
    Positive: Moving from general SWE → ML → Senior ML at product companies.
    Negative: Moving from non-tech → AI (suspicious jump).
    Neutral: Staying in same domain.
    """
    history = candidate.get("career_history", [])
    if len(history) < 2:
        return 0.5  # Neutral for single-role candidates
    
    progression = 0.0
    transitions = 0
    
    for i in range(len(history) - 1):
        current = history[i]
        next_role = history[i + 1]
        
        curr_title = (current.get("title") or "").lower()
        next_title = (next_role.get("title") or "").lower()
        curr_industry = (current.get("industry") or "").lower()
        next_industry = (next_role.get("industry") or "").lower()
        
        curr_tier = _title_tier(curr_title)
        next_tier = _title_tier(next_title)
        
        # Positive: tier increase
        if next_tier > curr_tier:
            progression += 1.0
        elif next_tier < curr_tier:
            progression -= 0.5
        else:
            progression += 0.0
        
        # Positive: moving from IT Services to Product/AI
        if ("services" in curr_industry or "consulting" in curr_industry) and \
           any(kw in next_industry for kw in ["ai", "software", "technology", "internet", "fintech"]):
            progression += 1.5
        
        # Strongly positive: moving from non-AI title to AI title
        is_ai_title = any(kw in next_title for kw in ["ai", "ml", "machine learning", "deep learning",
                                                       "nlp", "recommendation", "search", "data scientist"])
        was_not_ai = not any(kw in curr_title for kw in ["ai", "ml", "machine learning", "deep learning",
                                                         "nlp", "recommendation", "search", "data scientist"])
        if is_ai_title and was_not_ai:
            progression += 2.0  # Intentional career move toward AI
        
        # Positive: staying within AI/ML titles
        if curr_tier >= 1 and next_tier >= 1:
            progression += 0.5
        
        transitions += 1
    
    if transitions == 0:
        return 0.5
    
    avg_progression = progression / transitions
    # Normalize to 0-1 range (most scores will be between -1 and 3)
    normalized = max(0.0, min(1.0, (avg_progression + 1.0) / 4.0))
    return normalized


def company_quality_score(candidate):
    """Score company quality based on tier classification."""
    history = candidate.get("career_history", [])
    if not history:
        return 0.0
    
    score = 0.0
    count = 0
    
    for job in history:
        company = (job.get("company") or "").lower().strip()
        is_current = job.get("is_current", False)
        
        if company in COMPANY_TIER_1:
            s = 3.0
        elif company in COMPANY_TIER_2:
            s = 2.0
        elif company in COMPANY_TIER_3:
            s = 1.5
        elif company in CONSULTING_FIRMS:
            s = 0.0  # Neutral, consulting penalty handled elsewhere
        elif company in FICTIONAL_COMPANIES:
            s = -0.5  # Slight penalty
        else:
            s = 0.5  # Unknown company
        
        if is_current:
            s *= 1.5  # Current company matters more
        
        score += s
        count += 1
    
    if count == 0:
        return 0.0
    
    avg = score / count
    # Normalize to 0-1 range
    return max(0.0, min(1.0, (avg + 0.5) / 3.5))


# ═══════════════════════════════════════════════════════════════════════════════
# NEW WINNING FEATURES: Diamond Bonus, Talent Bonus, Consistency Score
# ═══════════════════════════════════════════════════════════════════════════════

def rare_skill_diamond_score(candidate):
    """Score for candidates with the rare 'diamond' skill combination.
    
    The JD specifically asks for retrieval + ranking + embeddings + search + LLM.
    Candidates who have ALL of these skills are extremely rare and valuable.
    This gives a significant bonus to genuine unicorn profiles.
    
    Returns: 0.0 to 1.0 (higher = rarer and more valuable combo)
    """
    skills = candidate.get("skills", [])
    if not skills:
        return 0.0
    
    skill_names = set(s["name"] for s in skills)
    diamond_skills = skill_names & DIAMOND_SKILL_SET
    count = len(diamond_skills)
    
    if count == 0:
        return 0.0
    
    # Check career history for evidence of diamond skills in practice
    history = candidate.get("career_history", [])
    all_desc = " ".join([
        (h.get("description") or "").lower()
        for h in history
    ])
    
    # Bonus for diamond skills evidenced in career (not just listed)
    evidenced = sum(1 for s in diamond_skills if s.lower() in all_desc)
    evidence_ratio = evidenced / max(len(diamond_skills), 1)
    
    # Score: combination of skill count and evidence
    # Full diamond (6+ skills) = 1.0, Partial (3-5) = 0.5-0.8, Few (1-2) = 0.2-0.4
    if count >= 6:
        base = 1.0
    elif count >= 4:
        base = 0.7 + 0.1 * (count - 4)  # 0.7, 0.8
    elif count >= 2:
        base = 0.3 + 0.1 * (count - 2)  # 0.3, 0.4
    else:
        base = 0.2
    
    # Adjust for evidence - full evidence keeps score, partial reduces
    score = base * (0.5 + 0.5 * evidence_ratio)
    
    return min(score, 1.0)


def talent_platform_bonus(candidate):
    """Bonus for candidates with HR tech / recruiting / talent platform domain expertise.
    
    Redrob AI is a talent platform — candidates who understand the recruiting domain
    will ramp faster and bring valuable domain insight. This is a subtle edge
    over generic ML engineers.
    """
    history = candidate.get("career_history", [])
    profile = candidate.get("profile", {})
    max_score = 0.0
    
    # Check career descriptions and industries
    for job in history:
        text = ((job.get("description") or "") + " " + (job.get("industry") or "")).lower()
        company = (job.get("company") or "").lower()
        title = (job.get("title") or "").lower()
        
        matches = sum(1 for kw in TALENT_PLATFORM_KEYWORDS if kw in text)
        
        job_score = 0.0
        if matches >= 4:
            job_score = 1.0  # Deep HR tech expertise
        elif matches >= 2:
            job_score = 0.6  # Significant domain exposure
        elif matches >= 1:
            job_score = 0.3  # Some domain exposure
        
        # Bonus for explicitly being in HR tech company
        company_matches = sum(1 for kw in TALENT_PLATFORM_KEYWORDS[:6] if kw in company)
        if company_matches > 0:
            job_score = max(job_score, 0.8)
        
        # Bonus for having HR/talent in the actual title
        if any(kw in title for kw in ["recruit", "talent", "hr", "people"]):
            job_score = max(job_score, 0.7)
        
        max_score = max(max_score, job_score)
    
    # Check summary
    summary = (profile.get("summary") or "").lower()
    summary_matches = sum(1 for kw in TALENT_PLATFORM_KEYWORDS if kw in summary)
    if summary_matches >= 2:
        max_score = max(max_score, 0.7)
    elif summary_matches >= 1:
        max_score = max(max_score, 0.4)
    
    return max_score


def profile_consistency_score(candidate):
    """Score how internally consistent the candidate's profile is.
    
    High consistency = genuine candidate with authentic data.
    Low consistency = fabricated or inflated profile.
    
    Returns: 0.0 to 1.0 (higher = more consistent)
    Used as a multiplier on the final score, not additive.
    """
    profile = candidate.get("profile", {})
    history = candidate.get("career_history", [])
    skills = candidate.get("skills", [])
    edus = candidate.get("education", [])
    
    score = 1.0  # Start perfect, deduct for inconsistencies
    
    # --- Check 1: Career history duration vs stated experience ---
    stated_years = profile.get("years_of_experience", 0) or 0
    if history and len(history) >= 1 and stated_years > 0:
        total_career_months = sum(h.get("duration_months", 0) or 0 for h in history)
        total_career_years = total_career_months / 12
        stated_years = profile.get("years_of_experience", 0) or 0
        
        if total_career_years > 0 and stated_years > 0:
            ratio = total_career_years / stated_years
            if ratio < CONSISTENCY_CAREER_RATIO_MIN:
                # Career history covers much less than stated experience
                score -= 0.15 * (1.0 - ratio / CONSISTENCY_CAREER_RATIO_MIN)
            elif ratio > CONSISTENCY_CAREER_RATIO_MAX:
                # Career history covers much more than stated experience
                score -= 0.20 * min((ratio - CONSISTENCY_CAREER_RATIO_MAX) / CONSISTENCY_CAREER_RATIO_MAX, 1.0)
    
    # --- Check 2: Skill proficiency vs duration ---
    if skills:
        anomalies = 0
        for s in skills:
            prof = s.get("proficiency", "beginner")
            duration = s.get("duration_months", 0) or 0
            # Expert-level skill with < 6 months experience = suspicious
            if prof == "expert" and duration < 6:
                anomalies += 1
            # Beginner-level skill with > 48 months = suspicious
            elif prof == "beginner" and duration > 48:
                anomalies += 1
        
        anomaly_ratio = anomalies / max(len(skills), 1)
        if anomaly_ratio > CONSISTENCY_MAX_SKILL_INCONSISTENCY_RATIO:
            penalty = min((anomaly_ratio - CONSISTENCY_MAX_SKILL_INCONSISTENCY_RATIO) * 0.5, 0.15)
            score -= penalty
    
    # --- Check 3: Education timeline progression ---
    if len(edus) >= 2:
        # Sort by start year
        sorted_edus = sorted(edus, key=lambda e: e.get("start_year", 0) or 0)
        gaps_ok = True
        for i in range(len(sorted_edus) - 1):
            curr_end = sorted_edus[i].get("end_year", 0) or 0
            next_start = sorted_edus[i + 1].get("start_year", 0) or 0
            if curr_end > 0 and next_start > 0:
                # Gap should be reasonable (0-3 years, or overlapping is suspicious)
                gap = next_start - curr_end
                # If next degree starts before current ends, or gap > 4 years
                if gap < -1 or gap > 4:
                    gaps_ok = False
                    break
        if not gaps_ok:
            score -= 0.10
    
    # --- Check 4: Career start date vs education end date ---
    if history and edus:
        earliest_work = 2026
        for h in history:
            sd = h.get("start_date", "")
            if sd and len(sd) >= 4:
                try:
                    earliest_work = min(earliest_work, int(sd[:4]))
                except ValueError:
                    pass
        
        latest_edu_end = 0
        for e in edus:
            ey = e.get("end_year", 0) or 0
            if ey > 0:
                latest_edu_end = max(latest_edu_end, ey)
        
        if earliest_work < 2026 and latest_edu_end > 0:
            # Working during school is fine (internships), but not 3+ years before
            if earliest_work < latest_edu_end - 3:
                score -= 0.10
    
    return max(0.5, min(1.0, score))


def behavioral_multiplier(candidate):
    """Compute behavioral signal multiplier (NOT additive).
    
    Range: BEHAVIORAL_MULTIPLIER_MIN to BEHAVIORAL_MULTIPLIER_MAX.
    Multiplies the base score instead of adding to it.
    This prevents well-behaved non-engineers from ranking above actual AI engineers.
    """
    signals = candidate.get("redrob_signals", {})
    if not signals:
        return 1.0
    
    raw = 0.0
    
    # Profile completeness (0-100 -> 0-0.10)
    completeness = signals.get("profile_completeness_score", 0)
    raw += (completeness / 100) * 0.10
    
    # Recruiter response rate (0-1 -> 0-0.20)
    resp_rate = signals.get("recruiter_response_rate", 0)
    if resp_rate >= 0:
        raw += resp_rate * 0.20
    
    # Interview completion rate (0-1 -> 0-0.15)
    interview_rate = signals.get("interview_completion_rate", 0)
    if interview_rate >= 0:
        raw += interview_rate * 0.15
    
    # Search appearance
    search_app = signals.get("search_appearance_30d", 0)
    raw += min(search_app / 200, 1.0) * 0.10
    
    # Saved by recruiters
    saved = signals.get("saved_by_recruiters_30d", 0)
    raw += min(saved / 20, 1.0) * 0.15
    
    # GitHub activity
    github = signals.get("github_activity_score", -1)
    if github >= 0:
        raw += (github / 100) * 0.10
    
    # Connections
    connections = signals.get("connection_count", 0)
    raw += min(connections / 500, 1.0) * 0.05
    
    # Endorsements
    endorsements = signals.get("endorsements_received", 0)
    raw += min(endorsements / 50, 1.0) * 0.05
    
    # Basic signals
    if signals.get("open_to_work_flag", False):
        raw += 0.05
    if signals.get("verified_email", False):
        raw += 0.03
    if signals.get("verified_phone", False):
        raw += 0.02
    if signals.get("willing_to_relocate", False):
        raw += 0.05
    
    # Notice period signal
    notice = signals.get("notice_period_days", 90)
    if notice <= 30:
        raw += 0.05
    elif notice <= 60:
        raw += 0.03
    elif notice >= 120:
        raw -= 0.02
    
    # Normalize to multiplier range: [MIN, MAX]
    # raw is roughly in [0, 1.05], map to [0.80, 1.15]
    multiplier = BEHAVIORAL_MULTIPLIER_MIN + raw * (BEHAVIORAL_MULTIPLIER_MAX - BEHAVIORAL_MULTIPLIER_MIN)
    
    # Clamp
    multiplier = max(BEHAVIORAL_MULTIPLIER_MIN, min(BEHAVIORAL_MULTIPLIER_MAX, multiplier))
    
    return multiplier


# ═══════════════════════════════════════════════════════════════════════════════
# HONEYPOT DETECTION (20 Checks)
# ═══════════════════════════════════════════════════════════════════════════════

def detect_honeypot_fast(candidate):
    """Fast honeypot check for Phase 1 (quick elimination).
    Returns tuple (penalty_multiplier, issues_list).
    Only runs the cheapest checks.
    """
    penalty = 1.0
    issues = []
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    history = candidate.get("career_history", [])
    years_exp = profile.get("years_of_experience", 0)
    
    # Check 1: Timeline inconsistency (quick)
    edus = candidate.get("education", [])
    if edus:
        latest_edu_end = max(e.get("end_year", 0) or 0 for e in edus)
        years_since_grad = 2026 - latest_edu_end
        if latest_edu_end > 0 and years_exp > years_since_grad + 5 and years_since_grad >= 0:
            severity = (years_exp - years_since_grad - 5) / 10
            penalty *= max(0.0, 1.0 - severity)
            issues.append(f"timeline: {years_exp}yrs exp but graduated {latest_edu_end}")
    
    # Check 2: No career history (very fast)
    if not history:
        penalty *= 0.1
        issues.append("no career history")
    
    # Check 3: Fictional company concentration (fast)
    if history:
        total_jobs = len(history)
        fictional_jobs = sum(
            1 for h in history
            if (h.get("company") or "").lower().strip() in FICTIONAL_COMPANIES
        )
        if total_jobs > 0 and fictional_jobs / total_jobs > 0.5:
            penalty *= 0.4
            issues.append(f"{fictional_jobs}/{total_jobs} jobs at fictional companies")
    
    return penalty, issues


def detect_honeypot_deep(candidate):
    """Full 20-check honeypot detection for Phase 2 (deep analysis).
    Returns tuple (penalty_multiplier, issues_list).
    """
    penalty, issues = detect_honeypot_fast(candidate)
    if penalty < 0.1:
        return penalty, issues  # Already eliminated
    
    profile = candidate.get("profile", {})
    edus = candidate.get("education", [])
    skills = candidate.get("skills", [])
    history = candidate.get("career_history", [])
    signals = candidate.get("redrob_signals", {})
    years_exp = profile.get("years_of_experience", 0)
    summary = (profile.get("summary") or "").lower()
    skill_names = set(s["name"] for s in skills)
    
    # Check 4: Overlapping education at different institutions
    if len(edus) >= 2:
        for i in range(len(edus)):
            for j in range(i + 1, len(edus)):
                e1, e2 = edus[i], edus[j]
                if e1.get("institution") != e2.get("institution"):
                    s1, e1e = e1.get("start_year", 0) or 0, e1.get("end_year", 0) or 0
                    s2, e2e = e2.get("start_year", 0) or 0, e2.get("end_year", 0) or 0
                    if s1 and s2 and e1e and e2e and not (e1e <= s2 or e2e <= s1):
                        penalty *= 0.35
                        issues.append(f"overlapping education: {e1.get('degree', '')}@{e1.get('institution', '')} & {e2.get('degree', '')}@{e2.get('institution', '')}")
                        break
    
    # Check 5: AI skills but no AI background
    ai_skill_overlap = len(skill_names & AI_CORE_SKILLS)
    if ai_skill_overlap >= 2:
        has_ai_edu = any(
            any(kw in (e.get("field_of_study", "") or "").lower()
                for kw in ["intelligence", "learning", "data science", "computer science", "data engineering"])
            for e in edus
        )
        has_ai_role = any(
            any(kw in (h.get("title", "") or "").lower()
                for kw in ["ai", "ml", "machine learning", "data scientist", "nlp", "recommendation", "search"])
            for h in history
        )
        if not has_ai_edu and not has_ai_role and ai_skill_overlap >= 3:
            severity = min(1.0, ai_skill_overlap / 10)
            penalty *= (1.0 - severity * 0.5)
            issues.append(f"suspicious: {ai_skill_overlap} AI skills but no AI edu/role")
    
    # Check 6: Skill endorsements vs skill count mismatch
    high_endorsements = any(s.get("endorsements", 0) >= 50 for s in skills)
    low_skill_count = len(skills) <= 3
    if high_endorsements and low_skill_count:
        penalty *= 0.7
        issues.append(f"high endorsements but only {len(skills)} skills")
    
    # Check 7: Career history exceeds stated experience
    if len(history) >= 2:
        total_career_months = sum(h.get("duration_months", 0) or 0 for h in history)
        total_career_years = total_career_months / 12
        if total_career_years > years_exp + 3 and years_exp > 0:
            penalty *= 0.5
            issues.append(f"career history ({total_career_years:.0f}yrs) exceeds stated exp ({years_exp}yrs)")
    
    # Check 8: Missing or very short career descriptions
    all_empty = all(not (h.get("description") or "").strip() for h in history) if history else True
    if history and all_empty:
        penalty *= 0.4
        issues.append("all career descriptions are empty")
    elif history:
        min_desc_len = min(len(h.get("description") or "") for h in history)
        if min_desc_len < 30:
            penalty *= 0.6
            issues.append(f"career description too short ({min_desc_len} chars)")
    
    # Check 9: Job-hopping (5+ jobs, compressed timeline)
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
    
    # Check 10: Summary has production AI keywords but zero career history matches
    if summary:
        prod_in_summary = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in summary)
        if prod_in_summary >= 8:
            hist_desc = " ".join([(h.get("description") or "").lower() for h in history])
            prod_in_hist = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in hist_desc)
            if prod_in_hist == 0:
                penalty *= 0.6
                issues.append(f"summary has {prod_in_summary} prod AI keywords but no career matches")
    
    # Check 11: Salary range inverted
    salary = signals.get("expected_salary_range_inr_lpa", {})
    if salary:
        s_min = salary.get("min", 0) or 0
        s_max = salary.get("max", 0) or 0
        if s_min > s_max and s_max > 0:
            penalty *= 0.6
            issues.append(f"salary range inverted: min={s_min}L > max={s_max}L")
        elif s_min == s_max and s_min > 0:
            penalty *= 0.85
            issues.append(f"salary range single point: {s_min}L")
    
    # Check 12: Signup after last active
    signup = signals.get("signup_date", "")
    last_active = signals.get("last_active_date", "")
    if signup and last_active:
        try:
            sp = tuple(int(p) for p in signup.split("-"))
            ap = tuple(int(p) for p in last_active.split("-"))
            if len(sp) == 3 and len(ap) == 3 and ap < sp:
                penalty *= 0.5
                issues.append(f"last active {last_active} before signup {signup}")
        except (ValueError, IndexError):
            pass
    
    # Check 13: Offer acceptance without interviews
    offer_rate = signals.get("offer_acceptance_rate", -1)
    interview_rate = signals.get("interview_completion_rate", 0)
    if offer_rate > 0.5 and interview_rate == 0:
        penalty *= 0.6
        issues.append(f"offer acceptance {offer_rate:.0%} but 0% interview completion")
    
    # Check 14: Skill-career mismatch (advanced skills not evidenced in career)
    if ai_skill_overlap >= 2:
        career_text = " ".join([(h.get("description") or "").lower() for h in history]).lower()
        unmatched = 0
        for s in skills:
            if s["name"] in AI_CORE_SKILLS and s["name"].lower() not in career_text:
                unmatched += 1
        if unmatched >= 4:
            penalty *= 0.5
            issues.append(f"{unmatched} AI skills not evidenced in career history")
    
    # Check 15: Keyword density anomaly (>10 AI keyword mentions per 1000 chars)
    # Thresholds chosen to catch obvious keyword stuffers (e.g., 10+ matches in 400 chars = 25/1K)
    # while allowing genuine ML engineers who naturally mention ranking/retrieval in context.
    all_desc = " ".join([(h.get("description") or "").lower() for h in history])
    ai_count = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in all_desc)
    total_chars = max(len(all_desc), 1)
    density = ai_count / total_chars * 1000
    if density > 14.0:
        penalty *= 0.5
        issues.append(f"keyword density anomaly: {ai_count} matches in {total_chars} chars ({density:.1f}/1K)")
    elif density > 10.0:
        penalty *= 0.7
        issues.append(f"elevated keyword density ({density:.1f}/1K)")
    
    # Check 16: Impossible age/timeline
    earliest_work_year = 2026
    for h in history:
        start = h.get("start_date", "")
        if start and len(start) >= 4:
            try:
                yr = int(start[:4])
                earliest_work_year = min(earliest_work_year, yr)
            except ValueError:
                pass
    
    earliest_edu_start = 2026
    for e in edus:
        yr = e.get("start_year", 0) or 0
        if yr > 0:
            earliest_edu_start = min(earliest_edu_start, yr)
    
    if earliest_work_year < 2026 and earliest_edu_start < 2026:
        # If they started working before finishing (or even starting) education
        if earliest_work_year < earliest_edu_start - 2:  # Started working 2+ years before education
            penalty *= 0.6
            issues.append(f"started working ({earliest_work_year}) before education ({earliest_edu_start})")
    
    # Check 17: No verifiable internet presence (ghost score)
    ghost_signals = 0
    if signals.get("search_appearance_30d", 0) < 10:
        ghost_signals += 1
    if signals.get("saved_by_recruiters_30d", 0) == 0:
        ghost_signals += 1
    if signals.get("github_activity_score", -1) < 0:
        ghost_signals += 1
    if not signals.get("verified_email", False):
        ghost_signals += 1
    if not signals.get("verified_phone", False):
        ghost_signals += 1
    if ghost_signals >= 4:
        penalty *= 0.5
        issues.append(f"no verifiable internet presence ({ghost_signals}/5 signals missing)")
    
    # Check 18: Skill count anomaly
    skill_count = len(skills)
    if skill_count > 20:
        penalty *= 0.7
        issues.append(f"unusually high skill count ({skill_count})")
    elif skill_count < 3 and years_exp > 5:
        penalty *= 0.6
        issues.append(f"only {skill_count} skills for {years_exp}yrs experience")
    
    # Check 19: Temporal order inversion
    for h in history:
        start = h.get("start_date", "")
        end = h.get("end_date", "") or ""
        if start and end:
            try:
                if end < start:
                    penalty *= 0.5
                    issues.append(f"job end date before start date: {h.get('title', '')}")
                    break
            except (ValueError, IndexError):
                pass
    
    # Check 20: Education end year in the future
    for e in edus:
        end_yr = e.get("end_year", 0) or 0
        if end_yr > 2026:
            penalty *= 0.5
            issues.append(f"education end year {end_yr} is in the future")
            break
    
    return penalty, issues


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: FAST FILTER SCORE
# ═══════════════════════════════════════════════════════════════════════════════

def compute_cheap_score(candidate, semantic_similarity):
    """Compute Stage 1 score using only cheap features.
    
    Components: TF-IDF semantic, title tier, experience, location, quick keyword counts.
    """
    profile = candidate.get("profile", {})
    years_exp = profile.get("years_of_experience", 0) or 0
    
    # Fast title tier
    title = profile.get("current_title", "") or ""
    title_tier_val = _title_tier_score(title)
    title_normalized = 1.0 - math.exp(-title_tier_val / 6)
    
    # Fast keyword counts
    summary = (profile.get("summary") or "").lower()
    rr_keywords_in_summary = sum(1 for kw in RETRIEVAL_RANKING_KEYWORDS if kw in summary)
    rr_summary_norm = 1.0 - math.exp(-rr_keywords_in_summary * 0.3)
    
    # Experience fit (fast)
    exp_fit = experience_fit_score(years_exp)
    
    # Location (fast)
    loc_score = location_preference_score(candidate)
    
    # Build cheap composite
    score = (
        semantic_similarity * 0.30 +
        title_normalized * 0.25 +
        rr_summary_norm * 0.20 +
        exp_fit * 0.15 +
        loc_score * 0.10
    )
    
    return score


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: DEEP SCORE
# ═══════════════════════════════════════════════════════════════════════════════

def compute_total_score(candidate):
    """Compute final composite score for a candidate.
    
    Multi-dimensional scoring with behavioral multiplier (not additive).
    Components aligned for NDCG@10 optimization.
    """
    profile = candidate.get("profile", {})
    years_exp = profile.get("years_of_experience", 0) or 0
    
    # --- Core career signals ---
    career_score = career_history_score(candidate)
    career_normalized = 1.0 - math.exp(-career_score / 15)
    
    # --- Role relevance ---
    role_score = role_relevance_score(candidate)
    role_normalized = 1.0 - math.exp(-role_score / 5)
    
    # --- Production AI evidence ---
    prod_ai_score = production_ai_evidence_score(candidate)
    prod_ai_normalized = 1.0 - math.exp(-prod_ai_score / 10)
    
    # --- Retrieval & Ranking experience ---
    rr_score = retrieval_ranking_experience_score(candidate)
    rr_normalized = 1.0 - math.exp(-rr_score / 12)
    
    # --- Experience fit ---
    exp_fit = experience_fit_score(years_exp)
    
    # --- Skills match (minimal) ---
    skills_score = skills_match_score(candidate)
    skills_normalized = 1.0 - math.exp(-skills_score / 15)
    
    # --- Education ---
    edu_fit = education_score(candidate)
    
    # --- NEW: Career progression ---
    prog = career_progression_score(candidate)
    
    # --- NEW: Skill-career coherence ---
    coherence = skill_career_coherence_score(candidate)
    
    # --- NEW: Company quality ---
    company_qual = company_quality_score(candidate)
    
    # --- NEW: Negative signal penalty ---
    neg_penalty = negative_signal_penalty(candidate)
    
    # --- NEW: Rare skill diamond bonus ---
    diamond = rare_skill_diamond_score(candidate)
    
    # --- NEW: Talent platform industry bonus ---
    talent = talent_platform_bonus(candidate)
    
    # --- NEW: Profile consistency ---
    consistency = profile_consistency_score(candidate)
    
    # --- Honeypot detection (full) ---
    hon_penalty, hon_issues = detect_honeypot_deep(candidate)
    
    # --- Base score using strategic weights ---
    base = (
        career_normalized * WEIGHTS["career_relevance"] +
        role_normalized * WEIGHTS["role_relevance"] +
        prod_ai_normalized * WEIGHTS["production_ai_evidence"] +
        rr_normalized * WEIGHTS["retrieval_ranking_experience"] +
        exp_fit * WEIGHTS["experience_fit"] +
        skills_normalized * WEIGHTS["skills_match"] +
        edu_fit * WEIGHTS["education_score"] +
        prog * 0.10 +                     # Career progression
        coherence * 0.04 +                # Skill-career coherence
        company_qual * 0.03 +             # Company quality bonus
        diamond * 0.06 +                  # Rare skill diamond (unicorn bonus)
        talent * 0.04 +                   # Talent platform domain bonus
        (0.0 - neg_penalty * 0.07)        # Negative signal penalty
    )
    
    # --- Profile consistency multiplier ---
    score = base * consistency
    
    # --- Behavioral multiplier (NOT additive) ---
    behav_mult = behavioral_multiplier(candidate)
    score *= behav_mult
    
    # --- Location & notice period bonuses (small additive) ---
    loc_score = location_preference_score(candidate)
    notice = notice_period_score(candidate)
    score += loc_score * 0.03 + notice * 0.02
    
    # --- Honeypot penalty ---
    score *= hon_penalty
    
    # Safety clamp: prevent negative scores
    score = max(0.0, score)
    
    return score, hon_penalty, hon_issues


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 3: S-CURVE TRANSFORMATION & REASONING
# ═══════════════════════════════════════════════════════════════════════════════

def s_curve_transform(scores, steepness=SCURVE_STEEPNESS, midpoint=SCURVE_MIDPOINT):
    """Apply S-curve (sigmoid) transformation to spread top scores.
    
    Creates larger gaps between top candidates for better NDCG@10.
    Scores below midpoint get compressed; scores above get amplified.
    
    Adaptive: if max score < 0.5 (low-quality pool), skip transformation
    to avoid over-compressing already-low scores.
    """
    if not scores:
        return []
    max_score = max(scores)
    if max_score < 0.5:
        return list(scores)  # Skip transformation for low-quality pools
    return [1.0 / (1.0 + math.exp(-steepness * (s - midpoint))) for s in scores]


def generate_reasoning(candidate, score, hon_penalty, hon_issues):
    """Generate varied, specific reasoning for each candidate.
    Only called for the final top 100 candidates.
    """
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "")
    headline = profile.get("headline", "")
    years_exp = profile.get("years_of_experience", 0) or 0
    signals = candidate.get("redrob_signals", {})
    history = candidate.get("career_history", [])
    location = profile.get("location", "")
    company = profile.get("current_company", "")
    industry = profile.get("current_industry", "")
    
    parts = []
    
    if hon_penalty < 0.3:
        parts.append("HIGH-RISK HONEYPOT CANDIDATE")
        if hon_issues:
            parts.append(f"({'; '.join(hon_issues[:2])})")
    elif hon_penalty < 0.8:
        parts.append("SUSPICIOUS PROFILE")
        if hon_issues:
            parts.append(f"({'; '.join(hon_issues[:2])})")
    
    parts.append(f"{title}")
    exp_str = f"{years_exp:.0f}yrs"
    if company:
        exp_str += f" at {company}"
    parts.append(exp_str)
    
    history_desc = " ".join([(h.get("description") or "").lower() for h in history])
    prod_signals = []
    for kw in ["retrieval", "ranking", "recommendation", "search", "embeddings",
               "vector", "faiss", "pinecone", "ndcg", "mrr", "production ml",
               "evaluation", "a/b testing"]:
        if kw in history_desc:
            prod_signals.append(kw)
    if prod_signals:
        if len(prod_signals) >= 4:
            parts.append(f"built {', '.join(prod_signals[:4])} systems")
        elif len(prod_signals) >= 2:
            parts.append(f"experience in {', '.join(prod_signals[:3])}")
        else:
            parts.append(f"worked on {prod_signals[0]}")
    
    hl = headline.lower()
    if hl and title.lower() not in hl:
        if any(kw in hl for kw in ["ai", "ml", "machine learning", "deep learning"]):
            parts.append("headline signals AI focus")
    
    industry_lower = industry.lower()
    if any(kw in industry_lower for kw in ["ai", "software", "technology", "internet", "saas", "product"]):
        parts.append("product co")
    elif any(kw in industry_lower for kw in ["fintech", "healthtech", "edtech"]):
        parts.append(f"{industry_lower} sector")
    
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
    
    notice = signals.get("notice_period_days", 90)
    if notice <= 15:
        parts.append("immediate join")
    elif notice <= 30:
        parts.append("short notice")
    elif notice >= 120:
        parts.append(f"{notice}d notice")
    
    # --- Diamond skill signal ---
    diamond = rare_skill_diamond_score(candidate)
    if diamond >= 0.8:
        parts.append("★ full-skill diamond")
    elif diamond >= 0.5:
        parts.append("★ partial diamond skills")
    
    # --- Talent platform signal ---
    talent = talent_platform_bonus(candidate)
    if talent >= 0.8:
        parts.append("★ HR tech domain expert")
    elif talent >= 0.5:
        parts.append("recruiting domain exp")
    
    if location:
        loc_lower = location.lower()
        if "pune" in loc_lower or "noida" in loc_lower:
            parts.append(f"based {location} (pref location)")
        else:
            parts.append(f"based {location}")
    
    reasoning = "; ".join(parts)
    return reasoning


# ═══════════════════════════════════════════════════════════════════════════════
# MULTI-STAGE PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def phase0_build_semantic_matcher(candidate_generator):
    """Phase 0: Build TF-IDF semantic matcher from all candidates.
    
    Optimized approach:
    - One pass: load + build texts
    - Fit TF-IDF on a SAMPLE of texts (IDF stabilizes fast)
    - Precompute ALL candidate vectors in ONE bulk transform call
    - Caches texts to avoid rebuilding in Phase 1
    
    Returns (matcher, candidates, cached_texts) for Phase 1.
    """
    print("  Phase 0: Loading candidates and building semantic matcher...", file=sys.stderr)
    start = time.time()
    
    # One pass: load candidates, build texts for ALL candidates
    candidates = []
    all_texts = []
    for candidate in candidate_generator:
        text = build_candidate_text(candidate)
        all_texts.append(text)
        candidates.append(candidate)
    
    # Fit TF-IDF on a SAMPLE (first K docs) — IDF stabilizes quickly
    # This is much faster than fitting on all 100K
    sample_size = min(TFIDF_SAMPLE_SIZE, len(all_texts))
    matcher = SemanticMatcher()
    matcher.fit(all_texts[:sample_size])
    
    # Precompute ALL candidate vectors in ONE bulk transform call
    # This replaces 100K individual transform() calls with 1 vectorized call
    print(f"  Precomputing {len(all_texts)} candidate vectors...", file=sys.stderr)
    vec_start = time.time()
    matcher.precompute_all_vectors(all_texts)
    vec_time = time.time() - vec_start
    
    elapsed = time.time() - start
    print(f"  Phase 0 complete: {len(candidates)} candidates, "
          f"{matcher.vectorizer.get_feature_names_out().shape[0]} features "
          f"(fit on {sample_size} sample, {len(all_texts)} total vectors in {vec_time:.1f}s, "
          f"total {elapsed:.1f}s)", file=sys.stderr)
    
    # Debug: show top JD terms
    top = matcher.top_terms(15)
    if top:
        print(f"  Top JD intent terms: {', '.join(f'{t}({w:.3f})' for t, w in top)}", file=sys.stderr)
    
    return matcher, candidates, all_texts


def phase1_fast_filter(matcher, candidates):
    """Phase 1: Fast scoring for all candidates, keep top K.
    
    Uses precomputed TF-IDF vectors (O(1) lookup) + cheap features.
    Phase 0 already built all vectors in bulk — this avoids 100K individual transform() calls.
    Returns heap of top K entries.
    """
    print(f"\n  Phase 1: Fast-filtering {len(candidates)} candidates...", file=sys.stderr)
    start = time.time()
    
    heap = []
    honeypot_count = 0
    total = len(candidates)
    
    for i, candidate in enumerate(candidates):
        # Use precomputed TF-IDF vectors — O(1) lookup, no transform() call
        semantic_sim = matcher.get_similarity(i)
        
        # Fast honeypot check
        hon_penalty, hon_issues = detect_honeypot_fast(candidate)
        if hon_penalty < 0.2:
            honeypot_count += 1
            continue  # Eliminate certain honeypots immediately
        
        # Cheap score
        cheap = compute_cheap_score(candidate, semantic_sim)
        fast_score = cheap * hon_penalty
        
        cid = candidate.get("candidate_id", f"CAND_{i+1:07d}")
        
        # Maintain heap of top K
        if len(heap) < FAST_FILTER_TOP_K:
            heapq.heappush(heap, (fast_score, cid, i))
        else:
            if fast_score > heap[0][0]:
                heapq.heapreplace(heap, (fast_score, cid, i))
        
        if (i + 1) % 25000 == 0:
            elapsed = time.time() - start
            print(f"    {i+1}/{total} ({elapsed:.1f}s)", file=sys.stderr)
    
    elapsed = time.time() - start
    print(f"  Phase 1 complete: {total} -> {min(len(heap), FAST_FILTER_TOP_K)} candidates ({elapsed:.1f}s)", file=sys.stderr)
    print(f"  Eliminated {honeypot_count} certain honeypots in fast-filter", file=sys.stderr)
    
    return heap


def phase2_deep_analysis(matcher, heap, candidates):
    """Phase 2: Deep analysis of top candidates.
    
    Computes full scoring: deep features, full honeypot detection,
    career progression, skill-career coherence, negative signals.
    Returns list of (score, candidate_id, reasoning_data) sorted by score descending.
    """
    print(f"\n  Phase 2: Deep-analyzing {len(heap)} candidates...", file=sys.stderr)
    start = time.time()
    
    # Extract top candidates from heap
    top_indices = [(score, cid, idx) for score, cid, idx in heap]
    top_indices.sort(key=lambda x: -x[0])  # Sort descending by score
    
    deep_results = []
    
    for rank, (fast_score, cid, idx) in enumerate(top_indices):
        candidate = candidates[idx]
        
        # Compute full score with all deep features
        score, hon_penalty, hon_issues = compute_total_score(candidate)
        
        deep_results.append((score, cid, hon_penalty, hon_issues))
        
        if (rank + 1) % 100 == 0:
            elapsed = time.time() - start
            print(f"    Analyzed {rank + 1} candidates ({elapsed:.1f}s)", file=sys.stderr)
    
    # Sort by score descending
    deep_results.sort(key=lambda x: -x[0])
    
    elapsed = time.time() - start
    print(f"  Phase 2 complete: {len(deep_results)} candidates scored ({elapsed:.1f}s)", file=sys.stderr)
    
    return deep_results


def phase3_final_polish(deep_results, candidates):
    """Phase 3: Final polish — S-curve, reasoning, verification.
    
    Only generates reasoning for the final top 100.
    """
    print(f"\n  Phase 3: Final polish...", file=sys.stderr)
    start = time.time()
    
    # Take top 100
    top_100 = deep_results[:FINAL_TOP_K]
    
    # Extract raw scores
    raw_scores = [r[0] for r in top_100]
    
    # Apply S-curve transformation for NDCG@10 optimization
    transformed = s_curve_transform(raw_scores)
    
    # Build final entries with reasoning
    final_entries = []
    for i, (raw_score, cid, hon_penalty, hon_issues) in enumerate(top_100):
        candidate = candidates[find_candidate_index(cid, candidates)]
        
        # Transform score
        s_curve_score = transformed[i]
        
        # Generate reasoning (only for top 100)
        reasoning = generate_reasoning(candidate, s_curve_score, hon_penalty, hon_issues)
        
        final_entries.append((s_curve_score, cid, reasoning, hon_penalty, hon_issues))
    
    # Sort by transformed score descending
    final_entries.sort(key=lambda x: -x[0])
    
    # Apply deterministic tie-breaking
    final_entries.sort(key=lambda x: (-round(x[0], 4), x[1]))
    
    # Verify honeypot ratio
    hon_in_top = sum(1 for h in final_entries if h[3] < 0.5)
    hon_ratio = hon_in_top / len(final_entries)
    print(f"  Honeypots in top {FINAL_TOP_K}: {hon_in_top}/{len(final_entries)} ({hon_ratio*100:.1f}%)", file=sys.stderr)
    if hon_ratio > 0.10:
        print(f"  WARNING: Honeypot ratio exceeds 10% threshold!", file=sys.stderr)
    
    # Verify unique reasonings
    reasonings = [r[2] for r in final_entries]
    unique_r = len(set(reasonings))
    print(f"  Unique reasonings: {unique_r}/{len(final_entries)}", file=sys.stderr)
    
    elapsed = time.time() - start
    print(f"  Phase 3 complete ({elapsed:.1f}s)", file=sys.stderr)
    
    return final_entries


def find_candidate_index(cid, candidates):
    """Find index of a candidate by ID in the candidates list."""
    for i, c in enumerate(candidates):
        if c.get("candidate_id") == cid:
            return i
    return 0


# ═══════════════════════════════════════════════════════════════════════════════
# I/O & MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def load_jsonl_line_by_line(path):
    """Generator to yield parsed JSON objects from JSONL file."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_submission(rankings, output_path):
    """Write submission CSV file."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("candidate_id,rank,score,reasoning\n")
        for rank, (score, cid, reasoning, hon_penalty, hon_issues) in enumerate(rankings, 1):
            score_str = f"{score:.4f}"
            reasoning_escaped = reasoning.replace('"', '""')
            f.write(f"{cid},{rank},{score_str},\"{reasoning_escaped}\"\n")
    
    print(f"Submission written to {output_path}", file=sys.stderr)


def run_pipeline(data_file, output_file):
    """Run the full 3-stage ranking pipeline."""
    print("=" * 60, file=sys.stderr)
    print("Redrob Hackathon - Candidate Ranking Pipeline v3.0", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    overall_start = time.time()
    
    # Phase 0: Load and build semantic matcher
    print("\nLoading candidates...", file=sys.stderr)
    matcher, candidates, _ = phase0_build_semantic_matcher(
        load_jsonl_line_by_line(data_file)
    )
    
    # Phase 1: Fast filter (uses precomputed vectors — no transform() calls)
    heap = phase1_fast_filter(matcher, candidates)
    
    # Phase 2: Deep analysis
    deep_results = phase2_deep_analysis(matcher, heap, candidates)
    
    # Phase 3: Final polish
    final_rankings = phase3_final_polish(deep_results, candidates)
    
    # Write output
    print(f"\nWriting submission to {output_file}...", file=sys.stderr)
    write_submission(final_rankings, output_file)
    
    total_elapsed = time.time() - overall_start
    print(f"\n{'=' * 60}", file=sys.stderr)
    print(f"Total time: {total_elapsed:.1f}s", file=sys.stderr)
    print(f"Throughput: {len(candidates) / total_elapsed:.0f} cand/s", file=sys.stderr)
    print(f"Top score: {final_rankings[0][0]:.4f}, Bottom score: {final_rankings[-1][0]:.4f}", file=sys.stderr)
    print(f"Top candidate: {final_rankings[0][1]}", file=sys.stderr)
    print(f"{'=' * 60}", file=sys.stderr)
    
    return final_rankings


def process_candidates(candidate_list):
    """Backward-compatible wrapper for app.py (Streamlit UI).
    
    Uses Phase 1+2 directly since candidates are already in memory.
    """
    if not candidate_list:
        return []
    
    # Build matcher on-the-fly
    matcher = SemanticMatcher()
    corpus = [build_candidate_text(c) for c in candidate_list]
    matcher.fit(corpus)
    matcher.precompute_all_vectors(corpus)  # Precompute for O(1) similarity lookup
    
    # Phase 1 simplified (already in memory) — same pattern as phase1_fast_filter
    heap = []
    for i, candidate in enumerate(candidate_list):
        sim = matcher.get_similarity(i)  # O(1) — uses precomputed array
        hon_p, _ = detect_honeypot_fast(candidate)
        if hon_p < 0.2:
            continue
        cheap = compute_cheap_score(candidate, sim)
        score = cheap * hon_p
        cid = candidate.get("candidate_id", f"CAND_{i+1:07d}")
        if len(heap) < FAST_FILTER_TOP_K:
            heapq.heappush(heap, (score, cid, i))
        elif score > heap[0][0]:
            heapq.heapreplace(heap, (score, cid, i))
    
    # Phase 2
    deep = []
    for score, cid, idx in heap:
        candidate = candidate_list[idx]
        total_score, hon_p, hon_i = compute_total_score(candidate)
        deep.append((total_score, cid, hon_p, hon_i))
    deep.sort(key=lambda x: -x[0])
    
    # Phase 3
    top = deep[:FINAL_TOP_K]
    raw_scores = [r[0] for r in top]
    transformed = s_curve_transform(raw_scores)
    
    final = []
    for i, (raw_score, cid, hon_p, hon_i) in enumerate(top):
        candidate = next((c for c in candidate_list if c.get("candidate_id") == cid), candidate_list[0])
        reasoning = generate_reasoning(candidate, transformed[i], hon_p, hon_i)
        final.append((transformed[i], cid, reasoning, hon_p, hon_i))
    
    final.sort(key=lambda x: (-round(x[0], 4), x[1]))
    return final


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Redrob Hackathon Ranker v3.0")
    parser.add_argument("--validate", action="store_true", help="Only validate existing submission")
    parser.add_argument("--sample", action="store_true", help="Run on sample data only")
    parser.add_argument("--debug-terms", action="store_true", help="Show top TF-IDF JD intent terms")
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
    
    if args.debug_terms:
        # Quick TF-IDF demo on sample data
        sample_path = os.path.join(DATA_DIR, "sample_candidates.json")
        with open(sample_path, "r") as f:
            samples = json.load(f)
        corpus = [build_candidate_text(c) for c in samples]
        matcher = SemanticMatcher()
        matcher.fit(corpus)
        print("Top JD Intent Terms:")
        for term, weight in matcher.top_terms(20):
            print(f"  {term}: {weight:.4f}")
        sys.exit(0)
    
    if args.sample:
        data_file = os.path.join(DATA_DIR, "sample_candidates.json")
        output_file = os.path.join(OUTPUT_DIR, "sample_submission.csv")
        with open(data_file, "r") as f:
            samples = json.load(f)
        rankings = process_candidates(samples)
        write_submission(rankings, output_file)
        
        print("\n=== Top 10 Candidates (Sample) ===")
        for rank, (score, cid, reasoning, hon_penalty, hon_issues) in enumerate(rankings[:10], 1):
            honeypot_tag = " [HONEYPOT]" if hon_penalty < 0.5 else (" [SUSPICIOUS]" if hon_penalty < 0.8 else "")
            print(f"  {rank}. {cid} (score={score:.4f}){honeypot_tag}")
            print(f"     {reasoning[:120]}")
    else:
        data_file = os.path.join(DATA_DIR, "candidates.jsonl")
        output_file = os.path.join(OUTPUT_DIR, "submission.csv")
        run_pipeline(data_file, output_file)
