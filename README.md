# PhaseCompiler

A Claude skill that turns vague project ideas into execution-ready roadmaps - with explicit “definition of done”, dependency-correct sequencing, and GitHub issue automation

## Table of Contents

- [The Process](#the-process)
- [Who is this for?](#who-is-this-for)
- [Why This Skill?](#why-this-skill)
- [Why not use Claude itself?](#why-can't-i-just-use-claude-itself-to-make-me-a-plan)
- [Installation](#installation)
- [Usage](#usage)
- [Best Practices](#best-practices)
  - [Claude Projects](#projects)
  - [Output](#output)
- [GitHub Integration](#github-integration)
- [File Structure](#file-structure)
- [License](#license)

## The process

First, you describe your project idea. Claude may ask you some questions around programming languages, runtime, architecture or constraints. After those are answered, you receive a validated, dependency-ordered execution plan with 6–12 sequential phases.

Each 'phase' consists of a series of actionable and testable tasks that can help you visualise how to go from nothing to a working product. Each phase includes:

- **Title**: Meaningful phase purpose
- **Deliverable**: Concrete output (working code, tests, docs)
- **Tasks**: Actionable 3–5 step checklist
- **Commit Condition**: When the phase is complete
- **Example I/O**: Data flow in and out to help you better understand the idea

Each phase is designed to be completed in isolation and must have a clear commit condition before progressing. This stops architectural drift and having lots of unfinished features.

Example output for a web project:

```
Phase 1: Backend Setup & Database Schema
Phase 2: Core API Endpoints
Phase 3: Authentication & Authorization
Phase 4: Frontend Scaffolding
Phase 5: Feature Implementation
...
Phase N: Testing, Optimization & Deployment
```

You can see an actual JSON example in the [Output](#output) section.

Each phase builds on the previous one, meaning there's no abstract phases that aren't relevant.

The plan can be exported as a JSON file, meaning you could for example pass it into an LLM for easy visual analysis by asking it to draw you a webpage of the plan.

---

## Who is this for?

Good for:

- Those that start projects but don't finish them
- Those who can't sequence ideas properly (What should I do next?)
- Indie developers shipping MVP's
- Those who fancy a bit of discipline and structure when programming

Bad for:

- Larger teams
- Complex multi-agent workflows

## Why This Skill?

Most developers don’t struggle with ideas, or asking Claude to turn their idea into a PLAN.md. They struggle with:

- **Starting too big**
- **Shipping half-finished features**
- **Rewriting architecture mid-build**
- **Scope creep killing momentum**
- **Never defining what “done” actually means**

PhaseCompiler forces discipline into your workflow:

- **Clear MVP boundaries**
- **Explicit commit conditions**
- **Sequential, dependency-aware phases**
- **Tangible deliverables per phase**
- **Re-runnable, idempotent planning**

## Why can't I just use Claude itself to make me a plan?

You could ask an LLM to “plan my project.”, but PhaseCompiler enforces structure which is the key idea. As an example:

- Every phase must produce a concrete deliverable
- Every phase must define a measurable commit condition
- Tasks are limited to actionable 3–5 step sequences
- Phases must build sequentially — no abstract fluff
- The output schema is stable and exportable
- Plans can be imported into GitHub as milestones + issues

All of these ideas are enforced by the skill and would be way tougher to keep track of with Claude.

## Installation

### Quick Install (recommended)

1. Download the SKILL.md file
2. Upload to Claude Desktop: **Open Sidebar > Customize > Create new Skill > Upload Skill**

---

## Usage

### First starting off

You can start by asking Claude to plan a project:

> "Help me plan a project"

> "I want to build a CLI tool for managing tasks. Can you create a development roadmap?"

> "Plan out a web app that lets users track expenses"

### Specifying Details

Provide project context upfront:

> "Plan a Python web backend using FastAPI with Postgres, starting from scratch, 8 phases"

> "I'm building a mobile app in React Native. It's for myself, serverless architecture. Create a plan."

> "Plan a library/SDK in Rust with these constraints: <1 week timeline, needs comprehensive tests"

### Iterative Refinement

> "Can you expand Phase 3 with more detail on the API design?"

> "Merge phases 5 and 6 to make this 8 phases instead of 9"

> "Adjust the phases to prioritize authentication earlier"

---

## Output

The skill returns a complete plan as structured JSON that you can action on:

```json
{
  "project": {
    "name": "MyApp",
    "description": "...",
    "language": "python",
    "runtime": "web",
    ...
  },
  "phases": [
    {
      "id": 1,
      "title": "Backend Setup & Database Schema",
      "deliverable": "Running API server with database connected",
      "tasks": ["...", "...", "..."],
      "commit_condition": "API responds to health check endpoint",
      "example_input": "Project requirements",
      "example_output": "Git repo with initial project structure"
    },
    ...
  ]
}
```

The structure is stable and idempotent, meaning it can be versioned, diffed, and safely re-imported into GitHub without duplicating issues.

Once generated, you can then:

- Copy the plan directly into a Markdown document
- Display the result as a live dashboard
- Export as `plan.json`
- Treat it as version control, diffing and versioning phases
- Ask Claude to adjust individual phases

## GitHub Integration

PhaseCompiler can export your plan directly into:

- GitHub Milestones (one per phase)
- GitHub Issues (one per task)
- A GitHub Actions workflow for automated importing

The import script is idempotent — re-running it will not duplicate issues. Examples can be seen in SKILL.md

The skill will provide you with steps to get started. Commit the workflow file and the script given to main and the workflow will automatically sync your roadmap into executable GitHub work.

---

## File Structure

```
phase-compiler/
├── README.md                   # This file
├── SKILL.md                    # Main skill instructions for Claude
├── schema.py                   # Pydantic models (project spec validation)
(optional)
```

**Note**: Only `SKILL.md` is needed for the Claude skill. The Python files (`schema.py`, `generate-plan.py`) are optional utilities for batch processing or integration with external systems. For conversational use in Claude Desktop or Claude.ai, just upload the skill via SKILL.md.

If you would rather have this tool but in a CLI format, feel free to switch over the the CLI branch and clone that.

---

## License

MIT
