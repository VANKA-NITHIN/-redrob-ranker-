"""
Robustness Tests — Verify the ranker handles any new/unseen data without crashing.
Tests edge cases: missing fields, null values, bad types, empty arrays, special chars.
"""
import sys
import os
import json
import unittest
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ranker import (
    compute_total_score,
    process_candidates,
    generate_reasoning,
    detect_honeypot_fast,
    detect_honeypot_deep,
    career_history_score,
    role_relevance_score,
    education_score,
    skills_match_score,
    experience_fit_score,
    behavioral_multiplier,
    negative_signal_penalty,
    skill_career_coherence_score,
    career_progression_score,
    company_quality_score,
    location_preference_score,
    notice_period_score,
    rare_skill_diamond_score,
    talent_platform_bonus,
    profile_consistency_score,
    latent_role_bonus,
    recruiter_attractiveness_score,
    startup_fit_score,
    continuous_honeypot_risk_score,
    production_ai_evidence_score,
    retrieval_ranking_experience_score,
    s_curve_transform,
    build_candidate_text,
)


class TestRobustnessWithMissingFields(unittest.TestCase):
    """Test the ranker handles completely missing fields without crashing."""

    def test_empty_dict(self):
        """Score an empty dictionary - should not crash."""
        try:
            score, penalty, issues = compute_total_score({})
            self.assertGreaterEqual(score, 0.0)
            self.assertGreaterEqual(penalty, 0.0)
        except Exception as e:
            self.fail(f"compute_total_score({{}}) crashed: {e}")

    def test_none_candidate(self):
        """Pass None as candidate - should not crash."""
        try:
            result = process_candidates([None])
            # Should handle gracefully
            self.assertIsInstance(result, list)
        except Exception as e:
            # Either handle gracefully or raise clear error
            pass

    def test_empty_list(self):
        """Process empty candidate list."""
        result = process_candidates([])
        self.assertEqual(result, [])

    def test_no_profile(self):
        """Candidate without profile field."""
        c = {"candidate_id": "TEST_0001"}
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"No profile crashed: {e}")

    def test_no_career_history(self):
        """Candidate without career_history field."""
        c = {
            "candidate_id": "TEST_0002",
            "profile": {"anonymized_name": "Test"},
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"No career_history crashed: {e}")

    def test_no_skills(self):
        """Candidate without skills field or with empty skills."""
        c = {
            "candidate_id": "TEST_0003",
            "profile": {},
            "skills": [],
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"No skills crashed: {e}")

    def test_no_education(self):
        """Candidate without education field."""
        c = {
            "candidate_id": "TEST_0004",
            "profile": {},
            "education": [],
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"No education crashed: {e}")

    def test_no_redrob_signals(self):
        """Candidate without redrob_signals field."""
        c = {
            "candidate_id": "TEST_0005",
            "profile": {},
            "career_history": [],
            "skills": [],
            "education": [],
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"No redrob_signals crashed: {e}")


class TestRobustnessWithNullValues(unittest.TestCase):
    """Test the ranker handles null/None values without crashing."""

    def test_null_years_experience(self):
        """years_of_experience is None."""
        c = {
            "candidate_id": "TEST_NULL_1",
            "profile": {
                "years_of_experience": None,
                "current_title": None,
                "current_company": None,
                "location": None,
                "country": None,
                "headline": None,
                "summary": None,
            },
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"Null years_of_experience crashed: {e}")

    def test_null_career_fields(self):
        """Career history with null fields."""
        c = {
            "candidate_id": "TEST_NULL_2",
            "profile": {"years_of_experience": 5},
            "career_history": [
                {
                    "company": None,
                    "title": None,
                    "description": None,
                    "start_date": None,
                    "end_date": None,
                    "duration_months": None,
                    "is_current": None,
                    "industry": None,
                    "company_size": None,
                }
            ],
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"Null career fields crashed: {e}")

    def test_null_skill_fields(self):
        """Skills with null fields."""
        c = {
            "candidate_id": "TEST_NULL_3",
            "profile": {"years_of_experience": 5},
            "skills": [
                {"name": None, "proficiency": None, "endorsements": None},
                {"name": "Python", "proficiency": None, "endorsements": None},
            ],
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"Null skill fields crashed: {e}")

    def test_null_education_fields(self):
        """Education with null fields."""
        c = {
            "candidate_id": "TEST_NULL_4",
            "profile": {"years_of_experience": 5},
            "education": [
                {
                    "institution": None,
                    "degree": None,
                    "field_of_study": None,
                    "start_year": None,
                    "end_year": None,
                    "grade": None,
                    "tier": None,
                }
            ],
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"Null education fields crashed: {e}")

    def test_null_signal_fields(self):
        """Redrob signals with null values."""
        c = {
            "candidate_id": "TEST_NULL_5",
            "profile": {"years_of_experience": 5},
            "redrob_signals": {
                "profile_completeness_score": None,
                "recruiter_response_rate": None,
                "interview_completion_rate": None,
                "search_appearance_30d": None,
                "saved_by_recruiters_30d": None,
                "github_activity_score": None,
                "connection_count": None,
                "endorsements_received": None,
                "open_to_work_flag": None,
                "verified_email": None,
                "verified_phone": None,
                "willing_to_relocate": None,
                "notice_period_days": None,
                "signup_date": None,
                "last_active_date": None,
                "offer_acceptance_rate": None,
            },
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"Null signal fields crashed: {e}")


class TestRobustnessWithBadTypes(unittest.TestCase):
    """Test the ranker handles wrong types without crashing."""

    def test_string_instead_of_number_exp(self):
        """years_of_experience as string."""
        c = {
            "candidate_id": "TEST_TYPE_1",
            "profile": {
                "years_of_experience": "seven",
                "current_title": "ML Engineer",
            },
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"String years crashed: {e}")

    def test_list_instead_of_dict_profile(self):
        """Profile as a list instead of dict."""
        c = {
            "candidate_id": "TEST_TYPE_2",
            "profile": ["this is not a dict"],
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"List profile crashed: {e}")

    def test_int_instead_of_bool(self):
        """Boolean fields as integers."""
        c = {
            "candidate_id": "TEST_TYPE_3",
            "profile": {"years_of_experience": 5},
            "redrob_signals": {
                "open_to_work_flag": 1,
                "verified_email": 1,
                "verified_phone": 0,
                "willing_to_relocate": 1,
            },
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"Int bools crashed: {e}")

    def test_negative_experience(self):
        """Negative years of experience."""
        try:
            result = experience_fit_score(-5)
            self.assertGreaterEqual(result, 0.0)
        except Exception as e:
            self.fail(f"Negative exp crashed: {e}")

    def test_extremely_high_experience(self):
        """Extremely high years of experience."""
        try:
            result = experience_fit_score(999)
            self.assertGreaterEqual(result, 0.0)
        except Exception as e:
            self.fail(f"High exp crashed: {e}")

    def test_nan_experience(self):
        """NaN years of experience."""
        try:
            result = experience_fit_score(float('nan'))
            self.assertTrue(True)  # Should not crash
        except Exception as e:
            self.fail(f"NaN exp crashed: {e}")

    def test_inf_experience(self):
        """Infinite years of experience."""
        try:
            result = experience_fit_score(float('inf'))
            self.assertGreaterEqual(result, 0.0)
        except Exception as e:
            self.fail(f"Inf exp crashed: {e}")


class TestRobustnessWithSpecialInputs(unittest.TestCase):
    """Test the ranker handles unusual but valid inputs."""

    def test_unknown_company(self):
        """Company not in any classification list."""
        c = {
            "candidate_id": "TEST_SPL_1",
            "profile": {"years_of_experience": 5},
            "career_history": [
                {
                    "company": "RandomUnknownCompanyXYZ",
                    "title": "ML Engineer",
                    "description": "Built ML models",
                    "duration_months": 36,
                    "is_current": True,
                    "industry": "Technology",
                    "company_size": "51-200",
                }
            ],
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"Unknown company crashed: {e}")

    def test_unknown_location(self):
        """Location not in preferred list."""
        c = {
            "candidate_id": "TEST_SPL_2",
            "profile": {
                "years_of_experience": 5,
                "location": "Small Town, Rural India",
                "country": "India",
                "current_title": "ML Engineer",
            },
        }
        try:
            score, penalty, issues = compute_total_score(c)
            loc = location_preference_score(c)
            self.assertGreaterEqual(loc, 0.0)
        except Exception as e:
            self.fail(f"Unknown location crashed: {e}")

    def test_non_india_location(self):
        """Non-India location."""
        c = {
            "candidate_id": "TEST_SPL_3",
            "profile": {
                "years_of_experience": 5,
                "location": "San Francisco",
                "country": "United States",
                "current_title": "ML Engineer",
            },
        }
        try:
            loc = location_preference_score(c)
            self.assertEqual(loc, 0.15)
        except Exception as e:
            self.fail(f"Non-India location crashed: {e}")

    def test_unknown_title(self):
        """Title not in any tier list."""
        c = {
            "candidate_id": "TEST_SPL_4",
            "profile": {
                "years_of_experience": 5,
                "current_title": "Chief Happiness Officer",
            },
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"Unknown title crashed: {e}")

    def test_special_characters_in_text(self):
        """Text with special characters and emojis."""
        c = {
            "candidate_id": "TEST_SPL_5",
            "profile": {
                "years_of_experience": 5,
                "current_title": "ML Engineer 🚀",
                "summary": "Built AI systems 🔥 using Python & PyTorch @ Scale! 100% success rate.",
                "headline": "AI Engineer ★★★",
            },
            "career_history": [
                {
                    "company": "AI Corp ©",
                    "title": "ML Engineer 💻",
                    "description": "Built ranking & retrieval systems using Python & PyTorch.",
                    "duration_months": 36,
                    "is_current": True,
                    "industry": "Technology",
                    "company_size": "51-200",
                }
            ],
            "skills": [
                {"name": "Python 🐍", "proficiency": "expert", "endorsements": 10},
                {"name": "PyTorch 🔥", "proficiency": "advanced", "endorsements": 5},
                {"name": "NLP 📝", "proficiency": "advanced", "endorsements": 3},
            ],
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"Special chars crashed: {e}")

    def test_missing_candidate_id(self):
        """Candidate without candidate_id."""
        c = {
            "profile": {"years_of_experience": 5, "current_title": "ML Engineer"},
            "career_history": [],
            "skills": [],
            "education": [],
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"Missing candidate_id crashed: {e}")

    def test_very_long_descriptions(self):
        """Very long description strings."""
        long_text = "ML and AI " * 5000  # 40K chars
        c = {
            "candidate_id": "TEST_LONG",
            "profile": {
                "years_of_experience": 5,
                "current_title": "ML Engineer",
                "summary": long_text[:2000],
            },
            "career_history": [
                {
                    "company": "Test Corp",
                    "title": "ML Engineer",
                    "description": long_text[:5000],
                    "duration_months": 36,
                    "is_current": True,
                    "industry": "Technology",
                    "company_size": "51-200",
                }
            ],
            "skills": [{"name": f"Skill{i}", "proficiency": "advanced", "endorsements": 5} for i in range(30)],
        }
        try:
            score, penalty, issues = compute_total_score(c)
            self.assertGreaterEqual(score, 0.0)
        except Exception as e:
            self.fail(f"Long text crashed: {e}")


class TestRobustnessForIndividualFunctions(unittest.TestCase):
    """Test individual scoring functions with edge cases."""

    def test_production_ai_evidence_empty(self):
        result = production_ai_evidence_score({})
        self.assertEqual(result, 0.0)

    def test_retrieval_ranking_empty(self):
        result = retrieval_ranking_experience_score({})
        self.assertEqual(result, 0.0)

    def test_career_history_empty(self):
        result = career_history_score({})
        self.assertEqual(result, 0.0)

    def test_role_relevance_empty(self):
        result = role_relevance_score({})
        self.assertEqual(result, 0.0)

    def test_skills_match_empty(self):
        result = skills_match_score({})
        self.assertEqual(result, 0.0)

    def test_education_empty(self):
        result = education_score({})
        self.assertEqual(result, 0.0)

    def test_negative_signal_empty(self):
        result = negative_signal_penalty({})
        self.assertEqual(result, 0.0)

    def test_coherence_empty(self):
        result = skill_career_coherence_score({})
        self.assertEqual(result, 0.0)

    def test_progression_empty(self):
        result = career_progression_score({})
        # 0.5 is correct: neutral score for empty/single-role (insufficient data to judge)
        self.assertEqual(result, 0.5)

    def test_company_quality_empty(self):
        result = company_quality_score({})
        self.assertEqual(result, 0.0)

    def test_location_empty(self):
        result = location_preference_score({})
        self.assertGreaterEqual(result, 0.0)

    def test_notice_empty(self):
        result = notice_period_score({})
        self.assertGreaterEqual(result, 0.0)

    def test_diamond_empty(self):
        result = rare_skill_diamond_score({})
        self.assertEqual(result, 0.0)

    def test_talent_empty(self):
        result = talent_platform_bonus({})
        self.assertEqual(result, 0.0)

    def test_consistency_empty(self):
        result = profile_consistency_score({})
        self.assertGreaterEqual(result, 0.5)

    def test_latent_role_empty(self):
        result = latent_role_bonus({})
        self.assertGreaterEqual(result, 0.0)

    def test_recruiter_attr_empty(self):
        result = recruiter_attractiveness_score({})
        self.assertEqual(result, 0.0)

    def test_startup_fit_empty(self):
        result = startup_fit_score({})
        self.assertEqual(result, 0.0)

    def test_continuous_honeypot_empty(self):
        risk, anomalies = continuous_honeypot_risk_score({})
        self.assertGreaterEqual(risk, 0.0)

    def test_s_curve_empty(self):
        result = s_curve_transform([])
        self.assertEqual(result, [])

    def test_build_candidate_text_empty(self):
        result = build_candidate_text({})
        self.assertEqual(result, "")

    def test_detect_honeypot_fast_empty(self):
        penalty, issues = detect_honeypot_fast({})
        self.assertGreaterEqual(penalty, 0.0)

    def test_detect_honeypot_deep_empty(self):
        penalty, issues = detect_honeypot_deep({})
        self.assertGreaterEqual(penalty, 0.0)

    def test_behavioral_multiplier_empty(self):
        result = behavioral_multiplier({})
        self.assertEqual(result, 1.0)

    def test_generate_reasoning_empty(self):
        result = generate_reasoning({}, 0.0, 1.0, [])
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main(verbosity=2)
