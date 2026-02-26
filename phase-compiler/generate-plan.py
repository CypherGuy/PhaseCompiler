#!/usr/bin/env python3
import json
import sys
from schema import ProjectSpec


def generate_plan(spec: ProjectSpec) -> dict:
    """
    Takes a validated spec and generates a structured output.
    Returns a dict with the plan.
    """
    plan = {}
    phases = spec.phase_count
    plan["phases"] = []
    for i in range(1, phases+1):
        plan["phases"].append({"id": i, "title": f"Phase {i}", "deliverable": "To be filled", "tasks": [
        ], "commit_condition": "To be filled", "example_input": "To be filled", "example_output": "To be filled"},)
    plan["total_phases"] = phases

    return plan


def main():
    # Read JSON from stdin or file
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    # Validate and convert to schema
    spec = ProjectSpec(**data)

    # Generate plan
    plan = generate_plan(spec)

    # Output
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
