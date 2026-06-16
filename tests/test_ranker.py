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
    behavioral_multiplier,
    detect_honeypot_fast,
    detect_honeypot_deep,
    compute_total_score,
    generate_reasoning,
    negative_signal_penalty,
    skill_career_coherence_score,
    career_progression_score,
    company_quality_score,
    s_curve_transform,
    rare_skill_diamond_score,
    talent_platform_bonus,
    profile_consistency_score,
    latent_role_classifier,
    latent_role_bonus,
    recruiter_attractiveness_score,
    startup_fit_score,
    continuous_honeypot_risk_score,
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
                "description": "Led development of ML-powered systems for the company's core ranking service. Built data pipelines and model serving infrastructure in Python and PyTorch. Worked closely with product teams to define requirements, implemented A/B testing frameworks, and monitored system performance in production. The team shipped bi-weekly updates and maintained 99.9% uptime. Managed relationships with three downstream teams and coordinated release schedules across four services. Led quarterly planning sessions and presented technical roadmaps to senior leadership, which helped align engineering priorities with business goals.",
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
                "description": "Developed machine learning models for information retrieval tasks. Improved search relevance through feature engineering and model optimization. Collaborated with cross-functional teams to launch new features, conducted code reviews, and mentored junior engineers. Also contributed to the team's sprint planning and retrospective ceremonies. Participated in weekly standups and bi-weekly retrospectives. Documented system architecture decisions and maintained runbooks for production incidents. Helped onboard three new engineers and created training materials for the team's ML platform.",
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
    """Test detect_honeypot_deep function (20 checks)."""

    def test_clean_candidate(self):
        candidate = _make_candidate()
        penalty, issues = detect_honeypot_deep(candidate)
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
        penalty, issues = detect_honeypot_deep(candidate)
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
        penalty, issues = detect_honeypot_deep(candidate)
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
        penalty, issues = detect_honeypot_deep(candidate)
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
        penalty, issues = detect_honeypot_deep(candidate)
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
        penalty, issues = detect_honeypot_deep(candidate)
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
        penalty, issues = detect_honeypot_deep(candidate)
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
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("duration" in i for i in issues))

    def test_salary_range_inverted(self):
        """Check 11: min > max should flag as honeypot."""
        candidate = _make_candidate(
            redrob_signals={
                **_make_candidate()["redrob_signals"],
                "expected_salary_range_inr_lpa": {"min": 50, "max": 20},
            }
        )
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("inverted" in i for i in issues),
                        f"Expected 'inverted' in issues but got: {issues}")

    def test_salary_single_point_suspicious(self):
        """Check 11: min == max should be mildly suspicious."""
        candidate = _make_candidate(
            redrob_signals={
                **_make_candidate()["redrob_signals"],
                "expected_salary_range_inr_lpa": {"min": 30, "max": 30},
            }
        )
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("single point" in i for i in issues),
                        f"Expected 'single point' in issues but got: {issues}")

    def test_signup_after_last_active(self):
        """Check 12: last active before signup date."""
        candidate = _make_candidate(
            redrob_signals={
                **_make_candidate()["redrob_signals"],
                "signup_date": "2025-06-01",
                "last_active_date": "2024-01-01",
            }
        )
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("before signup" in i for i in issues),
                        f"Expected 'before signup' in issues but got: {issues}")

    def test_offer_acceptance_no_interviews(self):
        """Check 13: high offer rate with 0% interviews."""
        candidate = _make_candidate(
            redrob_signals={
                **_make_candidate()["redrob_signals"],
                "offer_acceptance_rate": 0.8,
                "interview_completion_rate": 0,
            }
        )
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("offer acceptance" in i for i in issues),
                        f"Expected 'offer acceptance' in issues but got: {issues}")

    def test_ghost_score(self):
        """Check 17: no verifiable internet presence."""
        candidate = _make_candidate(
            redrob_signals={
                **_make_candidate()["redrob_signals"],
                "search_appearance_30d": 0,
                "saved_by_recruiters_30d": 0,
                "github_activity_score": -1,
                "verified_email": False,
                "verified_phone": False,
            }
        )
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("internet presence" in i for i in issues),
                        f"Expected 'internet presence' in issues but got: {issues}")

    def test_no_career_history_check_2(self):
        """Check 2: No career history should be eliminated immediately."""
        candidate = _make_candidate(career_history=[])
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 0.2)
        self.assertTrue(any("no career" in i for i in issues))

    def test_fictional_company_concentration_check_3(self):
        """Check 3: >50% jobs at fictional companies."""
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "Dunder Mifflin",
                    "title": "Engineer",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 24,
                    "is_current": True,
                    "industry": "Technology",
                    "company_size": "1-10",
                    "description": "Did work.",
                },
                {
                    "company": "Initech",
                    "title": "Developer",
                    "start_date": "2018-01-01",
                    "end_date": "2019-12-31",
                    "duration_months": 24,
                    "is_current": False,
                    "industry": "Technology",
                    "company_size": "1-10",
                    "description": "Did more work.",
                },
            ]
        )
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("fictional" in i for i in issues),
                        f"Expected fictional company flag but got: {issues}")

    def test_endorsement_mismatch_check_6(self):
        """Check 6: high endorsements but very few skills."""
        candidate = _make_candidate(
            skills=[
                {"name": "Python", "proficiency": "expert", "endorsements": 100},
                {"name": "Java", "proficiency": "advanced", "endorsements": 80},
            ]
        )
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("endorsements" in i for i in issues),
                        f"Expected endorsement mismatch flag but got: {issues}")

    def test_summary_mismatch_check_10(self):
        """Check 10: Many AI keywords in summary but none in career history."""
        candidate = _make_candidate(
            summary="retrieval ranking recommendation search embeddings vector database faiss "
                    "pinecone elasticsearch production ml model deployment pytorch tensorflow "
                    "and more AI systems",
            career_history=[
                {
                    "company": "Corp",
                    "title": "Accountant",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 24,
                    "is_current": True,
                    "industry": "Finance",
                    "company_size": "1001-5000",
                    "description": "Prepared financial statements and reconciled accounts.",
                }
            ]
        )
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("summary" in i for i in issues),
                        f"Expected summary mismatch flag but got: {issues}")

    def test_skill_career_mismatch_check_14(self):
        """Check 14: 4+ AI skills not evidenced in career."""
        candidate = _make_candidate(
            current_title="Accountant",
            career_history=[
                {
                    "company": "Firm",
                    "title": "Accountant",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 24,
                    "is_current": True,
                    "industry": "Finance",
                    "company_size": "1001-5000",
                    "description": "Did accounting.",
                }
            ],
            skills=[
                {"name": "PyTorch", "proficiency": "advanced", "endorsements": 5},
                {"name": "TensorFlow", "proficiency": "advanced", "endorsements": 5},
                {"name": "Computer Vision", "proficiency": "advanced", "endorsements": 5},
                {"name": "NLP", "proficiency": "advanced", "endorsements": 5},
                {"name": "FAISS", "proficiency": "advanced", "endorsements": 5},
            ]
        )
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("not evidenced" in i for i in issues),
                        f"Expected skill-career mismatch flag but got: {issues}")

    def test_impossible_timeline_check_16(self):
        """Check 16: started working before education."""
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "Old Corp",
                    "title": "Engineer",
                    "start_date": "2005-01-01",
                    "end_date": "2008-12-31",
                    "duration_months": 48,
                    "is_current": False,
                    "industry": "Technology",
                    "company_size": "1001-5000",
                    "description": "Worked early.",
                }
            ],
            education=[
                {
                    "institution": "Univ",
                    "degree": "B.Tech",
                    "field_of_study": "CS",
                    "start_year": 2010,
                    "end_year": 2014,
                    "tier": "tier_3",
                }
            ]
        )
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("before education" in i for i in issues),
                        f"Expected timeline flag but got: {issues}")

    def test_skill_count_anomaly_check_18(self):
        """Check 18: unusually high skill count."""
        candidate = _make_candidate(
            skills=[{"name": f"Skill{i}", "proficiency": "intermediate", "endorsements": 0}
                    for i in range(25)]
        )
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("skill count" in i for i in issues),
                        f"Expected skill count flag but got: {issues}")

    def test_tempotal_order_inversion_check_19(self):
        """Check 19: end date before start date."""
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "Corp",
                    "title": "Engineer",
                    "start_date": "2020-01-01",
                    "end_date": "2019-01-01",
                    "duration_months": 0,
                    "is_current": False,
                    "industry": "Technology",
                    "company_size": "1001-5000",
                    "description": "Date error.",
                }
            ]
        )
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("end date" in i for i in issues),
                        f"Expected temporal inversion flag but got: {issues}")

    def test_future_education_end_year_check_20(self):
        """Check 20: education end year in the future."""
        candidate = _make_candidate(
            education=[
                {
                    "institution": "Future Univ",
                    "degree": "PhD",
                    "field_of_study": "CS",
                    "start_year": 2020,
                    "end_year": 2030,
                    "tier": "tier_1",
                }
            ]
        )
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertLess(penalty, 1.0)
        self.assertTrue(any("future" in i for i in issues),
                        f"Expected future education flag but got: {issues}")

    def test_new_checks_do_not_false_flag_clean(self):
        """A clean candidate should not trigger any honeypot checks."""
        candidate = _make_candidate()
        penalty, issues = detect_honeypot_deep(candidate)
        self.assertEqual(len(issues), 0,
                         f"Clean candidate triggered false positive: {issues}")


class TestNegativeSignalPenalty(unittest.TestCase):
    """Test negative_signal_penalty function."""

    def test_clean_candidate_zero_penalty(self):
        candidate = _make_candidate()
        penalty = negative_signal_penalty(candidate)
        self.assertEqual(penalty, 0.0)

    def test_aspirant_language_penalized(self):
        candidate = _make_candidate(
            summary="I've been keeping up with AI/ML at a self-learner level. "
                    "Interested in transitioning toward more AI/ML-focused work."
        )
        penalty = negative_signal_penalty(candidate)
        self.assertGreater(penalty, 0.0)


class TestSkillCareerCoherence(unittest.TestCase):
    """Test skill_career_coherence_score."""

    def test_skills_match_career(self):
        candidate = _make_candidate()
        coherence = skill_career_coherence_score(candidate)
        self.assertGreater(coherence, 0.5)

    def test_no_skills_zero(self):
        candidate = _make_candidate(skills=[])
        coherence = skill_career_coherence_score(candidate)
        self.assertEqual(coherence, 0.0)


class TestCareerProgression(unittest.TestCase):
    """Test career_progression_score."""

    def test_single_role_neutral(self):
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "Test Corp",
                    "title": "ML Engineer",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 48,
                    "is_current": True,
                    "industry": "Technology",
                    "company_size": "1001-5000",
                    "description": "Built ML models.",
                }
            ]
        )
        prog = career_progression_score(candidate)
        self.assertEqual(prog, 0.5)  # Neutral for single role

    def test_progression_toward_ai(self):
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "Old Corp",
                    "title": "Software Engineer",
                    "start_date": "2016-01-01",
                    "end_date": "2019-12-31",
                    "duration_months": 48,
                    "is_current": False,
                    "industry": "Technology",
                    "company_size": "1001-5000",
                    "description": "Built web apps.",
                },
                {
                    "company": "AI Corp",
                    "title": "ML Engineer",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 48,
                    "is_current": True,
                    "industry": "AI",
                    "company_size": "51-200",
                    "description": "Built recommendation systems.",
                },
            ]
        )
        prog = career_progression_score(candidate)
        self.assertGreater(prog, 0.5)  # Positive progression


class TestCompanyQuality(unittest.TestCase):
    """Test company_quality_score."""

    def test_no_history_zero(self):
        candidate = _make_candidate(career_history=[])
        score = company_quality_score(candidate)
        self.assertEqual(score, 0.0)

    def test_tier1_company_scores_higher(self):
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "Google",
                    "title": "Engineer",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 48,
                    "is_current": True,
                    "industry": "Technology",
                    "company_size": "10001+",
                    "description": "Worked on search.",
                }
            ]
        )
        score = company_quality_score(candidate)
        self.assertGreater(score, 0.5)


class TestSCurveTransform(unittest.TestCase):
    """Test s_curve_transform function."""

    def test_high_scores_amplified(self):
        scores = [0.75, 0.85]
        transformed = s_curve_transform(scores)
        # High scores should spread apart
        self.assertGreater(transformed[1] - transformed[0], 0.05)

    def test_empty_list(self):
        self.assertEqual(s_curve_transform([]), [])


class TestComputeTotalScore(unittest.TestCase):
    """Test the full scoring pipeline."""

    def test_strong_candidate_scores_positive(self):
        candidate = _make_candidate()
        score, penalty, issues = compute_total_score(candidate)
        self.assertGreater(score, 0.3)  # New lower weights still produce positive scores
        self.assertEqual(penalty, 1.0)

    def test_weak_candidate_scores_lower(self):
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
        self.assertLess(score, 0.7)  # Penalized


class TestGenerateReasoning(unittest.TestCase):
    """Test the generate_reasoning function."""

    def test_reasoning_contains_key_info(self):
        candidate = _make_candidate()
        score, penalty, issues = compute_total_score(candidate)
        reasoning = generate_reasoning(candidate, score, penalty, issues)
        self.assertIn("Senior Machine Learning Engineer", reasoning)
        self.assertIn("7yrs", reasoning)


class TestRareSkillDiamondScore(unittest.TestCase):
    """Test the rare_skill_diamond_score function."""

    def test_no_skills_zero(self):
        candidate = _make_candidate(skills=[])
        self.assertEqual(rare_skill_diamond_score(candidate), 0.0)

    def test_diamond_skills_boosted(self):
        candidate = _make_candidate(
            skills=[
                {"name": "Ranking", "proficiency": "advanced", "endorsements": 10},
                {"name": "Information Retrieval", "proficiency": "advanced", "endorsements": 8},
                {"name": "FAISS", "proficiency": "intermediate", "endorsements": 5},
                {"name": "Semantic Search", "proficiency": "advanced", "endorsements": 7},
                {"name": "NDCG", "proficiency": "intermediate", "endorsements": 3},
                {"name": "Recommendation System", "proficiency": "advanced", "endorsements": 6},
            ]
        )
        score = rare_skill_diamond_score(candidate)
        self.assertGreater(score, 0.5)

    def test_no_diamond_skills_low(self):
        candidate = _make_candidate(
            skills=[
                {"name": "Python", "proficiency": "expert", "endorsements": 20},
                {"name": "Docker", "proficiency": "advanced", "endorsements": 10},
                {"name": "React", "proficiency": "intermediate", "endorsements": 5},
            ]
        )
        score = rare_skill_diamond_score(candidate)
        self.assertEqual(score, 0.0)


class TestTalentPlatformBonus(unittest.TestCase):
    """Test the talent_platform_bonus function."""

    def test_no_talent_signals_zero(self):
        candidate = _make_candidate(
            summary="Just a regular ML engineer.",
            career_history=[
                {
                    "company": "Tech Corp",
                    "title": "ML Engineer",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 48,
                    "is_current": True,
                    "industry": "Technology",
                    "company_size": "1001-5000",
                    "description": "Built ML models.",
                }
            ]
        )
        self.assertEqual(talent_platform_bonus(candidate), 0.0)

    def test_hr_tech_company_bonus(self):
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "Redrob",
                    "title": "ML Engineer",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 48,
                    "is_current": True,
                    "industry": "HR Technology",
                    "company_size": "51-200",
                    "description": "Built ML systems for talent acquisition and candidate matching.",
                }
            ]
        )
        score = talent_platform_bonus(candidate)
        self.assertGreater(score, 0.5)

    def test_recruiting_keywords_in_summary(self):
        candidate = _make_candidate(
            summary="Experienced ML engineer in talent marketplace and recruitment technology."
        )
        score = talent_platform_bonus(candidate)
        self.assertGreater(score, 0.0)


class TestProfileConsistencyScore(unittest.TestCase):
    """Test the profile_consistency_score function."""

    def test_perfect_profile_returns_one(self):
        candidate = _make_candidate()
        score = profile_consistency_score(candidate)
        self.assertEqual(score, 1.0)

    def test_career_duration_mismatch_penalized(self):
        """7 years stated but career history shows only 2 years."""
        candidate = _make_candidate(
            years_of_experience=7,
            career_history=[
                {
                    "company": "Corp",
                    "title": "Engineer",
                    "start_date": "2025-01-01",
                    "end_date": None,
                    "duration_months": 18,
                    "is_current": True,
                    "industry": "Technology",
                    "company_size": "1001-5000",
                    "description": "Did work.",
                },
                {
                    "company": "Old Corp",
                    "title": "Junior Engineer",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "duration_months": 6,
                    "is_current": False,
                    "industry": "Technology",
                    "company_size": "1001-5000",
                    "description": "More work.",
                },
            ]
        )
        score = profile_consistency_score(candidate)
        self.assertLess(score, 1.0)

    def test_expert_skill_short_duration_penalized(self):
        """Expert skill with 0 months duration."""
        candidate = _make_candidate(
            skills=[
                {"name": "PyTorch", "proficiency": "expert", "endorsements": 5},
                {"name": "Python", "proficiency": "expert", "endorsements": 10},
                {"name": "Docker", "proficiency": "advanced", "endorsements": 3},
                {"name": "Kubernetes", "proficiency": "advanced", "endorsements": 2},
            ]
        )
        score = profile_consistency_score(candidate)
        self.assertLess(score, 1.0)


class TestBehavioralMultiplier(unittest.TestCase):
    """Test the behavioral_multiplier function."""

    def test_complete_signals_multiplier_above_one(self):
        candidate = _make_candidate()
        mult = behavioral_multiplier(candidate)
        self.assertGreater(mult, 1.0)  # Full signals boost above 1.0

    def test_empty_signals_neutral(self):
        candidate = _make_candidate(redrob_signals={})
        mult = behavioral_multiplier(candidate)
        self.assertEqual(mult, 1.0)  # Empty signals = neutral multiplier

    def test_no_github_still_positive(self):
        signals = _make_candidate()["redrob_signals"].copy()
        signals["github_activity_score"] = -1
        candidate = _make_candidate(redrob_signals=signals)
        mult = behavioral_multiplier(candidate)
        self.assertGreater(mult, 1.0)  # Still above 1.0 with other signals




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


class TestLatentRoleClassifier(unittest.TestCase):
    """Test the latent_role_classifier and latent_role_bonus functions."""

    def test_ml_engineer_has_latent_role_signals(self):
        candidate = _make_candidate()
        roles = latent_role_classifier(candidate)
        self.assertGreater(len(roles), 0)
        # Test candidate has production AI descriptions, should score on applied_ml

    def test_latent_role_bonus_search_retrieval(self):
        """Candidate with search/retrieval keywords gets high bonus."""
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "SearchCo",
                    "title": "Search Engineer",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 48,
                    "is_current": True,
                    "industry": "Technology",
                    "company_size": "1001-5000",
                    "description": "Built search retrieval and ranking systems. Worked on query understanding, indexing pipeline, and search relevance. Implemented semantic search and dense retrieval with embeddings. Improved NDCG and precision@k metrics through feature engineering and model optimization.",
                }
            ]
        )
        bonus = latent_role_bonus(candidate)
        self.assertGreater(bonus, 0.5)

    def test_latent_role_bonus_accountant(self):
        """Accountant should have low latent role bonus."""
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
                    "description": "Prepared financial statements and reconciled accounts. Managed month-end close process.",
                }
            ],
            skills=[]  # Clear skills to avoid false signals
        )
        bonus = latent_role_bonus(candidate)
        self.assertLess(bonus, 0.5)


class TestRecruiterAttractiveness(unittest.TestCase):
    """Test the recruiter_attractiveness_score function."""

    def test_high_saved_recruiters(self):
        """Candidate with many recruiter saves scores high."""
        candidate = _make_candidate()
        score = recruiter_attractiveness_score(candidate)
        self.assertGreater(score, 0.5)

    def test_no_signals_low(self):
        candidate = _make_candidate(redrob_signals={})
        score = recruiter_attractiveness_score(candidate)
        self.assertEqual(score, 0.0)

    def test_zero_recruiter_engagement(self):
        """Candidate with zero recruiter activity scores low."""
        candidate = _make_candidate(
            redrob_signals={
                "saved_by_recruiters_30d": 0,
                "search_appearance_30d": 0,
                "recruiter_response_rate": 0,
                "interview_completion_rate": 0,
                "profile_completeness_score": 0,
                "verified_email": False,
                "verified_phone": False,
                "linkedin_connected": False,
                "github_activity_score": -1,
            }
        )
        score = recruiter_attractiveness_score(candidate)
        self.assertLess(score, 0.3)


class TestStartupFit(unittest.TestCase):
    """Test the startup_fit_score function."""

    def test_startup_engineer_high_score(self):
        """Early-stage startup engineer should score high."""
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "StartupCo",
                    "title": "First ML Engineer",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 48,
                    "is_current": True,
                    "industry": "AI",
                    "company_size": "11-50",
                    "description": "Built the ML platform from scratch as the first engineer. Designed and architected the ranking system end-to-end. Led the development of search infrastructure. Shipped products to users and iterated based on feedback.",
                }
            ]
        )
        score = startup_fit_score(candidate)
        self.assertGreater(score, 0.5)

    def test_consultant_low_startup_fit(self):
        """Service/consulting background scores lower."""
        candidate = _make_candidate(
            career_history=[
                {
                    "company": "TCS",
                    "title": "Software Engineer",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "duration_months": 48,
                    "is_current": True,
                    "industry": "Technology",
                    "company_size": "10001+",
                    "description": "Worked on client projects. Managed deliverables and stakeholder communication.",
                }
            ]
        )
        score = startup_fit_score(candidate)
        self.assertLess(score, 0.5)

    def test_no_history_zero(self):
        candidate = _make_candidate(career_history=[])
        score = startup_fit_score(candidate)
        self.assertEqual(score, 0.0)


class TestContinuousHoneypotRisk(unittest.TestCase):
    """Test the continuous_honeypot_risk_score function."""

    def test_clean_candidate_low_risk(self):
        candidate = _make_candidate()
        risk, anomalies = continuous_honeypot_risk_score(candidate)
        self.assertLess(risk, 0.3)

    def test_expert_skills_low_experience(self):
        """Many expert skills with low experience = suspicious."""
        candidate = _make_candidate(
            years_of_experience=2,
            skills=[
                {"name": f"Skill{i}", "proficiency": "expert", "endorsements": 20}
                for i in range(6)
            ]
        )
        risk, anomalies = continuous_honeypot_risk_score(candidate)
        self.assertGreater(risk, 0.0)

    def test_high_skill_count_anomaly(self):
        """Unusually high skill count triggers anomaly."""
        candidate = _make_candidate(
            skills=[{"name": f"Skill{i}", "proficiency": "intermediate", "endorsements": 0}
                    for i in range(25)]
        )
        risk, anomalies = continuous_honeypot_risk_score(candidate)
        self.assertGreater(risk, 0.0)
        self.assertTrue(any("skill count" in a for a in anomalies))


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
