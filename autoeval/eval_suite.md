# Phase-Compiler Eval Suite

## Test 1: Text Legibility & Grammar (4 requirements)
- req_1: No typos in phase titles, tasks, deliverables, or commit conditions
- req_2: Consistent formatting (bullet points, capitalization, punctuation)
- req_3: Technical terms spelled correctly (FastAPI, PostgreSQL, React, etc.)
- req_4: Units and versions formatted consistently (Python 3.11, not Python3.11)
Pass condition: Zero errors across entire plan

## Test 2: Tone/Style Consistency (4 requirements)
- req_1: Language matches specified skill level (junior/mid/senior developer)
- req_2: Jargon appropriate to domain (doesn't overexplain basics to experts)
- req_3: Tone is directive and confident ("Create", "Configure", "Deploy") not tentative ("Consider", "Maybe", "Try to")
- req_4: No condescending language or unnecessary hand-holding
Pass condition: Reads like a plan from someone who knows the domain

## Test 3: Linear Flow (Logical Phase Order) (5 requirements)
- req_1: Phase 1 always covers environment setup (dependencies, tools, project scaffold)
- req_2: No phase depends on deliverables from later phases (dependency graph has no cycles)
- req_3: Infrastructure (database, auth, API foundation) comes before features that need it
- req_4: Deployment/polish/documentation is in final phases, not early
- req_5: Each phase builds on previous phases' deliverables
Pass condition: Can execute phases 1→N without backtracking

## Test 4: Free of Arbitrary Ordering (4 requirements)
- req_1: Phase numbers represent true sequence dependencies, not arbitrary ranking
- req_2: Tasks within a phase don't force sequential order unless technically required
- req_3: No unnecessary substep numbering (1.1, 1.2, 1.3) unless steps are truly sequential
- req_4: Independent tasks are presented as parallel options (bullets, not numbered lists)
Pass condition: Developer can reorder independent tasks without breaking the build

## Test 5: Deliverable Specificity (4 requirements)
- req_1: Every deliverable names a concrete artifact (file path, endpoint, CLI command, URL, or deployed service)
- req_2: Banned vague words absent: "working", "complete", "functional", "ready", "done"
- req_3: Deliverables use specific verbs: "returns", "displays", "connects", "stores", "renders"
- req_4: File paths or API routes explicitly named where applicable
Pass condition: Zero ambiguous deliverables

## Test 6: Commit Condition Testability (4 requirements)
- req_1: Every commit condition starts with an action verb (Run, Test, Deploy, Load, Query, Execute)
- req_2: Includes expected output (e.g., "pytest returns all 15 tests passing", not "tests pass")
- req_3: Conditions are binary pass/fail (no subjective "looks good")
- req_4: No commit condition is just "Phase complete" or "All tasks done"
Pass condition: 100% of commit conditions are executable commands with clear success criteria

## Test 7: Task Actionability (4 requirements)
- req_1: All tasks start with action verbs (Create, Install, Configure, Write, Deploy, Test)
- req_2: No task is fewer than 3 words (e.g., "Setup database" → "Install PostgreSQL 15 and create dev database")
- req_3: Tasks specify what to create/modify (e.g., "Write user authentication endpoint" not "Add auth")
- req_4: External dependencies named explicitly (AWS S3, Stripe API, not "cloud storage", "payment service")
Pass condition: ≥90% of tasks are unambiguous actions

## Test 8: Example I/O Presence (5 requirements)
- req_1: Every phase includes example input → output or before → after state
- req_2: API phases show example curl/request + JSON response
- req_3: UI phases describe what user sees on screen or include mockup description
- req_4: Database phases show example schema or query result
- req_5: CLI phases show command + terminal output
Pass condition: 100% of phases have concrete examples

## Test 9: Phase Count & Granularity (5 requirements)
- req_1: Total phase count is between 6–12
- req_2: Each phase represents 1–3 days of work for specified skill level
- req_3: No phase is just one task (too granular)
- req_4: No phase has >8 tasks (too coarse, should be split)
- req_5: Phases represent meaningful milestones, not arbitrary groupings
Pass condition: 6 ≤ phase count ≤ 12, balanced workload distribution

## Test 10: Dependency Explicitness (5 requirements)
- req_1: Phase 1 lists: language version, runtime, package manager, framework (if any)
- req_2: Any external service is named in first usage (e.g., "Configure AWS S3" before "Upload files to storage")
- req_3: Database choice specified before any "Create table" tasks
- req_4: Auth strategy named before "Implement login"
- req_5: No assumptions about reader's environment or tool choices
Pass condition: Zero missing dependency declarations

## Test 11: Information Retrieval (5 questions)
- q1: "What's the complete tech stack?" → Should extract: language, framework, database, deployment platform
- q2: "How do you know Phase 5 is done?" → Commit condition should provide clear, testable answer
- q3: "What does the output of Phase 3 look like?" → Example I/O should show it
- q4: "Can you start Phase 6 before Phase 4?" → Dependency structure should make this answerable (usually no)
- q5: "What external services does this project use?" → Should be extractable from tasks/constraints
Pass condition: 5/5 questions answerable from plan alone, no guessing required
