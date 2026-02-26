from pydantic import ValidationError
from phasecompiler.schema import (
    ProjectSpec,
    ArchitectureStyle,
    ScalingStrategy,
    PhaseDuration,
    StartingPoint,
    PhasePlan

)
import typer
import json
import sys
from pathlib import Path
from phasecompiler.ai_filler import fill_plan


app = typer.Typer(help="PhaseCompiler")


def _prompt_list(prompt_text: str, required: bool = False) -> list[str]:
    """Collect multiple string entries until the user submits an empty line."""
    items = []
    while True:
        entry = typer.prompt(
            f"{prompt_text} (leave blank to finish)", default="")
        if not entry:
            if required and not items:
                typer.echo("At least one entry is required.")
                continue
            break
        items.append(entry)
    return items


def _prompt_enum(prompt_text: str, enum_cls, default) -> str:
    """Prompt for one of the valid enum values, showing choices."""
    choices = [e.value for e in enum_cls]
    choices_str = ", ".join(choices)
    while True:
        value = typer.prompt(
            f"{prompt_text} ({choices_str})", default=default.value)
        if value in choices:
            return value
        typer.echo(f"Invalid choice. Pick one of: {choices_str}")


def _create_spec(
    name: str,
    description: str,
    main_user: str,
    runtime: str,
    language: str,
    phase_count: int,
    done: list[str],
    constraints: list[str],
    architecture: str,
    architecture_notes: str,
    scaling_strategy: str,
    expected_scale: str,
    avoid: list[str],
    phase_duration: str,
    starting_point: str,
) -> dict:
    """Create and save a ProjectSpec with the given parameters."""
    output = ProjectSpec(
        name=name,
        description=description,
        main_user=main_user,
        runtime=runtime,
        language=language,
        phase_count=phase_count,
        done=done,
        constraints=constraints,
        architecture=ArchitectureStyle(architecture),
        architecture_notes=architecture_notes,
        scaling_strategy=ScalingStrategy(scaling_strategy),
        expected_scale=expected_scale,
        avoid=avoid,
        phase_duration=PhaseDuration(phase_duration),
        starting_point=StartingPoint(starting_point),
    )

    typer.echo("\nProject spec:")
    typer.echo(output.model_dump_json(indent=4))

    with open("phasecompiler/spec.json", "w") as f:
        json.dump(output.model_dump(), f, indent=4)

    return output.model_dump()


def _generate_plan(file: Path) -> dict:
    """Generate a phased plan from a spec file."""
    with open(file, "r") as f:
        spec = json.load(f)

    try:
        spec_obj = ProjectSpec(**spec)
    except ValidationError as e:
        raise ValueError(f"Spec validation failed: {e}")

    plan = {}
    plan["phases"] = []
    for i in range(1, spec_obj.phase_count+1):
        plan["phases"].append({"id": i, "title": f"Phase {i}", "deliverable": "TBD", "tasks": [
        ], "commit_condition": "TBD", "example_input": "TBD", "example_output": "TBD"},)

    output = PhasePlan(**plan)

    with open("phasecompiler/plan.json", "w") as f:
        json.dump(plan, f, indent=4)

    return plan


@app.command()
def init() -> dict:
    """
    Initialize a new project spec
    """
    typer.echo("Starting PhaseCompiler setup...")

    name = typer.prompt("What is the name of your project?")
    desc = typer.prompt("Please provide a short description of your project")
    main_user = typer.prompt(
        "Who is the main user of your project?", default="Just Myself")
    runtime = typer.prompt(
        "What is the runtime environment of your project?", default="cli")
    language = typer.prompt(
        "What is the programming language of your project?", default="python")
    while True:
        phases = typer.prompt(
            "How many phases does your project have? (6–12)", type=int, default=7)
        if 6 <= phases <= 12:
            break
        typer.echo("Phases must be between 6 and 12.")

    typer.echo("Enter 1+ completion conditions (what makes the project 'done'?):")
    done = _prompt_list("Condition", required=True)

    typer.echo("Enter any project constraints (optional):")
    constraints = _prompt_list("Constraint")

    # Architecture
    typer.echo("\n--- Architecture ---")
    architecture = _prompt_enum(
        "Architecture style", ArchitectureStyle, ArchitectureStyle.other)
    architecture_notes = typer.prompt(
        "Any extra architecture notes? (frameworks, layers, patterns — leave blank to skip)",
        default="")

    # Scaling
    typer.echo("\n--- Scaling ---")
    scaling_strategy = _prompt_enum(
        "Scaling strategy", ScalingStrategy, ScalingStrategy.none)
    expected_scale = typer.prompt(
        "Expected scale / load description (e.g. 'single user', '10k daily requests' — leave blank to skip)",
        default="")

    # Avoidances
    typer.echo("\n--- Things to avoid ---")
    typer.echo("List technologies, libraries, patterns, or practices to avoid:")
    avoid = _prompt_list("Avoid")

    # Phase generation context
    typer.echo("\n--- Phase generation ---")

    phase_duration = _prompt_enum(
        "Target duration per phase (Claude uses this to scope each phase's workload)",
        PhaseDuration,
        PhaseDuration.half_day,
    )
    starting_point = _prompt_enum(
        "Starting point (shapes what the first phases look like)",
        StartingPoint,
        StartingPoint.nothing,
    )

    return _create_spec(
        name=name,
        description=desc,
        main_user=main_user,
        runtime=runtime,
        language=language,
        phase_count=phases,
        done=done,
        constraints=constraints,
        architecture=architecture,
        architecture_notes=architecture_notes,
        scaling_strategy=scaling_strategy,
        expected_scale=expected_scale,
        avoid=avoid,
        phase_duration=phase_duration,
        starting_point=starting_point,
    )


@app.command()
def compile(file: Path = typer.Argument(Path("phasecompiler/spec.json"))):
    """
    loads spec.json and validates it against ProjectSpec
    """
    try:
        plan = _generate_plan(file)
        typer.echo("Compilation successful.")
        typer.echo(json.dumps(plan, indent=4))
        return plan
    except ValueError as e:
        typer.echo(f"Error: {e}")
        sys.exit(1)


@app.command()
def fill():
    """
Takes an existing plan.json
Uses the AI module to fill in TBD fields
Outputs updated plan.json
"""
    plan_path = Path("phasecompiler/plan.json")
    with open(plan_path, "r") as f:
        plan = json.load(f)

    with open("phasecompiler/spec.json", "r") as f:
        spec_data = json.load(f)

    spec = ProjectSpec(**spec_data)
    filled = fill_plan(spec, plan)

    with open(plan_path, "w") as f:
        json.dump(filled, f, indent=4)

    typer.echo("Plan filled successfully.")
    typer.echo(json.dumps(filled, indent=4))


if __name__ == "__main__":
    app()
