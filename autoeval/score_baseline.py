#!/usr/bin/env python3
"""
autoeval/score_baseline.py — Score the baseline plan once to seed results.tsv.

Run this before the main loop to establish the starting champion score.
The baseline plan is treated as "iteration 0" with status "baseline".
"""

import json
import os
import sys

# Reuse helpers from run.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run import (
    BASE, EVAL_FILE, RESULTS_FILE, SCORES_DIR, CHAMP_FILE, PROMPT_FILE,
    NUM_PLANS, REQ_COUNTS,
    load, save, log, make_client,
    score_plans, compute_test_totals, save_score_data, append_result,
)

BASELINE_PLAN = os.path.join(BASE, "plans", "baseline.json")


def main() -> None:
    if not os.path.exists(BASELINE_PLAN):
        sys.exit(f"Baseline plan not found: {BASELINE_PLAN}")

    # Check we haven't already seeded
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            lines = f.readlines()
        for line in lines[1:]:
            if line.startswith("0\t"):
                log("Baseline (iteration 0) already in results.tsv — skipping.")
                return

    client = make_client()
    eval_suite = load(EVAL_FILE)
    baseline_text = load(BASELINE_PLAN)

    log(f"Scoring baseline plan (replicated {NUM_PLANS}× to fill all plan slots)...")

    # Replicate baseline NUM_PLANS times so the scorer uses the full rubric
    plans = [baseline_text] * NUM_PLANS
    total_score, score_data = score_plans(client, plans, eval_suite)
    analysis = score_data.get("analysis", "")
    test_totals = compute_test_totals(score_data)

    single_plan_score = total_score // NUM_PLANS
    log(f"Baseline single-plan score: {single_plan_score}/490")
    log(f"Baseline aggregate ({NUM_PLANS} plans): {total_score}/{NUM_PLANS * 49 * 10}")
    log(f"Analysis: {analysis}")
    log("Per-test: " + " | ".join(f"{k}:{test_totals[k]}" for k in REQ_COUNTS))

    # Save score data
    save_score_data(score_data, 0)

    # Write iteration 0 to results.tsv
    append_result(
        iteration=0,
        score=total_score,
        champion_score=total_score,
        status="baseline",
        prompt_hash="baseline",
        brief_name="baseline.json",
        analysis=analysis,
        test_totals=test_totals,
    )

    # Save baseline prompt as initial champion (so loop knows what to beat)
    if not os.path.exists(CHAMP_FILE) and os.path.exists(PROMPT_FILE):
        save(CHAMP_FILE, load(PROMPT_FILE))
        log("Saved current prompt.md as initial champion_prompt.md.")

    log(f"Done. Baseline score {total_score}/{NUM_PLANS * 49 * 10} written as iteration 0.")
    log("Run `python autoeval/run.py` to start improving.")


if __name__ == "__main__":
    main()
