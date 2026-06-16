"""
Parameter Sweep — Find optimal feature weights for the ranker.
Tests different weight configurations on sample data and reports top candidates.
"""
import json
import os
import sys
import itertools
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ranker import compute_total_score, process_candidates

SAMPLE_PATH = os.path.join("data", "sample_candidates.json")


def load_samples():
    with open(SAMPLE_PATH, "r") as f:
        return json.load(f)


# Define weight configurations to test
SWEEP_CONFIGS = [
    # (career, role, prod_ai, retrieval_ranking, behavioral, experience, skills, education, location, notice)
    # Total must sum to ~1.0 (location & notice are bonuses on top)
    #
    # Current config (baseline)
    (35, 20, 14, 10, 10, 5, 3, 3, 3, 2),
    # Career-heavy: prioritize title/industry match
    (38, 18, 14, 10, 9, 4, 2, 2, 2, 1),
    (40, 17, 13, 10, 9, 4, 2, 2, 2, 1),
    # Role-heavy: surface AI titles aggressively
    (33, 24, 13, 10, 9, 4, 2, 2, 2, 1),
    (32, 25, 13, 10, 9, 4, 2, 2, 2, 1),
    # Prod-AI heavy: favor production ML experience
    (33, 18, 18, 12, 9, 4, 2, 2, 1, 1),
    (32, 17, 20, 12, 9, 4, 2, 2, 1, 1),
    # Retrieval-Ranking heavy: JD's #1 ask
    (33, 18, 12, 15, 10, 4, 3, 3, 2, 2),
    (31, 17, 12, 17, 10, 4, 3, 3, 2, 1),
    # Balanced 
    (34, 19, 14, 11, 10, 4, 3, 3, 2, 2),
    (35, 18, 14, 11, 10, 5, 3, 3, 2, 1),
]


def run_sweep():
    """Run parameter sweep on sample data and report results."""
    samples = load_samples()

    print("=" * 80)
    print("PARAMETER SWEEP — Redrob Hackathon Ranker")
    print("=" * 80)
    print(f"\nTesting {len(SWEEP_CONFIGS)} configurations on {len(samples)} sample candidates\n")

    results = []

    for i, config in enumerate(SWEEP_CONFIGS):
        (career_w, role_w, prod_ai_w, rr_w, behav_w, exp_w, skills_w, edu_w, loc_w, notice_w) = config
        label = f"Cfg{i+1}: Cr={career_w} Ro={role_w} Pr={prod_ai_w} RR={rr_w} Bh={behav_w} Ex={exp_w} Sk={skills_w} Ed={edu_w} Lc={loc_w} Nt={notice_w}"

        # Monkey-patch weights for this run (convert from integer % to decimal)
        import config as cfg
        orig_weights = cfg.WEIGHTS.copy()
        cfg.WEIGHTS["career_relevance"] = career_w / 100
        cfg.WEIGHTS["role_relevance"] = role_w / 100
        cfg.WEIGHTS["production_ai_evidence"] = prod_ai_w / 100
        cfg.WEIGHTS["retrieval_ranking_experience"] = rr_w / 100
        cfg.WEIGHTS["behavioral_signals"] = behav_w / 100
        cfg.WEIGHTS["experience_fit"] = exp_w / 100
        cfg.WEIGHTS["skills_match"] = skills_w / 100
        cfg.WEIGHTS["education_score"] = edu_w / 100

        start = time.time()
        heap_sorted = process_candidates(samples)
        elapsed = time.time() - start

        # Restore original weights
        cfg.WEIGHTS.update(orig_weights)

        top_score = heap_sorted[0][0]
        bottom_score = heap_sorted[-1][0]
        top_title = None
        for c in samples:
            if c.get("candidate_id") == heap_sorted[0][1]:
                top_title = c["profile"]["current_title"]
                break

        results.append({
            "config": config,
            "label": label,
            "time": elapsed,
            "top_score": top_score,
            "bottom_score": bottom_score,
            "top_id": heap_sorted[0][1],
            "top_title": top_title,
            "top_reasoning": heap_sorted[0][2][:100],
            "honeypots_in_top": sum(1 for h in heap_sorted if h[3] < 0.5),
        })

        print(f"  {label}")
        print(f"    Top: {results[-1]['top_id']} ({top_title}) — score={top_score:.4f}")
        print(f"    Bottom: {bottom_score:.4f} | Honeypots in top: {results[-1]['honeypots_in_top']}/{len(heap_sorted)}")
        print(f"    Time: {elapsed:.2f}s")
        print()

    # Summary
    print("=" * 80)
    print("SWEEP SUMMARY — Ranked by Top Score (descending)")
    print("=" * 80)
    results.sort(key=lambda r: -r["top_score"])
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['label']}")
        print(f"     Top={r['top_score']:.4f}  Bottom={r['bottom_score']:.4f}  "
              f"Honeypots={r['honeypots_in_top']}  Title={r['top_title']}")

    # Find best config (highest top score with minimal honeypots)
    best = max(results, key=lambda r: (r["top_score"], -r["honeypots_in_top"]))
    print(f"\n{'=' * 80}")
    print(f"BEST CONFIG: {best['label']}")
    print(f"  Top score: {best['top_score']:.4f}")
    print(f"  Top candidate: {best['top_id']} ({best['top_title']})")
    print(f"  Reasoning: {best['top_reasoning']}")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    run_sweep()
