#!/usr/bin/env python3
"""
autoeval/run.py — Self-improving phase-compiler skill loop.

Inspired by karpathy/autoresearch:
  - Single modifiable artifact: prompt.md (plan generation instructions)
  - Fixed evaluation:           eval_suite.md (49 requirements, 0–10 each)
  - Fixed test input:           brief.md (StudyBattles project brief)
  - Scoring:                    9 plans (3×brief) × 49 requirements × 10 pts = 4410 max
  - Accept/reject:              keep prompt if score > champion_score, else revert
  - Results log:                results.tsv

Loop per iteration:
  1. Load prompt.md (challenger) or champion_prompt.md if last run failed
  2. Generate 5 plans via Claude API
  3. Score all plans against all 49 requirements
  4. If score > champion: save champion_prompt.md, update SKILL.md Step 2
  5. Always generate improved prompt.md for next iteration
  6. Append row to results.tsv
"""

import anthropic
import datetime
import hashlib
import json
import os
import re
import sys

# ── paths ──────────────────────────────────────────────────────────────────────
BASE         = os.path.dirname(os.path.abspath(__file__))
PROMPT_FILE  = os.path.join(BASE, "prompt.md")
CHAMP_FILE   = os.path.join(BASE, "champion_prompt.md")
EVAL_FILE    = os.path.join(BASE, "eval_suite.md")
BRIEFS = [
    os.path.join(BASE, "brief.md"),       # StudyBattles  — 11 phases, MVP at 7
    os.path.join(BASE, "brief_cli.md"),   # DevLogSummarizer — 6 phases, MVP at 4
    os.path.join(BASE, "brief_saas.md"),  # InvoiceFlow   —  8 phases, MVP at 5
]
RESULTS_FILE = os.path.join(BASE, "results.tsv")
SKILL_FILE   = os.path.join(BASE, "..", "SKILL.md")
PLANS_DIR    = os.path.join(BASE, "plans")
SCORES_DIR   = os.path.join(BASE, "scores")

NUM_PLANS_PER_BRIEF = 3                            # plans generated per brief
NUM_PLANS = NUM_PLANS_PER_BRIEF * len(BRIEFS)      # 3 briefs × 3 = 9 total
MAX_SCORE = NUM_PLANS * 49 * 10                    # 9 × 49 × 10 = 4410

# ── helpers ────────────────────────────────────────────────────────────────────

def load(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()

def save(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def log(msg: str) -> None:
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

# ── claude client ──────────────────────────────────────────────────────────────

def make_client() -> anthropic.Anthropic:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        # Try loading from .env in project root
        env_path = os.path.join(BASE, "..", ".env")
        if os.path.exists(env_path):
            for line in open(env_path):
                if line.startswith("ANTHROPIC_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"\'')
    if not key:
        sys.exit("ANTHROPIC_API_KEY not found in environment or .env file.")
    return anthropic.Anthropic(api_key=key)

# ── generation ─────────────────────────────────────────────────────────────────

def generate_plan(client: anthropic.Anthropic, prompt: str, brief: str) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # cheapest model — generation only
        max_tokens=6000,
        system=prompt,
        messages=[{"role": "user", "content": brief}],
    )
    return response.content[0].text

# ── scoring ────────────────────────────────────────────────────────────────────

SCORE_SCHEMA = """{
  "plan_1": {
    "test_1":  {"req_1": 0, "req_2": 0, "req_3": 0, "req_4": 0},
    "test_2":  {"req_1": 0, "req_2": 0, "req_3": 0, "req_4": 0},
    "test_3":  {"req_1": 0, "req_2": 0, "req_3": 0, "req_4": 0, "req_5": 0},
    "test_4":  {"req_1": 0, "req_2": 0, "req_3": 0, "req_4": 0},
    "test_5":  {"req_1": 0, "req_2": 0, "req_3": 0, "req_4": 0},
    "test_6":  {"req_1": 0, "req_2": 0, "req_3": 0, "req_4": 0},
    "test_7":  {"req_1": 0, "req_2": 0, "req_3": 0, "req_4": 0},
    "test_8":  {"req_1": 0, "req_2": 0, "req_3": 0, "req_4": 0, "req_5": 0},
    "test_9":  {"req_1": 0, "req_2": 0, "req_3": 0, "req_4": 0, "req_5": 0},
    "test_10": {"req_1": 0, "req_2": 0, "req_3": 0, "req_4": 0, "req_5": 0},
    "test_11": {"q1": 0, "q2": 0, "q3": 0, "q4": 0, "q5": 0}
  },
  "plan_2": { ... same structure ... },
  "plan_3": { ... same structure ... },
  "plan_4": { ... same structure ... },
  "plan_5": { ... same structure ... },
  "plan_6": { ... same structure ... },
  "plan_7": { ... same structure ... },
  "plan_8": { ... same structure ... },
  "plan_9": { ... same structure ... },
  "analysis": "2–3 sentences on the most common failure patterns"
}"""


def score_plans(client: anthropic.Anthropic, plans: list[str], eval_suite: str) -> tuple[int, dict]:
    plans_block = "\n\n".join(
        f"=== PLAN {i + 1} ===\n{p}" for i, p in enumerate(plans)
    )

    prompt = f"""You are a strict evaluator for phase-compiler plans.
Score every requirement for every plan on a 0–10 scale:
  0  = completely fails
  5  = partially meets
  10 = fully meets

EVAL SUITE (49 requirements across 11 tests):
{eval_suite}

PLANS TO EVALUATE:
{plans_block}

Return ONLY valid JSON matching this schema (replace 0s with actual scores):
{SCORE_SCHEMA}

Important:
- test_11 asks 5 retrieval questions — score 10 if the plan alone answers the question, 0 if it cannot, 5 if partially.
- Be strict. A deliverable containing the word "working" scores 0 for test_5 req_2.
- A commit condition with no expected output scores 0 for test_6 req_2.
"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text

    # Extract JSON — handle both bare and fenced output
    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        raise ValueError(f"Scorer returned no JSON:\n{raw[:800]}")
    data = json.loads(match.group())

    total = 0
    for plan_key in [f"plan_{i}" for i in range(1, NUM_PLANS + 1)]:
        plan_scores = data.get(plan_key, {})
        for test_scores in plan_scores.values():
            if isinstance(test_scores, dict):
                total += sum(int(v) for v in test_scores.values())
    data["total_score"] = total
    return total, data


# ── prompt improvement ─────────────────────────────────────────────────────────

def improve_prompt(
    client: anthropic.Anthropic,
    current_prompt: str,
    plans: list[str],
    score_data: dict,
    eval_suite: str,
    champion_score: int,
) -> str:
    # Aggregate per-test scores across all plans to find worst tests
    test_totals: dict[str, int] = {}
    test_maxes: dict[str, int] = {}
    req_counts = {
        "test_1": 4, "test_2": 4, "test_3": 5, "test_4": 4,
        "test_5": 4, "test_6": 4, "test_7": 4, "test_8": 5,
        "test_9": 5, "test_10": 5, "test_11": 5,
    }
    for test_key, req_count in req_counts.items():
        total_pts = 0
        for plan_key in [f"plan_{i}" for i in range(1, NUM_PLANS + 1)]:
            plan_scores = score_data.get(plan_key, {})
            test_scores = plan_scores.get(test_key, {})
            if isinstance(test_scores, dict):
                total_pts += sum(int(v) for v in test_scores.values())
        max_pts = NUM_PLANS * req_count * 10
        test_totals[test_key] = total_pts
        test_maxes[test_key] = max_pts

    worst = sorted(test_totals.items(), key=lambda x: x[1] / test_maxes[x[0]])[:4]
    worst_str = "; ".join(
        f"{t} scored {test_totals[t]}/{test_maxes[t]}" for t, _ in worst
    )

    sample = "\n\n".join(
        f"=== PLAN {i + 1} (first 1200 chars) ===\n{p[:1200]}"
        for i, p in enumerate(plans[:3])
    )

    prompt = f"""You are improving a plan-generation system prompt for a software project planning skill called phase-compiler.

CURRENT PROMPT:
{current_prompt}

EVAL SUITE (fixed, never change this):
{eval_suite}

CURRENT SCORE: {score_data.get('total_score', 0)}/{MAX_SCORE}
CHAMPION SCORE: {champion_score}/{MAX_SCORE}

FAILURE ANALYSIS: {score_data.get('analysis', 'none')}
WORST TESTS: {worst_str}

SAMPLE GENERATED PLANS (first 3):
{sample}

Your task: rewrite the CURRENT PROMPT to fix the identified failure patterns.

Rules for your rewrite:
- Keep every rule that is already working well
- Add concrete, prescriptive rules with examples for the worst-performing tests
- Be more explicit — vague instructions produce vague plans
- Do NOT add padding or meta-commentary — every sentence must enforce a specific behavior
- The prompt is a system prompt fed directly to an LLM; it must be self-contained
- Keep the rewrite under 3000 words

Return ONLY the improved prompt text — no preamble, no explanation, no markdown wrapper.
"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


# ── results log ────────────────────────────────────────────────────────────────

def load_champion_score() -> int:
    if not os.path.exists(RESULTS_FILE):
        return 0
    scores = []
    with open(RESULTS_FILE, encoding="utf-8") as f:
        for line in f.readlines()[1:]:  # skip header
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                try:
                    scores.append(int(parts[2]))
                except ValueError:
                    pass
    return max(scores) if scores else 0


def get_iteration() -> int:
    if not os.path.exists(RESULTS_FILE):
        return 1
    with open(RESULTS_FILE, encoding="utf-8") as f:
        lines = f.readlines()
    return max(1, len(lines))  # header counts as line 1 → iteration 1 on first run


REQ_COUNTS = {
    "test_1": 4, "test_2": 4, "test_3": 5, "test_4": 4,
    "test_5": 4, "test_6": 4, "test_7": 4, "test_8": 5,
    "test_9": 5, "test_10": 5, "test_11": 5,
}


def compute_test_totals(score_data: dict) -> dict[str, int]:
    """Return per-test aggregate scores across all plans."""
    totals: dict[str, int] = {k: 0 for k in REQ_COUNTS}
    for plan_key in [f"plan_{i}" for i in range(1, NUM_PLANS + 1)]:
        plan_scores = score_data.get(plan_key, {})
        for test_key in REQ_COUNTS:
            test_scores = plan_scores.get(test_key, {})
            if isinstance(test_scores, dict):
                totals[test_key] += sum(int(v) for v in test_scores.values())
    return totals


def save_score_data(score_data: dict, iteration: int) -> None:
    """Persist the full per-requirement score breakdown as JSON."""
    os.makedirs(SCORES_DIR, exist_ok=True)
    path = os.path.join(SCORES_DIR, f"iter{iteration:04d}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(score_data, f, indent=2)


def append_result(
    iteration: int,
    score: int,
    champion_score: int,
    status: str,
    prompt_hash: str,
    brief_name: str,
    analysis: str,
    test_totals: dict[str, int],
) -> None:
    write_header = not os.path.exists(RESULTS_FILE)
    test_keys = list(REQ_COUNTS.keys())
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        if write_header:
            per_test_header = "\t".join(test_keys)
            f.write(f"iteration\ttimestamp\tscore\tchampion_score\tstatus\tprompt_hash\tbrief\t{per_test_header}\tanalysis\n")
        ts = datetime.datetime.now().isoformat()
        safe_analysis = analysis.replace("\t", " ").replace("\n", " ")[:300]
        per_test_vals = "\t".join(str(test_totals.get(k, 0)) for k in test_keys)
        f.write(f"{iteration}\t{ts}\t{score}\t{champion_score}\t{status}\t{prompt_hash}\t{brief_name}\t{per_test_vals}\t{safe_analysis}\n")


# ── skill.md sync ──────────────────────────────────────────────────────────────

def sync_to_skill_md(champion_prompt: str) -> None:
    """Replace the Step 2 generation content in SKILL.md with the champion prompt."""
    if not os.path.exists(SKILL_FILE):
        log(f"SKILL.md not found at {SKILL_FILE}, skipping sync.")
        return
    skill = load(SKILL_FILE)
    # Build the new Step 2 block
    new_block = (
        "### Step 2: Generate the Plan\n\n"
        + champion_prompt
        + "\n\n---"
    )
    updated = re.sub(
        r"### Step 2: Generate the Plan.*?---",
        new_block,
        skill,
        count=1,
        flags=re.DOTALL,
    )
    if updated == skill:
        log("Warning: SKILL.md Step 2 pattern not found — skipping sync.")
        return
    save(SKILL_FILE, updated)
    log("Synced champion prompt to SKILL.md Step 2.")


# ── save plans ─────────────────────────────────────────────────────────────────

def save_plans(plans: list[str], iteration: int, score: int) -> None:
    os.makedirs(PLANS_DIR, exist_ok=True)
    for i, plan in enumerate(plans):
        path = os.path.join(PLANS_DIR, f"iter{iteration:04d}_plan{i + 1}_score{score}.json")
        save(path, plan)


# ── main loop ──────────────────────────────────────────────────────────────────

def main() -> None:
    client = make_client()
    eval_suite = load(EVAL_FILE)
    champion_score = load_champion_score()
    iteration = get_iteration()

    brief_name = "all_3"

    # Load challenger prompt: use prompt.md if it exists, else fall back to champion
    if os.path.exists(PROMPT_FILE):
        current_prompt = load(PROMPT_FILE)
    elif os.path.exists(CHAMP_FILE):
        current_prompt = load(CHAMP_FILE)
        save(PROMPT_FILE, current_prompt)
    else:
        sys.exit("No prompt.md or champion_prompt.md found.")

    prompt_hash = hashlib.md5(current_prompt.encode()).hexdigest()[:8]
    log(f"Iteration {iteration} | Briefs: all 3 | Champion: {champion_score}/{MAX_SCORE} | Prompt: {prompt_hash}")

    # ── Step 1: Generate 3 plans per brief (9 total) ──────────────────────────
    log(f"Generating {NUM_PLANS_PER_BRIEF} plans × {len(BRIEFS)} briefs = {NUM_PLANS} total...")
    plans: list[str] = []
    plan_num = 0
    for brief_path in BRIEFS:
        brief = load(brief_path)
        brief_label = os.path.basename(brief_path)
        for j in range(NUM_PLANS_PER_BRIEF):
            plan_num += 1
            log(f"  Plan {plan_num}/{NUM_PLANS} ({brief_label}, variant {j + 1})...")
            plans.append(generate_plan(client, current_prompt, brief))

    # ── Step 2: Score all plans ────────────────────────────────────────────────
    log("Scoring 5 plans against 49 requirements (0–10 each)...")
    total_score, score_data = score_plans(client, plans, eval_suite)
    analysis = score_data.get("analysis", "")
    log(f"Score: {total_score}/{MAX_SCORE} | Champion: {champion_score}/{MAX_SCORE}")
    log(f"Analysis: {analysis[:200]}")

    # ── Step 3: Save plans and score breakdown to disk ────────────────────────
    save_plans(plans, iteration, total_score)
    save_score_data(score_data, iteration)
    test_totals = compute_test_totals(score_data)
    log("Per-test scores: " + " | ".join(f"{k}:{test_totals[k]}" for k in REQ_COUNTS))

    # ── Step 4: Accept / reject ────────────────────────────────────────────────
    if total_score > champion_score:
        status = "keep"
        log(f"IMPROVEMENT: {champion_score} → {total_score}. Saving new champion.")
        save(CHAMP_FILE, current_prompt)
        champion_score = total_score
        sync_to_skill_md(current_prompt)
    else:
        status = "discard"
        log("No improvement. Reverting to champion for next improvement base.")
        # Improve from champion, not the failed challenger
        if os.path.exists(CHAMP_FILE):
            current_prompt = load(CHAMP_FILE)

    # ── Step 5: Generate improved prompt for next iteration ───────────────────
    log("Generating improved prompt for next iteration...")
    improved = improve_prompt(client, current_prompt, plans, score_data, eval_suite, champion_score)
    save(PROMPT_FILE, improved)
    log("Saved improved prompt.md.")

    # ── Step 6: Log result ─────────────────────────────────────────────────────
    append_result(iteration, total_score, champion_score, status, prompt_hash, brief_name, analysis, test_totals)
    log(f"Done. Results appended to results.tsv.")


if __name__ == "__main__":
    main()
