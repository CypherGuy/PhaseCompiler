import json
import time
import anthropic

from phasecompiler.schema import ProjectSpec


def call_anthropic_api(prompt):
    message = anthropic.Anthropic().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content


def _extract_text(content_blocks):
    """Extract text from content blocks, returning first text block found."""
    for block in content_blocks:
        if hasattr(block, "text"):
            return block.text
    return ""


def _strip_code_fences(text: str) -> str:
    """Strip markdown code fences if the model wrapped its JSON response."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1])
    return text.strip()


def _build_prior_phases_summary(completed_phases: list[dict]) -> str:
    if not completed_phases:
        return "None yet."
    return "\n".join(
        f"  Phase {p['id']}: {p['deliverable']}" for p in completed_phases
    )


def generate_phase(spec: ProjectSpec, phase_num: int, completed_phases: list[dict]) -> dict:
    prior_summary = _build_prior_phases_summary(completed_phases)
    prompt = f"""You are planning a software project phase by phase.

Project: {spec.name}
Description: {spec.description}
Language: {spec.language}
Runtime: {spec.runtime}
Architecture: {spec.architecture}
Constraints: {", ".join(spec.constraints) if spec.constraints else "None"}
Avoid: {", ".join(spec.avoid) if spec.avoid else "None"}
Phase duration: {spec.phase_duration}
Total phases: {spec.phase_count}
Done when: {", ".join(spec.done)}

Phases completed so far:
{prior_summary}

Now generate Phase {phase_num} of {spec.phase_count}.

Return only valid JSON with this exact structure:
{{
  "deliverable": "short description of what is produced",
  "tasks": ["task 1", "task 2", "task 3"],
  "commit_condition": "what must be true to consider this phase done",
  "example_input": "example of input at this phase",
  "example_output": "example of output at this phase"
}}"""

    response = call_anthropic_api(prompt)
    return json.loads(_strip_code_fences(_extract_text(response)))


def fill_plan(spec: ProjectSpec, plan: dict) -> dict:
    """Generate phase details with progress updates."""
    total_phases = len(plan["phases"])
    completed_phases = []
    last_update = time.time()

    for phase in plan["phases"]:
        phase_num = phase["id"]

        # Print progress every 5 seconds
        current_time = time.time()
        if current_time - last_update >= 5:
            print(
                f"\n[Progress] Processing phase {phase_num} of {total_phases}...")
            last_update = current_time

        generated = generate_phase(spec, phase_num, completed_phases)
        phase.update(generated)
        completed_phases.append(
            {"id": phase_num, "deliverable": phase["deliverable"]})

    return plan
