# phasecompiler/cli.py

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


app = typer.Typer(help="PhaseCompiler – schema-driven project planning")


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


@app.command()
def init():
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

    output = ProjectSpec(
        name=name,
        description=desc,
        main_user=main_user,
        runtime=runtime,
        language=language,
        phase_count=phases,
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


@app.command()
def compile(file: Path = Path("phasecompiler/spec.json")):
    """
    loads spec.json and validates it against ProjectSpec
    """
    with open(file, "r") as f:
        spec = json.load(f)

    try:
        spec_obj = ProjectSpec(**spec)
    except ValidationError as e:
        typer.echo(f"Spec validation failed: {e}")
        sys.exit(1)

    typer.echo("Compilation successful.")
    plan = {}

    plan["phases"] = []
    for i in range(1, spec_obj.phase_count+1):
        plan["phases"].append({"id": i, "title": f"Phase {i}", "deliverable": "TBD", "tasks": [
        ], "commit_condition": "TBD", "example_input": "TBD", "example_output": "TBD"},)

    output = PhasePlan(**plan)

    typer.echo(output.model_dump_json(indent=4))

    with open("phasecompiler/plan.json", "w") as f:
        json.dump(plan, f, indent=4)


if __name__ == "__main__":
    app()
