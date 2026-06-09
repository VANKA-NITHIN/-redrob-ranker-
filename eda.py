"""
EDA - Redrob Hackathon Candidate Data
Explores sample data, distributions, and identifies honeypot patterns.
"""
import json
import os
from collections import Counter, defaultdict

DATA_DIR = "data"

# Load sample data
with open(os.path.join(DATA_DIR, "sample_candidates.json"), "r") as f:
    samples = json.load(f)

print(f"=== Sample candidates: {len(samples)} ===\n")

# --- Basic stats ---
years_exp = [c["profile"]["years_of_experience"] for c in samples]
locations = [c["profile"]["location"] for c in samples]
countries = [c["profile"]["country"] for c in samples]
titles = [c["profile"]["current_title"] for c in samples]
industries = [c["profile"]["current_industry"] for c in samples]

print(f"Years of experience: min={min(years_exp):.1f}, max={max(years_exp):.1f}, avg={sum(years_exp)/len(years_exp):.1f}")
print(f"\nCountries: {dict(Counter(countries).most_common())}")
print(f"\nLocations: {dict(Counter(locations).most_common(10))}")
print(f"\nCurrent Titles (top 15): {dict(Counter(titles).most_common(15))}")
print(f"\nIndustries (top 10): {dict(Counter(industries).most_common(10))}")

# --- Skills analysis ---
all_skills = []
for c in samples:
    for s in c.get("skills", []):
        all_skills.append((s["name"], s["proficiency"], s["endorsements"]))

skill_counts = Counter(s[0] for s in all_skills)
print(f"\n--- Skills (top 30) ---")
for skill, count in skill_counts.most_common(30):
    endorsements = sum(s[2] for s in all_skills if s[0] == skill)
    print(f"  {skill}: {count} candidates, {endorsements} total endorsements")

# --- Education tiers ---
tiers = [e["tier"] for c in samples for e in c.get("education", [])]
print(f"\n--- Education Tiers ---")
for tier, count in Counter(tiers).most_common():
    print(f"  {tier}: {count}")
    
fields = [e["field_of_study"] for c in samples for e in c.get("education", [])]
print(f"\n--- Fields of Study (top 20) ---")
for f, count in Counter(fields).most_common(20):
    print(f"  {f}: {count}")

# --- Redrob signals ---
print(f"\n--- Redrob Signals Overview ---")
signal_keys = [
    "profile_completeness_score", "open_to_work_flag", "recruiter_response_rate",
    "interview_completion_rate", "offer_acceptance_rate", "github_activity_score",
    "connection_count", "willing_to_relocate", "verified_email", "verified_phone"
]
for key in signal_keys:
    vals = [c["redrob_signals"].get(key) for c in samples]
    numeric_vals = [v for v in vals if isinstance(v, (int, float)) and v != -1]
    if numeric_vals:
        print(f"  {key}: min={min(numeric_vals)}, max={max(numeric_vals)}, avg={sum(numeric_vals)/len(numeric_vals):.2f}, null/na={sum(1 for v in vals if v == -1 or v is None)}")
    elif all(isinstance(v, bool) for v in vals if v is not None):
        print(f"  {key}: True={sum(1 for v in vals if v)}, False={sum(1 for v in vals if not v)}")
    else:
        print(f"  {key}: {dict(Counter(str(v) for v in vals).most_common(5))}")

# --- Career history depth ---
hist_lengths = [len(c.get("career_history", [])) for c in samples]
print(f"\nCareer history entries: min={min(hist_lengths)}, max={max(hist_lengths)}, avg={sum(hist_lengths)/len(hist_lengths):.1f}")

# --- Skill count distribution ---
skill_counts_per_cand = [len(c.get("skills", [])) for c in samples]
print(f"Skills per candidate: min={min(skill_counts_per_cand)}, max={max(skill_counts_per_cand)}, avg={sum(skill_counts_per_cand)/len(skill_counts_per_cand):.1f}")

# --- Honeypot exploration: Look for impossible/inconsistent profiles ---
print(f"\n=== HONEYPOT ANALYSIS ===")
# Check: very young age with high experience (e.g., graduated 2024 but 15+ yrs exp)
for c in samples:
    issues = []
    yoe = c["profile"]["years_of_experience"]
    edus = c.get("education", [])
    
    if edus:
        latest_edu_end = max(e.get("end_year", 0) or 0 for e in edus)
        # If they graduated recently but have too many years of experience
        if latest_edu_end > 0 and yoe > 0 and (2026 - latest_edu_end) < (yoe - 2):
            issues.append(f"Graduated {latest_edu_end} but has {yoe} yrs exp")
    
    # Multiple educations at same time
    edu_years = [(e.get("start_year", 0), e.get("end_year", 0)) for e in edus]
    for i, (s1, e1) in enumerate(edu_years):
        for j, (s2, e2) in enumerate(edu_years):
            if i < j and s1 and s2 and e1 and e2:
                if not (e1 < s2 or e2 < s1):  # overlapping
                    # If they overlap AND are different degree levels
                    if edus[i]["institution"] != edus[j]["institution"]:
                        issues.append(f"Overlapping education: {edus[i]['degree']}@{edus[i]['institution']}({s1}-{e1}) and {edus[j]['degree']}@{edus[j]['institution']}({s2}-{e2})")
                        break
    
    # Check if AI/ML skills but no relevant education or experience
    ai_skills = {"NLP", "Fine-tuning LLMs", "Object Detection", "Image Classification", 
                 "Speech Recognition", "GANs", "LLM", "Transformer", "Deep Learning",
                 "Machine Learning", "AI", "Computer Vision", "BERT", "GPT"}
    has_ai = any(s["name"] in ai_skills for s in c.get("skills", []))
    has_ai_edu = any("intelligence" in (e.get("field_of_study", "") or "").lower() or 
                     "learning" in (e.get("field_of_study", "") or "").lower() or
                     "data science" in (e.get("field_of_study", "") or "").lower()
                     for e in edus)
    has_ai_role = any("ai" in (h.get("title", "") or "").lower() or 
                      "ml" in (h.get("title", "") or "").lower() or
                      "machine learning" in (h.get("title", "") or "").lower()
                      for h in c.get("career_history", []))
    
    if has_ai and not has_ai_edu and not has_ai_role:
        issues.append(f"Has AI/ML skills but no AI education or role")

    if issues:
        print(f"\n  {c['candidate_id']} ({c['profile']['anonymized_name']}):")
        for iss in issues:
            print(f"    - {iss}")

# Check the full dataset size
print(f"\n=== FULL DATASET ===")
total_lines = 0
with open(os.path.join(DATA_DIR, "candidates.jsonl"), "r") as f:
    for _ in f:
        total_lines += 1
print(f"Total candidates in full dataset: {total_lines}")
print(f"File size: {os.path.getsize(os.path.join(DATA_DIR, 'candidates.jsonl')) / 1e6:.0f} MB")
