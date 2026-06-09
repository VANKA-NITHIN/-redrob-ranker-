"""
Deep EDA - Redrob Hackathon Candidate Dataset
Analyzes 10K candidates for model improvement opportunities.
"""
import json
import os
from collections import Counter, defaultdict

DATA_DIR = "data"

batch = []
with open(os.path.join(DATA_DIR, "candidates.jsonl"), "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= 10000:
            break
        batch.append(json.loads(line.strip()))

print(f"=== Analyzed {len(batch)} candidates ===\n")

# --- Title Distribution ---
titles = Counter()
for c in batch:
    t = c["profile"]["current_title"].lower()
    titles[t] += 1

print("=== Top 30 Current Titles ===")
for t, cnt in titles.most_common(30):
    print(f"  {t}: {cnt}")

# --- Experience Distribution ---
years = [c["profile"]["years_of_experience"] for c in batch]
print(f"\n=== Experience Distribution ===")
print(f"  Min: {min(years):.1f}, Max: {max(years):.1f}, Mean: {sum(years)/len(years):.1f}")
yr_buckets = Counter()
for y in years:
    bucket = int(y // 2) * 2
    yr_buckets[f"{bucket}-{bucket+2}"] += 1
for b in sorted(yr_buckets.keys(), key=lambda x: int(x.split("-")[0])):
    print(f"  {b}: {yr_buckets[b]}")

# --- Skills Analysis ---
print("\n=== Top 40 Skills ===")
all_skills = Counter()
for c in batch:
    for s in c.get("skills", []):
        all_skills[s["name"]] += 1
for s, cnt in all_skills.most_common(40):
    print(f"  {s}: {cnt}")

# Skills per candidate
skill_counts = [len(c.get("skills", [])) for c in batch]
print(f"\n=== Skills Per Candidate ===")
print(f"  Min: {min(skill_counts)}, Max: {max(skill_counts)}, Mean: {sum(skill_counts)/len(skill_counts):.1f}")

# Career history length
hist_lens = [len(c.get("career_history", [])) for c in batch]
print(f"\n=== Career History Length ===")
print(f"  Min: {min(hist_lens)}, Max: {max(hist_lens)}, Mean: {sum(hist_lens)/len(hist_lens):.1f}")
hist_buckets = Counter(hist_lens)
for b in sorted(hist_buckets.keys()):
    print(f"  {b} jobs: {hist_buckets[b]}")

# --- Country Distribution ---
countries = Counter()
for c in batch:
    countries[c["profile"]["country"]] += 1
print(f"\n=== Country Distribution ===")
for ct, cnt in countries.most_common(15):
    print(f"  {ct}: {cnt}")

# --- Redrob Signals ---
print(f"\n=== Redrob Signals (10K sample) ===")
# Recruiter response rate
resp_rates = [c["redrob_signals"].get("recruiter_response_rate", -1)
              for c in batch if c["redrob_signals"].get("recruiter_response_rate", -1) >= 0]
if resp_rates:
    print(f"  Response rate: mean={sum(resp_rates)/len(resp_rates):.3f}, n={len(resp_rates)}")

# GitHub activity
github_scores = [c["redrob_signals"].get("github_activity_score", -1)
                 for c in batch if c["redrob_signals"].get("github_activity_score", -1) >= 0]
print(f"  GitHub linked: {len(github_scores)}/{len(batch)} ({len(github_scores)*100/len(batch):.1f}%)")
if github_scores:
    print(f"  GitHub mean score: {sum(github_scores)/len(github_scores):.1f}")

# Notice period
notice_periods = [c["redrob_signals"].get("notice_period_days", 90) for c in batch]
if notice_periods:
    print(f"  Notice period: mean={sum(notice_periods)/len(notice_periods):.1f}d")

# Profile completeness
completeness = [c["redrob_signals"].get("profile_completeness_score", 0) for c in batch]
if completeness:
    print(f"  Profile completeness: mean={sum(completeness)/len(completeness):.1f}")

# Open to work
open_to_work = sum(1 for c in batch if c["redrob_signals"].get("open_to_work_flag", False))
print(f"  Open to work: {open_to_work}/{len(batch)} ({open_to_work*100/len(batch):.1f}%)")

# Willing to relocate
willing = sum(1 for c in batch if c["redrob_signals"].get("willing_to_relocate", False))
print(f"  Willing to relocate: {willing}/{len(batch)} ({willing*100/len(batch):.1f}%)")

# Saved by recruiters
saved = [c["redrob_signals"].get("saved_by_recruiters_30d", 0) for c in batch]
print(f"  Saved by recruiters 30d: mean={sum(saved)/len(saved):.1f}, max={max(saved)}")

# Search appearance
search_app = [c["redrob_signals"].get("search_appearance_30d", 0) for c in batch]
print(f"  Search appearance 30d: mean={sum(search_app)/len(search_app):.1f}, max={max(search_app)}")

# --- Education ---
edu_counts = [len(c.get("education", [])) for c in batch]
no_edu = sum(1 for ec in edu_counts if ec == 0)
print(f"\n=== Education ===")
print(f"  No education listed: {no_edu}/{len(batch)} ({no_edu*100/len(batch):.1f}%)")
print(f"  Mean educations: {sum(edu_counts)/len(edu_counts):.1f}")

# Check how many have Tier 1 education
tiers = []
fields = []
for c in batch:
    for e in c.get("education", []):
        tiers.append(e.get("tier", "unknown"))
        fields.append(e.get("field_of_study", "").lower())
tier_counts = Counter(tiers)
print(f"  Education tiers: {dict(tier_counts.most_common())}")
relevant_fields = sum(1 for f in fields if any(rf in f for rf in [
    "artificial intelligence", "machine learning", "data science",
    "computer science", "computer engineering", "software engineering",
    "statistics", "mathematics"
]))
print(f"  Relevant fields of study: {relevant_fields}/{len(fields)} ({relevant_fields*100/len(fields):.1f}%)")

# --- Honeypot Analysis ---
print(f"\n=== Deep Honeypot Analysis ===")

overlap_count = 0
timeline_issues = 0
ai_skills_no_bg = 0
total_flagged = 0
flag_details = []

PRODUCTION_AI_KEYWORDS = [
    "retrieval", "information retrieval", "retrieval augmented",
    "ranking", "learning to rank", "reranking", "rank", "ranker",
    "recommendation", "recommender", "search relevance",
    "semantic search", "vector search", "neural search",
    "embeddings", "embedding", "vector database", "vector db",
    "faiss", "pinecone", "qdrant", "weaviate", "chroma", "milvus",
    "elasticsearch", "opensearch", "solr",
    "ndcg", "mrr", "map", "precision@k", "recall@k",
    "evaluation", "a/b testing", "online evaluation",
    "production ml", "model deployment", "model serving",
    "pytorch", "tensorflow", "transformers",
    "python", "ml system", "ml pipeline",
]

AI_CORE_SKILLS = {
    "NLP", "Fine-tuning LLMs", "LLM", "Large Language Models",
    "Object Detection", "Image Classification", "Computer Vision",
    "Speech Recognition", "TTS", "GANs", "Deep Learning",
    "Machine Learning", "Transfer Learning", "Reinforcement Learning",
    "Recommendation System", "Ranking", "Learning to Rank",
    "Information Retrieval", "Semantic Search", "Vector Search",
    "Embeddings", "RAG", "Retrieval Augmented Generation",
    "Neural Networks", "Transformer", "BERT", "GPT",
    "PyTorch", "TensorFlow", "Keras", "scikit-learn", "JAX",
    "MLflow", "Weights & Biases", "WandB",
}

for c in batch:
    flags = []
    yoe = c["profile"]["years_of_experience"]
    edus = c.get("education", [])
    skills = c.get("skills", [])
    history = c.get("career_history", [])
    summary = (c["profile"].get("summary") or "").lower()

    # Check 1: Timeline inconsistency
    if edus:
        latest_end = max(e.get("end_year", 0) or 0 for e in edus)
        if latest_end > 2020 and yoe >= 10:
            flags.append(f"Grad={latest_end}, exp={yoe}yrs")
            timeline_issues += 1

    # Check 2: Overlapping education at different institutions
    if len(edus) >= 2:
        for i in range(len(edus)):
            for j in range(i + 1, len(edus)):
                if edus[i].get("institution") != edus[j].get("institution"):
                    s1, e1 = edus[i].get("start_year", 0) or 0, edus[i].get("end_year", 0) or 0
                    s2, e2 = edus[j].get("start_year", 0) or 0, edus[j].get("end_year", 0) or 0
                    if s1 and s2 and e1 and e2 and not (e1 <= s2 or e2 <= s1):
                        flags.append(f"Overlap edu")
                        overlap_count += 1
                        break

    # Check 3: Prod AI keywords in summary but no career history
    prod_in_summary = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in summary)
    if prod_in_summary >= 8:
        hist_desc = " ".join([(h.get("description") or "").lower() for h in history])
        prod_in_hist = sum(1 for kw in PRODUCTION_AI_KEYWORDS if kw in hist_desc)
        if prod_in_hist == 0:
            flags.append(f"Summary has {prod_in_summary} prod AI keywords but no career history matches")
            ai_skills_no_bg += 1

    # Check 4: AI skills but no AI education or role
    skill_names = set(s["name"] for s in skills)
    ai_overlap = len(skill_names & AI_CORE_SKILLS)
    if ai_overlap >= 4:
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
        if not has_ai_edu and not has_ai_role:
            flags.append(f"AI skills ({ai_overlap}) but no AI edu/role")

    # Check 5: Career history months exceed stated experience
    if len(history) >= 2:
        total_months = sum(h.get("duration_months", 0) or 0 for h in history)
        total_years_from_hist = total_months / 12
        if total_years_from_hist > yoe + 3 and yoe > 0:
            flags.append(f"Hist={total_years_from_hist:.0f}yrs > stated={yoe}yrs")

    if flags:
        total_flagged += 1
        if total_flagged <= 30:
            print(f"  {c['candidate_id']}: {'; '.join(flags[:3])}")

print(f"\n=== Honeypot Summary ===")
print(f"  Total flagged in 10K: {total_flagged}")
print(f"  Timeline inconsistencies: {timeline_issues}")
print(f"  Overlapping education: {overlap_count}")
print(f"  AI skills without background: {ai_skills_no_bg}")

# Check for candidates with NO career history
no_history = sum(1 for c in batch if not c.get("career_history"))
print(f"  No career history: {no_history}")

# Check for candidates with excessively long descriptions
long_desc = 0
for c in batch:
    for h in c.get("career_history", []):
        desc = h.get("description", "")
        if desc and len(desc) > 2000:
            long_desc += 1
            break
print(f"  Excessively long descriptions (>2000 chars): {long_desc}")

# Career history and skill correlation
print(f"\n=== Cross-Correlation Analysis ===")
hist_no_skills = sum(1 for c in batch if c.get("career_history") and not c.get("skills"))
skills_no_hist = sum(1 for c in batch if c.get("skills") and not c.get("career_history"))
print(f"  Has career history but no skills: {hist_no_skills}")
print(f"  Has skills but no career history: {skills_no_hist}")

# AI title vs AI skills mismatch
ai_titles = {"ai engineer", "ml engineer", "machine learning engineer",
             "applied scientist", "research scientist", "data scientist",
             "nlp engineer", "deep learning engineer", "ai architect"}
has_ai_title_no_skills = 0
for c in batch:
    title = c["profile"]["current_title"].lower()
    if title in ai_titles:
        skill_names = set(s["name"] for s in c.get("skills", []))
        ai_overlap = len(skill_names & AI_CORE_SKILLS)
        if ai_overlap == 0:
            has_ai_title_no_skills += 1
print(f"  AI title but zero AI skills: {has_ai_title_no_skills}")
