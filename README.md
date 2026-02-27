# PhaseCompiler

A Claude skill for converting software project ideas into structured, phased execution plans.

## Table of Contents

- [The Process](#the-process)
- [Why This Skill?](#why-this-skill)
- [Installation](#installation)
- [Usage](#usage)
- [Best Practices](#best-practices)
  - [Claude Projects](#projects)
  - [Output](#output)
- [File Structure](#file-structure)
- [License](#license)

## The process

First, you describe your project idea. Claude may ask you some questions around programming languages, runtime, architecture or constraints. After those are answered, you get a validated JSON schema, which you can view in schema.py, with 6-12 sequential phases.

Each 'phase' consists of a series of actionable and testable tasks that can help you visualise how to go from nothing to a working product. Each phase includes:

- **Title**: Meaningful phase purpose
- **Deliverable**: Concrete output (working code, tests, docs)
- **Tasks**: Actionable 3–5 step checklist
- **Commit Condition**: When the phase is complete
- **Example I/O**: Data flow in and out to help you better understand the idea

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

## Why This Skill?

Sometimes when I set down and program, I just have no idea where to begin. I may not have a clear idea of what I want to build, or I may have no clue how to structure it.

This skill helps me with that, and is:

- **High enough** to see the full journey in one view
- **Detailed enough** to start coding immediately after Phase 1
- **Flexible enough** to adapt based on project type, language, architecture, and constraints

---

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

## Best Practices

### Projects

Create a Claude Project for your development work. Add:

1. This skill (upload the `.zip` or add via `/skills add`)
2. Any existing project documentation, design docs, API specs, or requirements
3. Project instructions like: "When I ask for help planning a feature, use the phase-compiler skill"

You can also set a global default instruction at **Settings > General > What personal preferences should Claude consider...?** with something like: "Use the phase-compiler skill whenever I ask to plan, structure, or roadmap a project."

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

You can then:

- Copy the plan directly into a Markdown document
- Display the result as a live dashboard
- Export as `plan.json`
- Treat it as version control, diffing and versioning phases
- Ask Claude to adjust individual phases

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
