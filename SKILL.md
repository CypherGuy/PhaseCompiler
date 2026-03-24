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

**Phase count must be between 6 and 12.** Each phase should represent 1–3 days of solo developer work. Every phase must have at least 2 tasks and no more than 7 tasks. If a phase accumulates 8+ tasks, split it into two phases with distinct milestones. Phases must represent meaningful milestones — not arbitrary groupings of tasks.

**Always output all phases to completion.** Never truncate the plan. The final phase must be a deployment, documentation, or polish phase. Ensure the JSON is complete and valid — every phase array must close, every object must close.

## Task Ordering Within Phases: UNORDERED SET — CRITICAL

**Tasks within a phase are an UNORDERED SET of independent actions.** Present tasks as a flat JSON array of strings. The order of strings in the JSON array carries NO meaning. A developer must be able to execute them in ANY order (or in parallel) unless an explicit artifact dependency is noted.

**Absolute prohibitions inside task strings:**
- No numeric prefixes: "1.", "2.", "3.", "Step 1:", "Step 2:"
- No ordinal words implying sequence between sibling tasks: "First", "Then", "Next", "After that", "Finally", "Subsequently", "Lastly", "Before the above", "Once the previous"
- No alphabetic prefixes: "a)", "b)", "A."

**The ONLY exception:** If task B literally requires the file or artifact created by task A within the same phase, note the dependency inside task B's string by referencing the artifact name (e.g., "Create `tests/test_auth.py` testing the endpoints defined in `routes/auth.py`"). Do NOT use ordinal language — reference the artifact, not the position.

**Shuffle-test your tasks mentally:** If reordering the array would confuse a reader, you have embedded implicit sequence. Rewrite to eliminate it.

**Good example (unordered, independent, no sequence indicators):**
```json
"tasks": [
  "Install FastAPI 0.111 and uvicorn 0.29 into requirements.txt",
  "Create `backend/main.py` with FastAPI app instance and CORS middleware",
  "Add `GET /health` endpoint returning {\"status\": \"ok\"} in `backend/routes/health.py`",
  "Write pytest test for health endpoint in `tests/test_health.py`"
]
```

**Bad example (numbered, sequential language):**
```json
"tasks": ["1. Install FastAPI", "2. Then create main.py", "3. Next add health endpoint", "4. Finally write tests"]
```

## Deliverable Rules

Every `deliverable` field must:
- Name a specific artifact: file path, API endpoint, CLI command, URL, or deployed service
- Use a specific verb: "returns", "displays", "connects", "stores", "renders", "serves", "exports", "generates", "validates", "authenticates"
- **Banned words (NEVER use in ANY deliverable, including deployment phases):** "working", "complete", "functional", "ready", "done", "basic", "simple", "proper", "fully", "successful", "accessible", "operational"
- Scan every deliverable string character by character for ALL banned words before output. This includes compound forms like "fully functional" or "accessible at".

**Bad:** "Working PDF export feature"
**Bad:** "Basic user authentication system"
**Bad:** "Application fully functional on AWS EC2"
**Bad:** "Deployed service accessible at https://..."
**Good:** "`GET /api/export/pdf/{topic_id}` returns a binary PDF stream of unlocked questions"
**Good:** "`POST /api/auth/login` validates credentials against MongoDB users collection and returns a signed JWT"
**Good:** "`https://app.example.com/health` returns {\"status\": \"ok\"} from Docker container on AWS EC2"

## Commit Condition Rules

Every `commit_condition` must:
- Start with an action verb: Run, Execute, Test, Query, Load, Deploy, Open, Send, Call
- Include the exact command to run (copy-pasteable into terminal)
- Include the expected output or success criterion with specific numbers or strings
- Be binary pass/fail — no subjective judgments
- Never be "Phase complete", "All tasks done", "Feature looks good", or any variant

**Good:** "Run `pytest tests/test_export.py -v` — all 12 tests pass with 0 failures"
**Good:** "Run `curl -s http://localhost:8000/health | jq .status` — returns `\"ok\"`"

## Task Rules

Every task must:
- Start with an action verb: Create, Install, Configure, Write, Deploy, Add, Test, Connect, Register, Generate, Implement, Define, Set up, Initialize
- Be at least 6 words long
- Name the specific file, service, or component being modified
- Name external services explicitly (not "cloud storage" — say "AWS S3"; not "payment provider" — say "Stripe API"; not "AI service" — say "OpenAI GPT-4 API")

## Example I/O Rules — MANDATORY Format Matching Per Phase Type

Every phase MUST have both `example_input` and `example_output`. Select the format that matches what the phase actually produces. **Every phase must use at least one of the concrete formats below — never use vague descriptions like "the API works" or "the page loads".**

**Setup/CLI phases:** Show the terminal command and its expected stdout.
```
example_input: "Empty project directory with no dependencies installed"
example_output: "Run `python backend/main.py` — terminal prints 'Uvicorn running on http://127.0.0.1:8000'; `curl http://localhost:8000/docs` returns Swagger UI HTML"
```

**Database/model phases:** Show the document/row schema or a query with its result.
```
example_input: "MongoDB 'users' collection exists but contains no documents"
example_output: "db.users.findOne() returns {\"_id\": \"64a1b...\", \"email\": \"test@example.com\", \"hashed_password\": \"$2b$12...\", \"created_at\": \"2024-01-15T10:00:00Z\"}"
```

**API phases:** Show a concrete `curl` command and the JSON response body with status code.
```
example_input: "curl -X POST http://localhost:8000/api/topics -H 'Authorization: Bearer eyJ...' -H 'Content-Type: application/json' -d '{\"name\": \"Algebra\", \"subject\": \"Math\"}'"
example_output: "HTTP 201: {\"id\": \"64a1b2c3\", \"name\": \"Algebra\", \"subject\": \"Math\", \"created_at\": \"2024-01-15T10:00:00Z\"}"
```

**UI/Frontend phases:** Describe what the user sees — page URL, components rendered, interactive elements, and visible data.
```
example_input: "Browser at http://localhost:3000/dashboard — blank page with nav bar only"
example_output: "Browser at http://localhost:3000/dashboard — grid of topic cards with title, progress bar (e.g., '65% unlocked'), and 'Study' button; sidebar shows user stats"
```

**Export/file generation phases:** Describe file content, format, and size or structure.
```
example_input: "curl -X GET http://localhost:8000/api/export/pdf/64a1b2c3 -H 'Authorization: Bearer eyJ...'"
example_output: "HTTP 200 with Content-Type: application/pdf — 3-page PDF containing 15 questions with answers, topic title as header"
```

**Deployment phases:** Show the deploy command and the verification step.
```
example_input: "Run `docker-compose up -d` on AWS EC2 instance with .env configured"
example_output: "Run `curl -s https://api.example.com/health` — returns {\"status\": \"ok\", \"version\": \"1.0.0\"}; `docker ps` shows 3 containers running (api, mongodb, nginx)"
```

**CRITICAL: Phase-type detection.** For each phase, ask: "What artifact does this phase primarily produce?" Then use the matching format above. A phase that creates database models MUST show a schema/query example. A phase that adds API endpoints MUST show curl + JSON. A phase that modifies the frontend MUST describe what the browser renders. A phase that sets up infrastructure MUST show terminal commands and stdout.

**For projects with no frontend (CLI tools, libraries, pure APIs):** Use CLI or API examples for every phase. Do NOT fabricate UI examples. If a phase produces a library module, show an import statement and function call with expected return value.

**For projects with a frontend:** Every phase that modifies frontend code must include a UI-type example_output describing what the browser renders at a specific URL.

**Mixed phases (e.g., API + database):** Show the most user-facing format. An API phase that also creates database models should show the curl command and JSON response (the API example implicitly validates the database).

## Dependency Explicitness Rules

- Name every external service before any task that uses it
- Specify database choice before any "Create collection/table/schema" task
- Specify auth strategy (JWT, session, OAuth) before any login/auth task
- Never assume the reader knows the tech stack — state it in Phase 1
- Phase 1 must list: language version, runtime, package manager, framework with version, database with version

## Tone Rules

- Use directive language: "Create", "Configure", "Deploy", "Write", "Install"
- Never use: "Consider", "Maybe", "Try to", "You might want to", "Feel free to", "Don't forget to", "Make sure you"
- Write for a mid-level developer who knows the stack — do not over-explain basic concepts
- Be confident and prescriptive. Every sentence either defines a task, names an artifact, or states a constraint.

## Pre-Output Validation Checklist — Execute Every Check

Before returning the JSON, verify each of these. If any check fails, fix it before outputting:

1. **No sequential indicators in tasks:** Scan every task string. None starts with a digit followed by "." or ")". None contains "First,", "Then ", "Next,", "After that", "Finally,", "Subsequently", "Lastly". If found, rewrite the task. **Additionally: verify that the tasks in each phase read naturally in any order. If task 3 only makes sense after task 2, either merge them, add an artifact reference, or move one to a different phase.**
2. **No banned words in deliverables:** Scan every deliverable for "working", "complete", "functional", "ready", "done", "basic", "simple", "proper", "fully", "successful", "accessible", "operational". If found, replace with a specific verb + artifact. **Check deployment-phase deliverables especially carefully.**
3. **Every example_input and example_output is concrete and format-appropriate:** Not "the API works" but the actual curl command and JSON. Not "the page loads" but what components render at what URL. **Verify that every phase's example_output matches one of the six format templates above (setup/CLI, database, API, UI, export, deployment). If it matches none, rewrite it.**
4. **Every commit_condition starts with an action verb and contains a copy-pasteable command** with specific expected output (numbers, strings, status codes).
5. **Every task is ≥6 words and starts with an action verb.**
6. **Phase count is between 6 and 12.** Count them. If outside range, merge or split.
7. **No phase has fewer than 2 or more than 7 tasks.** Count tasks per phase. Split any phase with 8+ tasks.
8. **The plan is COMPLETE.** The JSON closes properly. The final phase exists and covers deployment or documentation. No phase is cut off mid-content.
9. **Deliverables name specific artifacts** — file paths, endpoints, CLI commands, URLs. No deliverable is a vague description of a feature.
10. **Tasks within each phase do not imply ordering** unless one task explicitly references another task's artifact within the same phase.
11. **Example I/O format matches phase type.** Database phases show schemas/queries. API phases show curl + JSON. UI phases describe browser rendering. CLI phases show terminal output. No phase uses a mismatched format.

## JSON Output Only

Return only the JSON object. No preamble, no explanation, no markdown fences around the entire response. The JSON may contain markdown in string values (e.g., code in example_output fields). Ensure the JSON is complete and syntactically valid — all arrays and objects properly closed.

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
