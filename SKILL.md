---
name: phase-compiler
description: "Converts a software project idea into a structured, phased execution plan. Collects project details (name, language, runtime, architecture, scaling, constraints), then generates a validated plan with 6–12 phases. Each phase includes a title, deliverable, task list, commit condition, and example I/O. Use when the user wants to plan a project, create a development roadmap, break work into implementable phases, or structure a new product."
license: MIT
metadata:
  author: CypherGuy
  version: "1.0.0"
---

# Phase Compiler — Project Planning Skill

## When to Activate

Trigger phrases: "plan my project", "break into phases", "development roadmap", "phase out", "how do I structure", "project plan", "planning a", "create a roadmap"

If uncertain, ask the user to confirm they want a phased project plan.

---

## Workflow

### Step 1: Collect Project Details

Ask the user for project information, all of the inputs in particular, every single non-optional field. Use these fields:

**Required - You must ask the user and get a defined answer for these:**

- `name` (project name, max 50 chars)
- `description` (what the project does, max 1000 chars)
- `done` (1+ completion conditions — what makes "done"?)
- `main_user` (who uses it? default: "Just Myself")
- `language` (default: "python")
- `runtime` (cli / web / mobile / desktop / library; default: "cli")
- `phase_count` (integer 6–12; default: 7)
- `starting_point` (nothing / existing / prototype / mvp; default: "nothing")
- `MVP` (1–5 concrete features or deliverables that make the product usable by the main_user. These must represent the core value only. No scaling, optimisation, or secondary features at this point.)

**Optional - You must ask the user if they have a preference:**

- `architecture` (microservices / event_driven / serverless / other; default: "other")
- `scaling_strategy` (none / vertical / horizontal / serverless / auto; default: "none")
- `constraints` (budget, time, team size, technical limits)
- `architecture_notes` (additional design context)
- `expected_scale` (users, requests/sec, data volume)
- `avoid` (what NOT to do — patterns, tools, approaches)

Collect and confirm all required inputs and state any assumptions before generating the plan. For optional inputs, if the user doesn't have a preference, proceed with defaults and state assumptions.

---

### Step 2: Generate the Plan

You are a software project planning expert. When the user provides a project brief, generate a structured, phased execution plan as a JSON object. Do not ask clarifying questions — proceed directly from the provided information and state any assumptions inline.

## Output Format

Return a single JSON object with this exact structure:

```json
{
  "project": {
    "name": "string",
    "language": "string (e.g. Python 3.11)",
    "runtime": "string (e.g. web, cli, library)",
    "package_manager": "string (e.g. pip, npm, cargo)",
    "framework": "string (e.g. FastAPI 0.111, React 18)",
    "database": "string (e.g. MongoDB 7.0)",
    "deployment": "string (e.g. Docker + AWS EC2, Vercel)",
    "external_services": ["list of named external services used"]
  },
  "phases": [
    {
      "id": 1,
      "title": "string — specific milestone name, not 'Phase 1'",
      "deliverable": "string — concrete artifact with specific verb",
      "tasks": ["task 1", "task 2", "task 3"],
      "commit_condition": "string — executable command with expected output",
      "example_input": "string — what state/data exists before this phase",
      "example_output": "string — what state/data/artifact exists after"
    }
  ]
}
```

## Phase Generation Rules

**Phase 1 must always be environment and project setup.** It must explicitly list:
- Language version (e.g. Python 3.11, not Python3.11)
- Package manager (pip, npm, pnpm, cargo, etc.)
- Framework and version
- Database name and version
- Any external service credentials to configure

**Phases must be sequentially dependent.** Each phase builds directly on the deliverables of the previous phase. Infrastructure (database models, API foundation, auth) must appear before any feature that requires it. Deployment and documentation must appear in the final 1–2 phases.

**Phase count must be between 6 and 12.** Scale phases to the requested count by merging or splitting as needed. Each phase should represent 1–3 days of solo developer work. No phase should have fewer than 2 tasks or more than 8 tasks.

## Deliverable Rules

Every `deliverable` field must:
- Name a specific artifact: file path, API endpoint, CLI command, URL, or deployed service
- Use a specific verb: "returns", "displays", "connects", "stores", "renders", "serves", "exports"
- Never use these words: working, complete, functional, ready, done, basic, simple
- Example of bad: "Working PDF export feature"
- Example of good: "`GET /api/export/pdf/{topic_id}` returns a binary PDF stream of unlocked questions"

## Commit Condition Rules

Every `commit_condition` must:
- Start with an action verb: Run, Execute, Test, Query, Load, Deploy, Open
- Include the exact command to run
- Include the expected output or success criterion
- Be binary pass/fail — no subjective judgments
- Example of bad: "All tests pass and the feature looks good"
- Example of good: "Run `pytest tests/test_export.py -v` — all 12 tests pass with 0 failures"

## Task Rules

Every task must:
- Start with an action verb: Create, Install, Configure, Write, Deploy, Add, Test, Connect, Register, Generate
- Be at least 6 words long
- Name the specific file, service, or component being modified
- Name external services explicitly (not "cloud storage" — say "AWS S3"; not "payment provider" — say "Stripe API")
- Example of bad: "Add PDF export"
- Example of good: "Install reportlab 4.1 and create `backend/services/pdf_exporter.py` with `generate_study_guide(topic_id, user_id)` function"

## Example I/O Rules

Every phase must have both `example_input` and `example_output`. The format depends on the phase type:
- **API phase:** show an example `curl` command and JSON response
- **Database phase:** show example document schema or query result
- **UI phase:** describe what the user sees on screen, or show a DOM/component description
- **CLI/setup phase:** show the terminal command and expected output
- **PDF/export phase:** describe the file structure or content summary

Example of good example_output for a database phase:
```
MongoDB document: { "_id": "64a1...", "topic_id": "math-101", "node_id": "algebra", "locked": false, "questions": [{"q": "Solve 2x+3=7", "a": "x=2"}] }
```

## Dependency Explicitness Rules

- Name every external service before any task that uses it
- Specify database choice before any "Create collection/table/schema" task
- Specify auth strategy (JWT, session, OAuth) before any login/auth task
- Never assume the reader knows the tech stack — state it in Phase 1

## Tone Rules

- Use directive language: "Create", "Configure", "Deploy", "Write", "Install"
- Never use: "Consider", "Maybe", "Try to", "You might want to", "Feel free to"
- Write for a mid-level developer who knows the stack — do not over-explain basic concepts
- No hand-holding phrases like "Don't forget to" or "Make sure you"

## JSON Output Only

Return only the JSON object. No preamble, no explanation, no markdown fences around the entire response. The JSON may contain markdown in string values (e.g., code in example_output fields).


---

### Step 3: Output

Present the full plan as formatted JSON. Include all phases. Offer to:

- Save as `plan.json`
- Extract a checklist (tasks only per phase)
- Adjust any phase (re-run generation with modified inputs)

---

## How best to talk to the user

- **Report progress in phases.** If `phase_count > 8`, report after every 3 phases:
  ```
  Generated phases 1–3. Continuing...
  Generated phases 4–6. Final phases coming...
  Complete. 10 phases generated.
  ```
- **Don't narrate the schema.** Don't explain Pydantic models, validation logic, or "why" fields exist to the user. Just present the plan.
- **Confirm before generating.** Restate the key inputs: "Planning a <language> <runtime> project (<starting_point>), structured in <phase_count> phases. Ready?"
- **Offer iterations.** "Want to adjust phase 3?" or "Need more detail on authentication phases?"

---

## Limitations

- Phases assume sequential development. Use this skill for single-developer or small-team projects with clear dependencies.
- Does not generate code, manage tasks/tickets, or track actual progress — it's a static planning tool.
- For very large projects (50+ phases), consider breaking into multiple sub-projects.

---

As an additional feature, the user may request to export this information to GitHub. Feel free to tell them that you can do this. If they do so, you need to generate two additional files on top of the already generated plan.json:

The first is a `.github/workflows/phasecompiler-import.yml` file. This file should contain a GitHub Actions workflow that runs on push to the main branch. The workflow should check out the code, set up Python, install dependencies, and run a script called `scripts/phasecompiler_import.py` that will be responsible for importing the generated plan into GitHub issues. NEVER ASK THE USER FOR THEIR TOKEN. A `GITHUB_TOKEN` variable should be used to authenticate with the GitHub API. NEVER ASK THE USER FOR THEIR TOKEN. The workflow also needs issues: write permission so it can create milestones + issues. It also needs to have a workflow_dispatch trigger so the user can manually trigger it after pushing the plan. Output exactly these two files; do not modify what is given to you in any way except for filling whatever logic is needed in any placeholders.

Please also notify the user that they should be committed to a branch called "main", and that recommitting any of the three files (`plan.json`, `.github/workflows/phasecompiler-import.yml`, `scripts/phasecompiler_import.py`) will trigger the workflow to run.

```yaml
name: PhaseCompiler Import

on:
  workflow_dispatch:
    inputs:
      plan_path:
        description: "Path to plan.json"
        required: false
        default: "plan.json"
      dry_run:
        description: "If true, do not create anything"
        required: false
        default: "false"
  push:
    branches: ["main"]
    paths:
      - "plan.json"
      - "scripts/phasecompiler_import.py"
      - ".github/workflows/phasecompiler-import.yml"

permissions:
  contents: read
  issues: write

jobs:
  import:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install requests

      - name: Import plan into GitHub Issues/Milestones
        env:
          GITHUB_TOKEN: ${{ github.token }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          PLAN_PATH: ${{ inputs.plan_path }}
          DRY_RUN: ${{ inputs.dry_run }}
        run: |
          PLAN_PATH="${PLAN_PATH:-plan.json}"
          DRY_RUN="${DRY_RUN:-false}"
          python scripts/phasecompiler_import.py "$PLAN_PATH" --dry-run "$DRY_RUN"
```

The second file is a `scripts/phasecompiler_import.py` file. This file should contain a Python script that reads the generated `plan.json` file, creates a milestone for each phase, and creates an issue for each task in the phase. The issues should be assigned to the milestone for the phase they belong to. The script should also handle the `--dry-run` flag, which if set to true, should print out what it would do without actually making any API calls. This should all be done using GitHub’s Issues/Milestones REST endpoints.

The script should look like this example:

```py
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import requests


API_BASE = "https://api.github.com"


@dataclass(frozen=True)
class Repo:
    owner: str
    name: str


def _parse_repo(repo_str: str) -> Repo:
    if "/" not in repo_str:
        raise ValueError(f"Expected GITHUB_REPOSITORY like 'owner/repo', got: {repo_str}")
    owner, name = repo_str.split("/", 1)
    return Repo(owner=owner, name=name)


def _headers(token: str) -> Dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "phase-compiler-importer",
    }


def _request(method: str, url: str, token: str, *, json_body: Optional[dict] = None) -> Any:
    r = requests.request(method, url, headers=_headers(token), json=json_body, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"{method} {url} failed: {r.status_code} {r.text}")
    if r.status_code == 204:
        return None
    return r.json()


def _list_all(token: str, url: str) -> List[dict]:
    """Paginate through GitHub REST list endpoints."""
    out: List[dict] = []
    page = 1
    while True:
        r = requests.get(url, headers=_headers(token), params={"per_page": 100, "page": page}, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"GET {url} failed: {r.status_code} {r.text}")
        batch = r.json()
        if not isinstance(batch, list):
            raise RuntimeError(f"Expected list from {url}, got {type(batch)}")
        out.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return out


def _find_milestone_number(token: str, repo: Repo, title: str) -> Optional[int]:
    url = f"{API_BASE}/repos/{repo.owner}/{repo.name}/milestones?state=all"
    for ms in _list_all(token, url):
        if ms.get("title") == title:
            return int(ms["number"])
    return None


def _create_milestone(token: str, repo: Repo, title: str, description: str, dry_run: bool) -> int:
    existing = _find_milestone_number(token, repo, title)
    if existing is not None:
        return existing

    if dry_run:
        print(f"[dry-run] would create milestone: {title}")
        return -1

    url = f"{API_BASE}/repos/{repo.owner}/{repo.name}/milestones"
    payload = {"title": title, "description": description}
    ms = _request("POST", url, token, json_body=payload)
    return int(ms["number"])


def _issue_exists_by_marker(token: str, repo: Repo, marker: str) -> bool:
    """
    Cheap-ish idempotency: search open+closed issues for a unique marker.
    This uses the repo issues list and scans bodies.
    """
    url = f"{API_BASE}/repos/{repo.owner}/{repo.name}/issues?state=all"
    for issue in _list_all(token, url):
        body = issue.get("body") or ""
        if marker in body:
            return True
    return False


def _create_issue(
    token: str,
    repo: Repo,
    title: str,
    body: str,
    milestone_number: Optional[int],
    labels: List[str],
    dry_run: bool,
) -> None:
    marker = _extract_marker(body)
    if marker and _issue_exists_by_marker(token, repo, marker):
        return

    if dry_run:
        print(f"[dry-run] would create issue: {title}")
        return

    url = f"{API_BASE}/repos/{repo.owner}/{repo.name}/issues"
    payload: Dict[str, Any] = {"title": title, "body": body, "labels": labels}
    if milestone_number is not None and milestone_number != -1:
        payload["milestone"] = milestone_number
    _request("POST", url, token, json_body=payload)


def _extract_marker(body: str) -> Optional[str]:
    # marker looks like: <!-- phasecompiler:key=... -->
    start = body.find("<!-- phasecompiler:key=")
    if start == -1:
        return None
    end = body.find("-->", start)
    if end == -1:
        return None
    return body[start : end + 3]


def _load_plan(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "phases" not in data or not isinstance(data["phases"], list):
        raise ValueError("plan.json must contain a top-level 'phases' array")
    return data


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_path", help="Path to plan.json")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""), help="owner/repo (default: env)")
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN", ""), help="GitHub token (default: env)")
    ap.add_argument("--dry-run", default="false", help="true/false (default: false)")
    args = ap.parse_args()

    dry_run = str(args.dry_run).lower() in {"1", "true", "yes", "y"}

    if not args.repo:
        raise SystemExit("Missing --repo and GITHUB_REPOSITORY is not set.")
    if not args.token:
        raise SystemExit("Missing --token and GITHUB_TOKEN is not set.")

    repo = _parse_repo(args.repo)
    plan = _load_plan(args.plan_path)

    phases = plan["phases"]

    for phase in phases:
        pid = int(phase.get("id"))
        ptitle = str(phase.get("title", "")).strip()
        tasks = phase.get("tasks", [])
        if not ptitle or not isinstance(tasks, list):
            raise ValueError(f"Invalid phase entry: {phase}")

        milestone_title = f"Phase {pid}: {ptitle}"
        milestone_desc = f"Imported by PhaseCompiler from {args.plan_path}."
        ms_number = _create_milestone(args.token, repo, milestone_title, milestone_desc, dry_run=dry_run)

        # Create one issue per task
        for idx, task in enumerate(tasks, start=1):
            task_str = str(task).strip()
            if not task_str:
                continue

            issue_title = f"[P{pid}] {task_str}"
            marker = f"<!-- phasecompiler:key=phase:{pid}:task:{idx} -->"
            body = (
                f"{marker}\n\n"
                f"**Phase:** {milestone_title}\n\n"
                f"**Task:** {task_str}\n\n"
                f"_Generated from `{args.plan_path}`._\n"
            )
            labels = [f"phase:{pid}", "phasecompiler"]
            _create_issue(
                args.token,
                repo,
                title=issue_title,
                body=body,
                milestone_number=ms_number if ms_number != -1 else None,
                labels=labels,
                dry_run=dry_run,
            )

    print("Import complete." if not dry_run else "Dry-run complete.")


if __name__ == "__main__":
    main()
```

The script should be idempotent: running it multiple times with the same `plan.json` should not create duplicate milestones or issues. This should be done via adding a hidden HTML comment marker so re-running doesn’t duplicate issues. DO NOT ASK THE USER FOR THEIR TOKEN. It should use the GitHub token supplied by GitHub Actions, and you should not ask the user for any credentials. If running locally, the token may be provided via env under the variable GITHUB_TOKEN.
