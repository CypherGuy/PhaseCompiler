import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from phasecompiler.cli import app
from phasecompiler.schema import (
    ArchitectureStyle,
    PhaseDuration,
    PhasePlan,
    ProjectSpec,
    ScalingStrategy,
    StartingPoint,
)

sys.path.insert(0, str(Path(__file__).parent.parent))

runner = CliRunner()

_BASE_SPEC = {
    "name": "MyProject",
    "description": "A sample project description",
    "main_user": "developer",
    "runtime": "cli",
    "language": "python",
    "done": ["shipped"],
    "architecture": "other",
    "architecture_notes": "",
    "scaling_strategy": "none",
    "expected_scale": "",
    "phase_duration": "half-day",
    "starting_point": "nothing",
}


def test_compile_generates_correct_phase_count(tmp_path, monkeypatch):
    """compile should generate n phases matching phase_count from spec.json."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "phasecompiler").mkdir()

    # Create a spec with 7 phases
    spec = {**_BASE_SPEC, "phase_count": 7}
    spec_path = tmp_path / "phasecompiler" / "spec.json"
    spec_path.write_text(json.dumps(spec))

    result = runner.invoke(app, ["compile", str(spec_path)])

    assert result.exit_code == 0
    assert "Compilation successful" in result.output

    # Verify plan.json was created
    plan_path = tmp_path / "phasecompiler" / "plan.json"
    assert plan_path.exists()

    # Verify plan has correct number of phases
    plan = json.loads(plan_path.read_text())
    assert len(plan["phases"]) == 7


def test_compile_phase_structure(tmp_path, monkeypatch):
    """Each phase should have id, title, deliverable, tasks, commit_condition, example_input, example_output."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "phasecompiler").mkdir()

    spec = {**_BASE_SPEC, "phase_count": 6}
    spec_path = tmp_path / "phasecompiler" / "spec.json"
    spec_path.write_text(json.dumps(spec))

    result = runner.invoke(app, ["compile", str(spec_path)])

    assert result.exit_code == 0

    plan_path = tmp_path / "phasecompiler" / "plan.json"
    plan = json.loads(plan_path.read_text())

    # Check each phase has required fields
    for i, phase in enumerate(plan["phases"], 1):
        assert phase["id"] == i
        assert phase["title"] == f"Phase {i}"
        assert "deliverable" in phase
        assert "tasks" in phase
        assert isinstance(phase["tasks"], list)
        assert "commit_condition" in phase
        assert "example_input" in phase
        assert "example_output" in phase


def test_compile_validates_against_phase_plan_schema(tmp_path, monkeypatch):
    """Generated plan should validate against PhasePlan schema."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "phasecompiler").mkdir()

    spec = {**_BASE_SPEC, "phase_count": 8}
    spec_path = tmp_path / "phasecompiler" / "spec.json"
    spec_path.write_text(json.dumps(spec))

    result = runner.invoke(app, ["compile", str(spec_path)])

    assert result.exit_code == 0

    plan_path = tmp_path / "phasecompiler" / "plan.json"
    plan = json.loads(plan_path.read_text())

    # This should not raise ValidationError
    phase_plan = PhasePlan(**plan)
    assert len(phase_plan.phases) == 8


def test_compile_outputs_plan_to_terminal(tmp_path, monkeypatch):
    """compile should output the generated plan.json to the terminal."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "phasecompiler").mkdir()

    spec = {**_BASE_SPEC, "phase_count": 6}
    spec_path = tmp_path / "phasecompiler" / "spec.json"
    spec_path.write_text(json.dumps(spec))

    result = runner.invoke(app, ["compile", str(spec_path)])

    assert result.exit_code == 0
    # Verify plan is in output
    assert '"phases"' in result.output
    assert '"id"' in result.output
    assert '"title"' in result.output


def test_compile_rejects_invalid_spec(tmp_path, monkeypatch):
    """compile should gracefully reject invalid spec.json."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "phasecompiler").mkdir()

    # Missing required field "done"
    invalid_spec = {
        "name": "MyProject",
        "description": "A sample project description",
        "main_user": "developer",
        "runtime": "cli",
        "language": "python",
        "phase_count": 7,
        # Missing "done"
    }
    spec_path = tmp_path / "phasecompiler" / "spec.json"
    spec_path.write_text(json.dumps(invalid_spec))

    result = runner.invoke(app, ["compile", str(spec_path)])

    assert result.exit_code == 1
    assert "Spec validation failed" in result.output


def test_compile_boundary_phase_counts(tmp_path, monkeypatch):
    """compile should work with phase_count at valid boundaries (6 and 12)."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "phasecompiler").mkdir()

    for phase_count in [6, 12]:
        spec = {**_BASE_SPEC, "phase_count": phase_count}
        spec_path = tmp_path / "phasecompiler" / f"spec_{phase_count}.json"
        spec_path.write_text(json.dumps(spec))

        result = runner.invoke(app, ["compile", str(spec_path)])

        assert result.exit_code == 0
        plan_path = tmp_path / "phasecompiler" / "plan.json"
        plan = json.loads(plan_path.read_text())
        assert len(plan["phases"]) == phase_count


def test_compile_file_not_found(tmp_path, monkeypatch):
    """compile should handle missing spec.json gracefully."""
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["compile", "/nonexistent/spec.json"])

    assert result.exit_code != 0
