"""
Test Cfg9 optimal weights from parameter sweep on the full 100K dataset.
Cfg9: C=0.35 P=0.17 R=0.15 B=0.12 E=0.12 S=0.02 Ed=0.07
"""
import sys
import os
import time
import subprocess

sys.path.insert(0, ".")

# Apply Cfg9 weights
import config as cfg
cfg.WEIGHTS["career_relevance"] = 0.35
cfg.WEIGHTS["production_ai_evidence"] = 0.17
cfg.WEIGHTS["role_relevance"] = 0.15
cfg.WEIGHTS["behavioral_signals"] = 0.12
cfg.WEIGHTS["experience_fit"] = 0.12
cfg.WEIGHTS["skills_match"] = 0.02
cfg.WEIGHTS["education_score"] = 0.07

from ranker import process_candidates, load_jsonl_line_by_line

print("Running full pipeline with Cfg9 weights:")
print("  C=0.35 P=0.17 R=0.15 B=0.12 E=0.12 S=0.02 Ed=0.07")
print("=" * 60)

start = time.time()
gen = load_jsonl_line_by_line("data/candidates.jsonl")
rankings = process_candidates(gen)
elapsed = time.time() - start

# Write submission
os.makedirs("output", exist_ok=True)
with open("output/submission_cfg9.csv", "w", encoding="utf-8") as f:
    f.write("candidate_id,rank,score,reasoning\n")
    for rank, (score, cid, reasoning, hon_penalty, hon_issues) in enumerate(rankings, 1):
        score_str = f"{score:.4f}"
        reasoning_escaped = reasoning.replace('"', '""')
        f.write(f'{cid},{rank},{score_str},"{reasoning_escaped}"\n')

# Validate
result = subprocess.run(
    ["python", "data/validate_submission.py", "output/submission_cfg9.csv"],
    capture_output=True, text=True
)
print(f"Validation: {result.stdout.strip()}")
print(f"Time: {elapsed:.1f}s")
print(f"Top score: {rankings[0][0]:.4f}")
print(f"Bottom score: {rankings[-1][0]:.4f}")
honeypots = sum(1 for h in rankings if h[3] < 0.5)
print(f"Honeypots in top 100: {honeypots}")

# Show top 3
print("\n=== Top 3 ===")
for i in range(3):
    s, cid, reason, pen, issues = rankings[i]
    print(f"  {i+1}. {cid} (score={s:.4f}, pen={pen:.2f})")
    print(f"     {reason[:150]}")
