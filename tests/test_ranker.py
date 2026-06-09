"""
Unit tests for Redrob Hackathon Candidate Ranking System.
Tests: title classification, scoring functions, honeypot detection, experience fit.
"""
import sys
import os
import json
import unittest
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ranker import (
    _title_tier,
    production_ai_evidence_score,
    career_history_score,
    role_relevance_score,
    skills_match_score,
    experience_fit_score,
    education_score,
    redrob_signals_score,
    detect_honeypot,
    compute_total_score,
    generate_reasoning,
)


def _make_candidate(**overrides):
    """Helper to create a minimal candidate dict for testing."""
    candidate = {
        "candidate_id": "CAND_0000001",
        "profile": {
            "anonymized_name": "Test User",
            "headline": "",
            "summary": "",
            "location": "Test City",
            "country": "Test Country",
            "years_of_experience": 7.0,
            "current_title": "Senior Machine Learning Engineer",
            "current_company": "Test Corp",
            "current_company_size": "1001-5000",
            "current_industry": "Technology",
        },
        "career_history": [
            {
                "company": "Test Corp",
                "title": "Senior Machine Learning Engineer",
                "start_date": "2020-01-01",
                "end_date": None,
                "duration_months": 48,
                "is_current": True,
                "industry": "Technology",
                "company_size": "1001-5000",
                "description": "Built production ranking and retrieval systems using vector search and embeddings. Worked on recommendation engine.",
            },
            {
                "company": "Old Corp",
                "title": "ML Engineer",
                "start_date": "2016-01-01",
                "end_date": "2019-12-31",
                "duration_months": 48,
                "is_current": False,
                "industry": "Technology",
                "company_size": "201-500",
                "description": "Developed machine learning models for search relevance.",
            },
        ],
        "education": [
            {
                "institution": "IIT Bombay",
                "degree": "B.Tech",
                "field_of_study": "Computer Science",
                "start_year": 2012,
                "end_year": 2016,
                "grade": "8.5 CGPA",
                "tier": "tier_1",
            }
        ],
        "skills": [
            {"name": "Python", "proficiency": "expert", "endorsements": 20},
            {"name": "PyTorch", "proficiency": "advanced", "endorsements": 15},
            {"name": "Ranking", "proficiency": "advanced", "endorsements": 10},
            {"name": "Information Retrieval", "proficiency": "advanced", "endorsements": 8},
            {"name": "FAISS", "proficiency": "intermediate", "endorsements": 5},
        ],
        "redrob_signals": {
            "profile_completeness_score": 85,
            "signup_date": "2020-01-01",
            "last_active_date": "2025-12-01",
            "open_to_work_flag": True,
            "profile_views_received_30d": 150,
            "applications_submitted_30d": 5,
            "recruiter_response_rate": 0.75,
            "avg_response_time_hours": 12,
            "skill_assessment_scores": {},
            "connection_count": 350,
            "endorsements_received": 45,
            "notice_period_days": 30,
            "expected_salary_range_inr_lpa": {"min": 25, "max": 45},
            "preferred_work_mode": "remote",
            "willing_to_relocate": True,
            "github_activity_score": 60,
            "search_appearance_30d": 200,
            "saved_by_recruiters_30d": 15,
            "interview_completion_rate": 0.9,
            "offer_acceptance_rate": 0.5,
            "verified_email": True,
            "verified_phone": True,
            "linkedin_connected": True,
        },
    }
    # Apply overrides
    for key, value in overrides.items():
        if key == "years_of_experience":
            candidate["profile"]["years_of_experience"] = value
        elif key == "current_title":
            candidate["profile"]["current_title"] = value
        elif key == "headline":
            candidate["profile"]["headline"] = value
        elif key == "summary":
            candidate["profile"]["summary"] = value
        elif key == "skills":
            candidate["skills"] = value
        elif key == "career_history":
            candidate["career_history"] = value
        elif key == "education":
            candidate["education"] = value
        elif key == "redrob_signals":
            candidate["redrob_signals"] = value
        elif key == "candidate_id":
            candidate["candidate_id"] = value
    return candidate


class TestTitleTier(unittest.TestCase):
    """Test the _title_tier function."""

    def test_tier_a_titles(self):
        self.assertEqual(_title_tier("Senior Machine Learning Engineer"), 2)
        self.assertEqual(_title_tier("AI Engineer"), 2)
        self.assertEqual(_title_tier("ML Engineer"), 2)
        self.assertEqual(_title_tier("Data Scientist"), 2)
        self.assertEqual(_title_tier("Search Engineer"), 2)
        self.assertEqual(_title_tier("NLP Engineer"), 2)

    def test_tier_b_titles(self):
        self.assertEqual(_title_tier("Backend Engineer"), 1)
        self.assertEqual(_title_tier("Software Engineer"), 1)
        self.assertEqual(_title_tier("DevOps Engineer"), 1)
        self.assertEqual(_title_tier("Data Engineer"), 1)
        self.assertEqual(_title_tier("Full Stack Developer"), 1)

    def test_tier_c_titles(self):
        self.assertEqual(_title_tier("HR Manager"), -1)
        self.assertEqual(_title_tier("Accountant"), -1)
        self.assertEqual(_title_tier("Sales Executive"), -1)
        self.assertEqual(_title_tier("Marketing Manager"), -1)
        self.assertEqual(_title_tier("Civil Engineer"), -1)
        self.assertEqual(_title_tier("Business Analyst"), -1)

    def test_neutral_titles(self):
        self.assertEqual(_title_tier("Unknown Role"), 0)
        self.assertEqual(_title_tier("Some Random Title"), 0)
        self.assertEqual(_title_tier(""), 0)


class TestExperienceFitScore(unittest.TestCase):
    """Test the experience_fit_score function."""

    def test_zero_experience(self):
        self.assertEqual(experience_fit_score(0), 0.0)

    def test_below_min(self):
        score = experience_fit_score(1)
        self.assertLess(score, 0.3)

    def test_peak_range(self):
        # 5-9 years should be the peak
        score_5 = experience_fit_score(5)
        score_7 = experience_fit_score(7)
        score_9 = experience_fit_score(9)
        self.assertGreater(score_7, 0.9)
        self.assertGreater(score_5, 0.8)
        self.assertGreater(score_9, 0.8)

    def test_decline_after_peak(self):
        score_12 = experience_fit_score(12)
        score_15 = experience_fit_score(15)
        self.assertLess(score_12, 0.8)
        self.assertLess(score_15, 0.5)

    def test_monotonic_in_early_years(self):
        """Score should increase from 2 to 7 years."""
        scores = [experience_fit_score(y) for y in range(2, 8)]
        for i in range(len(scores) - 1):
            self.assertGreaterEqual(scores[i + 1], scores[i],
                                    f"Score dropped between year {2 + i} and {3 + i}")


class TestProductionAIEvidence(unittest.TestCase):
    """Test production_ai_evidence_score."""

    def test_high_prod_ai_score(self):
        candidate = _make_candidate()
        score = production_ai_evidence_score(candidate)
        self.assertGreater(score, 0)

    def test_no_prod_ai(self):
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "Test Corp",
                    "title": "Manager",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 48,
                    "is_current": True,
                    "industry": "Finance",
                    "company_size": "1001-5000",
                    "description": "Managed a team of accountants.",
                }
            ],
            summary="I manage people.",
            skills=[]
        )
        score = production_ai_evidence_score(candidate)
        self.assertEqual(score, 0.0)


class TestCareerHistoryScore(unittest.TestCase):
    """Test career_history_score."""

    def test_ai_career_scores_high(self):
        candidate = _make_candidate()
        score = career_history_score(candidate)
        self.assertGreater(score, 0)

    def test_empty_history(self):
        candidate = _make_candidate(career_history=[])
        score = career_history_score(candidate)
        self.assertEqual(score, 0.0)

    def test_non_ai_career_scores_lower(self):
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "Some Corp",
                    "title": "Accountant",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 48,
                    "is_current": True,
                    "industry": "Finance",
                    "company_size": "1001-5000",
                    "description": "Did accounting work.",
                }
            ]
        )
        score = career_history_score(candidate)
        self.assertLess(score, 2.0)

    def test_consulting_penalty(self):
        """Entire career at consulting firms should get penalized (50% reduction)."""
        # Same candidate without consulting penalty (non-consulting firm names)
        non_consulting = _make_candidate()
        non_consulting_score = career_history_score(non_consulting)

        # Now with consulting firms
        consulting = _make_candidate(
            career_history=[
                {
                    "company": "tcs",
                    "title": "Software Engineer",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 48,
                    "is_current": True,
                    "industry": "Technology",
                    "company_size": "10001+",
                    "description": "Worked on client projects.",
                },
                {
                    "company": "infosys",
                    "title": "Junior Developer",
                    "start_date": "2016-01-01",
                    "end_date": "2019-12-31",
                    "duration_months": 48,
                    "is_current": False,
                    "industry": "Technology",
                    "company_size": "10001+",
                    "description": "Developed software.",
                },
            ]
        )
        consulting_score = career_history_score(consulting)
        # Consulting score should be at most 60% of non-consulting (50% penalty + lower title tiers)
        if non_consulting_score > 0:
            self.assertLess(consulting_score / non_consulting_score, 0.6)


class TestHoneypotDetection(unittest.TestCase):
    """Test detect_honeypot function."""

    def test_clean_candidate(self):
        candidate = _make_candidate()
        penalty, issues = detect_honeypot(candidate)
        self.assertEqual(penalty, 1.0)
        self.assertEqual(len(issues), 0)

    def test_overlapping_education(self):
        candidate = _make_candidate(
            education=[
                {
                    "institution": "IIT Bombay",
                    "degree": "B.Tech",
                    "field_of_study": "CS",
                    "start_year": 2012,
                    "end_year": 2016,
                    "tier": "tier_1",
                },
                {
                    "institution": "IIT Delhi",
                    "degree": "M.Tech",
                    "field_of_study": "CS",
                    "start_year": 2014,
                    "end_year": 2016,
                    "tier": "tier_1",
                },
            ]
        )
        penalty, issues = detect_honeypot(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("overlapping" in i for i in issues))

    def test_timeline_inconsistency(self):
        """Graduated in 2024 but has 15 years experience."""
        candidate = _make_candidate(
            years_of_experience=15,
            education=[
                {
                    "institution": "Test Univ",
                    "degree": "B.Tech",
                    "field_of_study": "CS",
                    "start_year": 2020,
                    "end_year": 2024,
                    "tier": "tier_3",
                }
            ]
        )
        penalty, issues = detect_honeypot(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("timeline" in i for i in issues))

    def test_career_exceeds_stated(self):
        """Career history sums to more years than stated experience."""
        candidate = _make_candidate(
            years_of_experience=3,
            career_history=[
                {
                    "company": "A",
                    "title": "Engineer",
                    "start_date": "2015-01-01",
                    "end_date": "2020-01-01",
                    "duration_months": 60,
                    "is_current": False,
                    "industry": "Technology",
                    "company_size": "1001-5000",
                    "description": "Did some work.",
                },
                {
                    "company": "B",
                    "title": "Senior Engineer",
                    "start_date": "2010-01-01",
                    "end_date": "2015-01-01",
                    "duration_months": 60,
                    "is_current": False,
                    "industry": "Technology",
                    "company_size": "1001-5000",
                    "description": "Did more work.",
                },
            ]
        )
        penalty, issues = detect_honeypot(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("exceeds" in i for i in issues))

    def test_short_descriptions(self):
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "Test",
                    "title": "Engineer",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 12,
                    "is_current": True,
                    "industry": "Technology",
                    "company_size": "1-10",
                    "description": "Hi",
                }
            ]
        )
        penalty, issues = detect_honeypot(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("short" in i for i in issues))

    def test_ai_skills_no_background(self):
        """4+ AI skills but no AI education or role."""
        candidate = _make_candidate(
            current_title="Accountant",
            career_history=[
                {
                    "company": "Firm",
                    "title": "Accountant",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 48,
                    "is_current": True,
                    "industry": "Finance",
                    "company_size": "1001-5000",
                    "description": "Did accounting.",
                }
            ],
            education=[
                {
                    "institution": "Test Univ",
                    "degree": "B.Com",
                    "field_of_study": "Commerce",
                    "start_year": 2016,
                    "end_year": 2020,
                    "tier": "tier_4",
                }
            ],
            skills=[
                {"name": "PyTorch", "proficiency": "advanced", "endorsements": 5},
                {"name": "TensorFlow", "proficiency": "advanced", "endorsements": 3},
                {"name": "Deep Learning", "proficiency": "advanced", "endorsements": 2},
                {"name": "Computer Vision", "proficiency": "intermediate", "endorsements": 1},
                {"name": "NLP", "proficiency": "intermediate", "endorsements": 1},
            ]
        )
        penalty, issues = detect_honeypot(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("AI skills" in i for i in issues))

    def test_empty_descriptions_all(self):
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "Test",
                    "title": "Engineer",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 12,
                    "is_current": True,
                    "industry": "Technology",
                    "company_size": "1-10",
                    "description": "",
                },
                {
                    "company": "Old",
                    "title": "Junior",
                    "start_date": "2018-01-01",
                    "end_date": "2019-12-31",
                    "duration_months": 24,
                    "is_current": False,
                    "industry": "Technology",
                    "company_size": "1-10",
                    "description": "",
                },
            ]
        )
        penalty, issues = detect_honeypot(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("empty" in i for i in issues))

    def test_job_hopping_zero_duration(self):
        candidate = _make_candidate(
            years_of_experience=5,
            career_history=[
                {
                    "company": f"Co{i}",
                    "title": "Engineer",
                    "start_date": f"202{i}-01-01",
                    "end_date": None if i == 4 else f"202{i}-12-31",
                    "duration_months": 0,
                    "is_current": i == 4,
                    "industry": "Technology",
                    "company_size": "1-10",
                    "description": f"Worked at company {i}.",
                }
                for i in range(5)
            ]
        )
        penalty, issues = detect_honeypot(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("duration" in i for i in issues))


class TestComputeTotalScore(unittest.TestCase):
    """Test the full scoring pipeline."""

    def test_strong_candidate_scores_high(self):
        candidate = _make_candidate()
        score, penalty, issues = compute_total_score(candidate)
        self.assertGreater(score, 0.7)  # New weights: strong candidates still score high
        self.assertEqual(penalty, 1.0)

    def test_weak_candidate_scores_low(self):
        candidate = _make_candidate(
            current_title="HR Manager",
            years_of_experience=1,
            career_history=[
                {
                    "company": "HR Corp",
                    "title": "HR Manager",
                    "start_date": "2024-01-01",
                    "end_date": None,
                    "duration_months": 12,
                    "is_current": True,
                    "industry": "Services",
                    "company_size": "1001-5000",
                    "description": "Managed HR operations.",
                }
            ],
            education=[
                {
                    "institution": "Unknown",
                    "degree": "BA",
                    "field_of_study": "Arts",
                    "start_year": 2020,
                    "end_year": 2024,
                    "grade": "",
                    "tier": "tier_4",
                }
            ],
            skills=[],
            redrob_signals={}
        )
        score, penalty, issues = compute_total_score(candidate)
        self.assertLess(score, 0.5)

    def test_honeypot_penalty_applied(self):
        candidate = _make_candidate(
            years_of_experience=15,
            education=[
                {
                    "institution": "Test",
                    "degree": "B.Tech",
                    "field_of_study": "CS",
                    "start_year": 2022,
                    "end_year": 2024,
                    "tier": "tier_4",
                }
            ]
        )
        score, penalty, issues = compute_total_score(candidate)
        self.assertLess(penalty, 1.0)
        self.assertLess(score, 0.8)  # Penalized


class TestGenerateReasoning(unittest.TestCase):
    """Test the generate_reasoning function."""

    def test_reasoning_contains_key_info(self):
        candidate = _make_candidate()
        score, penalty, issues = compute_total_score(candidate)
        reasoning = generate_reasoning(candidate, score, penalty, issues)
        self.assertIn("Senior Machine Learning Engineer", reasoning)
        self.assertIn("7yrs", reasoning)
        # New reasoning format uses "built ... systems" instead of "prod exp:"
        self.assertTrue("built" in reasoning or "systems" in reasoning)


class TestRedrobSignals(unittest.TestCase):
    """Test the redrob_signals_score function."""

    def test_complete_signals_score_high(self):
        candidate = _make_candidate()
        score = redrob_signals_score(candidate)
        self.assertGreater(score, 0.5)

    def test_empty_signals_score_zero(self):
        candidate = _make_candidate(redrob_signals={})
        score = redrob_signals_score(candidate)
        self.assertEqual(score, 0.0)

    def test_no_github_penalty(self):
        signals = _make_candidate()["redrob_signals"].copy()
        signals["github_activity_score"] = -1
        candidate = _make_candidate(redrob_signals=signals)
        score = redrob_signals_score(candidate)
        self.assertGreater(score, 0)  # Should still have other signals


class TestEducationScore(unittest.TestCase):
    """Test the education_score function."""

    def test_top_tier_relevant_field(self):
        candidate = _make_candidate()
        score = education_score(candidate)
        self.assertGreater(score, 2.0)

    def test_no_education(self):
        candidate = _make_candidate(education=[])
        score = education_score(candidate)
        self.assertEqual(score, 0.0)

    def test_low_tier_irrelevant_field(self):
        candidate = _make_candidate(
            education=[
                {
                    "institution": "Unknown",
                    "degree": "BA",
                    "field_of_study": "Arts",
                    "start_year": 2010,
                    "end_year": 2014,
                    "grade": "",
                    "tier": "tier_4",
                }
            ]
        )
        score = education_score(candidate)
        self.assertLess(score, 2.0)


class TestIntegration(unittest.TestCase):
    """Integration tests: process sample candidates end-to-end."""

    def test_sample_candidates_ranked(self):
        """Load sample data and verify all get scored."""
        sample_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "sample_candidates.json"
        )
        with open(sample_path, "r") as f:
            samples = json.load(f)

        for candidate in samples:
            score, penalty, issues = compute_total_score(candidate)
            self.assertGreaterEqual(score, 0)
            self.assertGreaterEqual(penalty, 0)
            self.assertLessEqual(penalty, 1.0)

        # Verify the top candidate is an AI role
        scored = [(compute_total_score(c), c) for c in samples]
        scored.sort(key=lambda x: -x[0][0])
        top_candidate = scored[0][1]
        top_title = top_candidate["profile"]["current_title"].lower()
        # The top candidate should have a relevant title or production AI evidence
        self.assertTrue(
            any(kw in top_title for kw in ["engineer", "scientist", "developer", "architect"])
            or production_ai_evidence_score(top_candidate) > 0
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
