---
name: phase-compiler
description: "Converts a software project idea into a structured, phased execution plan. Collects project details (name, language, runtime, architecture, scaling, constraints), then generates a validated plan with 6–12 phases. Each phase includes a title, deliverable, task list, commit condition, and example I/O. Use when the user wants to plan a project, create a development roadmap, break work into implementable phases, or structure a new product."
license: MIT
metadata:
  author: CypherGuy
  version: "0.1.0"
---

# Phase Compiler — Project Planning Skill

## When to Activate

Trigger phrases: "plan my project", "break into phases", "development roadmap", "phase out", "how do I structure", "project plan", "planning a", "create a roadmap"

If uncertain, ask the user to confirm they want a phased project plan.

---

## Workflow

### Step 1: Collect Project Details

Ask the user for project information. Use these fields:

**Required:**

- `name` (project name, max 50 chars)
- `description` (what the project does, max 1000 chars)
- `done` (1+ completion conditions — what makes "done"?)

**With Defaults:**

- `main_user` (who uses it? default: "Just Myself")
- `language` (default: "python")
- `runtime` (cli / web / mobile / desktop / library; default: "cli")
- `phase_count` (integer 6–12; default: 7)
- `architecture` (microservices / event_driven / serverless / other; default: "other")
- `scaling_strategy` (none / vertical / horizontal / serverless / auto; default: "none")
- `starting_point` (nothing / existing / prototype / mvp; default: "nothing")

**Optional:**

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

## Communication Style

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
