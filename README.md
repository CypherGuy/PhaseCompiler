# PhaseCompiler

A CLI tool that turns your project specification into a structured, execution plan that's split into phases using Claude AI. Instead of vague ideas, you get an actionable roadmap broken into 6–12 concrete phases, each with deliverables, tasks, commit conditions, and examples.

## The Process

PhaseCompiler works in three steps via three commands:

1. **`phasecompiler init`** — Answer a series of questions about your project (name, tech stack, constraints, architecture, scaling, etc.) and save a structured `spec.json`
2. **`phasecompiler compile`** — Validate your spec and generate a skeleton `plan.json` with TBD placeholders for each phase
3. **`phasecompiler fill`** — Call Claude Haiku API to intelligently fill in each phase with:
   - **Deliverable**: What's the concrete output of this phase?
   - **Tasks**: What needs to be done?
   - **Commit Condition**: How do you know this phase is complete?
   - **Example Input/Output**: Real examples of the phase in action

Claude receives your full spec and a summary of previously completed phases, ensuring each phase is contextual and builds on earlier work. All three phases are filled with a single API call per phase, making it quick, clean and cost-efficient.

## Why This Tool

Sometimes when I set down and program, I just have no idea where to begin. I may not have a clear idea of what I want to build, or I may have no clue how to structure it. Just telling an AI to "Add auth" or "refactor" doesn't clarify scope, dependencies, or deliverables, which is where this tool comes in. PhaseCompiler:

- Forces you to define what "done" means, what constraints matter, and what your architecture looks like
- Ensures each phase is scoped relative to your tech choices, timeline, and previous work
- Saves time: Claude can generate deliverables, tasks, commit conditions, and initial phases in around 10-15 seconds
- Cives you examples for each phase to clarify expectations
- Costs 1 API call per phase - not 5 separate calls for deliverable, tasks, etc.

Unlike the Claude skill (which integrates into Claude Desktop or Claude Projects) in the main branch, PhaseCompiler is a standalone tool you can run from the terminal. It only needs your Anthropic API key.

## Installation

### Prerequisites

- **Python 3.12+**
- **uv** (fast Python package manager) — [install here](https://docs.astral.sh/uv/getting-started/installation/)
- **Anthropic API key** — [get one here](https://console.anthropic.com/)

### Steps

1. **Clone the repo:**

   ```bash
   git clone https://github.com/CypherGuy/phase-compiler.git
   cd phase-compiler
   ```

2. **Install dependencies:**

   ```bash
   uv sync
   ```

3. **Set your API key:**

   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

4. **Verify installation:**
   ```bash
   uv run phasecompiler --help
   ```

## Usage

### Workflow: `init` → `compile` → `fill`

#### 1. Initialize a Project

Start with interactive questions about your project:

```bash
uv run phasecompiler init
```

This prompts you for:

- Project name & description
- Tech stack (runtime, language)
- Phase count (6–12)
- Completion criteria (what does "done" mean?)
- Constraints (For example if you don't want auth)
- Architecture style & notes
- How you wish to scale & expected scale (requests/second, amount of users, etc.)
- Things to avoid (Things you don't want to use, technologies/patterns in particular)
- How long each phase should take and where you're starting

Your answers are saved to `phasecompiler/spec.json`.

#### 2. Compile the Spec

Validate your spec and generate a skeleton plan:

```bash
uv run phasecompiler compile
```

This outputs `phasecompiler/plan.json` with TBD placeholders:

```json
{
  "phases": [
    {
      "id": 1,
      "title": "Phase 1",
      "deliverable": "TBD",
      "tasks": [],
      "commit_condition": "TBD",
      "example_input": "TBD",
      "example_output": "TBD"
    }
    // ... phases 2–6 (or however many you specified)
  ]
}
```

#### 3. Fill with Claude

Call Claude to fill in each phase:

```bash
uv run phasecompiler fill
```

Claude processes each phase with your full spec and a summary of previous phases. The result overwrites `phasecompiler/plan.json` with concrete details:

```json
{
  "phases": [
    {
      "id": 1,
      "title": "Phase 1: Project Setup",
      "deliverable": "Initialized Flask project with SQLite database and basic directory structure",
      "tasks": [
        "Create Python project structure with virtual environment",
        "Set up Flask app with basic routes",
        "Initialize SQLite database with schema for habits"
      ],
      "commit_condition": "Flask server starts and serves a basic index page; database tables created",
      "example_input": "Running `flask run` after project setup",
      "example_output": "Server starts on localhost:5000; landing page loads"
    }
    // All the rest of the phases
  ]
}
```

You can then:

- Copy the plan directly into a Markdown document
- Export as plan.json
- Extract a checklist (tasks only)
- Ask Claude to adjust individual phases

If you want to quickly init, compile, and fill in sequence, just chain using &&:

```bash
uv run phasecompiler init && uv run phasecompiler compile && uv run phasecompiler fill
```

## Example: HabitFlow

Here's a real example output from the included `phasecompiler/spec.json`:

**Project:** HabitFlow — A habit tracker where users build streaks

**Phases Generated:**

1. **Backend Setup** — Flask project, SQLite schema, basic API routes
2. **Frontend** — React UI for creating habits, marking complete
3. **Habit Logic** — Core completion tracking, streak calculation
4. **Streak Visualization** — Display streak counts and progress
5. **Calendar View** — Visual calendar of completed habits
6. **Polish** — Offline-first features, error handling, refinements

Each phase includes concrete deliverables, tasks, and examples. You can then hand this to developers or use it as your own roadmap. You can see the full plan in `phasecompiler/plan.json`

## Best Practices

### 1. Be Specific About Constraints & Avoidances

- **Constraints**: "Must work offline", "Single-account only", "No third-party auth"
- **Avoidances**: "No Kubernetes", "No real-time sync", "No custom CSS"

The more you specify, the better Claude can scope phases.

### 2. Define "Done" Upfront

The main thing is to make sure you're specific:

- "Users can create habits and mark them complete daily"
- "Streak counter increments correctly"

- ❌ "Habit tracker is working" (This is too vague)

### 3. Choose Realistic Phase Durations

- **1-2h**: Small, focused features (e.g., "Add login button")
- **Half-day**: Moderate features (e.g., "Habit creation + UI")
- **Full-day**: Larger features (e.g., "Payment integration")
- **Multi-day**: Major subsystems (e.g., "Complete auth system")

If you're like me and just want quicker wins, go with 1-2h

### 4. Set an Appropriate Phase Count

- **6 phases**: Small projects, simple features, quick MVPs
- **8–10 phases**: Medium projects, multiple features, a few dependencies
- **12 phases**: Large projects, complex architecture, many independent tracks

Recall that PhaseCompiler supports up to 12 phases.

### 5. Run `fill` When You're Ready

The `compile` step is fast (no API calls). Run `fill` only when your spec is finalized. Filling each phase costs around $0.002 in API fees from testing.

## File Structure

```
phase-compiler/
├── phasecompiler/
│   ├── __init__.py
│   ├── cli.py                 # CLI commands: init, compile, fill
│   ├── schema.py              # Pydantic models for spec & plan validation
│   ├── ai_filler.py           # Claude API integration & phase generation
│   ├── spec.json              # Your project specification (created by init)
│   └── plan.json              # Generated phased plan (created by compile, filled by fill)
├── tests/
│   ├── test_cli.py            # Tests for compile & fill commands
│   ├── test_schema.py         # Tests for spec & plan validation
│   └── test_ai_filler.py      # Tests for AI helper functions
├── pyproject.toml             # Dependencies & project metadata
├── uv.lock                    # Locked dependency versions
└── README.md                  # This file
```

## Environment Variables

- **`ANTHROPIC_API_KEY`** (required): Your Anthropic API key. Set before running:
  ```bash
  export ANTHROPIC_API_KEY="sk-ant-..."
  ```

## Testing

Run the test suite to verify everything works:

```bash
uv run pytest
```

## Contributing

Pull requests are welcome!

## License

MIT
