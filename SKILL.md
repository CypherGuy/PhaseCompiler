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

**Required - You must ask the user for these:**

- `name` (project name, max 50 chars)
- `description` (what the project does, max 1000 chars)
- `done` (1+ completion conditions — what makes "done"?)
- `main_user` (who uses it? default: "Just Myself")
- `language` (default: "python")
- `runtime` (cli / web / mobile / desktop / library; default: "cli")
- `phase_count` (integer 6–12; default: 7)
- `architecture` (microservices / event_driven / serverless / other; default: "other")
- `scaling_strategy` (none / vertical / horizontal / serverless / auto; default: "none")
- `starting_point` (nothing / existing / prototype / mvp; default: "nothing")

**Optional - ask the user if they have a preference:**

- `constraints` (budget, time, team size, technical limits)
- `architecture_notes` (additional design context)
- `expected_scale` (users, requests/sec, data volume)
- `avoid` (what NOT to do — patterns, tools, approaches)

Confirm all inputs before generating.

---

### Step 2: Generate the Plan

For each phase **1** through **N** (where N = `phase_count`), produce a phase object with:

```json
{
  "id": 1,
  "title": "<meaningful, specific title>",
  "deliverable": "<concrete output — code, doc, features, tests>",
  "tasks": ["<task 1>", "<task 2>", "<task 3>"],
  "commit_condition": "<when this phase is complete>",
  "example_input": "<what flows into this phase>",
  "example_output": "<what comes out>"
}
```

**Generation Rules:**

- **Phases are sequential and build on each other.** Phase 2 depends on Phase 1, etc.
- **No "TBD" stubs.** Every field is concrete and specific to the project.
- **Titles reflect the phase purpose**, not just "Phase N". Example: "Setup & Project Structure", "Core API Endpoints", "Integration & Testing".
- **Deliverables are tangible.** Examples: "Working CLI with arg parsing", "Database schema + migrations", "Frontend deployment to staging".
- **Tasks are actionable.** 3–5 per phase, in order. Example: `["Create models.py", "Write migrations", "Add CLI argument parsing"]`.
- **Commit conditions are testable.** Example: "All unit tests pass, API responds to 5 core endpoints."
- **Example I/O shows data flow.** Describes what state/artifacts exist before and after the phase.
- **Always ask questions.** Clarify any ambiguities, missing information or otherwise things the user didn't directly provide with the user before proceeding.
- **Determine the value add of the project.** If the user doesn't explicitly state it, ask "What is the main value or benefit this project provides to users? How does it solve an issue they have or improve their workflow?" Use this to guide phase generation.

**Generation Strategy:**

1. **Assess the project type** (language, runtime, architecture, starting point).
2. **Decompose into logical phases** based on the project's structure:
   - If starting from nothing: Setup → Models → API/Core → Testing → Integration → Polish → Deploy
   - If web project: Setup → Auth → Database → API → Frontend → Testing → Deploy
   - If library: Setup → Core Logic → Tests → Docs → Package → Release
3. **Scale by `phase_count`.** Merge or split phases to fit the requested count.
4. **Incorporate constraints** (time, budget, team size, dependencies).
5. **Order tasks within each phase** so they can be executed sequentially.

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

As an additional feature, the user may request to export this information to GitHub. Feel free to tell them that you can do this. If they do so, you need to generate two additional files:

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
      - "scripts/phasecompiler-import.py"
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
