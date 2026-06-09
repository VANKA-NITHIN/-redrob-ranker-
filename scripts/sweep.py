"""
Parameter Sweep — Find optimal feature weights for the ranker.
Tests different weight configurations on sample data and reports top candidates.
"""
import json
import os
import sys
import itertools
import time

sys.path.insert(0, os.path.dirname(__file__))

from ranker import compute_total_score, process_candidates

SAMPLE_PATH = os.path.join("data", "sample_candidates.json")


def load_samples():
    with open(SAMPLE_PATH, "r") as f:
        return json.load(f)


# Define weight configurations to test
SWEEP_CONFIGS = [
    # (career, prod_ai, role, behavioral, experience, skills, education)
    # Baseline
    (0.38, 0.18, 0.17, 0.12, 0.08, 0.02, 0.05),
    # More career-focused
    (0.40, 0.18, 0.17, 0.10, 0.08, 0.02, 0.05),
    (0.42, 0.18, 0.15, 0.10, 0.08, 0.02, 0.05),
    # More production AI focused
    (0.35, 0.22, 0.17, 0.11, 0.08, 0.02, 0.05),
    (0.35, 0.20, 0.17, 0.13, 0.08, 0.02, 0.05),
    # More role relevance focused
    (0.35, 0.18, 0.20, 0.12, 0.08, 0.02, 0.05),
    (0.36, 0.18, 0.19, 0.12, 0.08, 0.02, 0.05),
    # More behavioral focused
    (0.35, 0.17, 0.15, 0.16, 0.10, 0.02, 0.05),
    # More experience focused
    (0.35, 0.17, 0.15, 0.12, 0.12, 0.02, 0.07),
    # Even lower skills
    (0.38, 0.19, 0.17, 0.12, 0.08, 0.01, 0.05),
    (0.39, 0.19, 0.17, 0.11, 0.08, 0.01, 0.05),
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
        career_w, prod_ai_w, role_w, behav_w, exp_w, skills_w, edu_w = config
        label = f"Cfg{i+1}: C={career_w:.2f} P={prod_ai_w:.2f} R={role_w:.2f} B={behav_w:.2f} E={exp_w:.2f} S={skills_w:.2f} Ed={edu_w:.2f}"

        # Monkey-patch weights for this run
        import config as cfg
        orig_weights = cfg.WEIGHTS.copy()
        cfg.WEIGHTS["career_relevance"] = career_w
        cfg.WEIGHTS["production_ai_evidence"] = prod_ai_w
        cfg.WEIGHTS["role_relevance"] = role_w
        cfg.WEIGHTS["behavioral_signals"] = behav_w
        cfg.WEIGHTS["experience_fit"] = exp_w
        cfg.WEIGHTS["skills_match"] = skills_w
        cfg.WEIGHTS["education_score"] = edu_w

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
