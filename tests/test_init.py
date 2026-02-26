from phasecompiler.schema import (
    ArchitectureStyle,
    PhaseDuration,
    ProjectSpec,
    ScalingStrategy,
    StartingPoint,
)
from phasecompiler.cli import app
import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent))


runner = CliRunner()

_BASE_SPEC = {
    "name": "MyProject",
    "description": "A sample project description",
    "main_user": "developer",
    "runtime": "cli",
    "done": ["shipped"],
    "architecture": ArchitectureStyle.other,
    "architecture_notes": "",
    "scaling_strategy": ScalingStrategy.none,
    "expected_scale": "",
    "phase_duration": PhaseDuration.half_day,
    "starting_point": StartingPoint.nothing,
    "phase_count": 8,
}


def test_phases_boundary_validation():
    """phases must be between 6 and 12 inclusive; anything outside is rejected."""
    for bad in (0, 5, 13, 100, -1):
        with pytest.raises(ValidationError):
            ProjectSpec(**{**_BASE_SPEC, "phase_count": bad})

    for ok in (6, 12):
        spec = ProjectSpec(**{**_BASE_SPEC, "phase_count": ok})
        assert spec.phase_count == ok


def test_name_length_constraints():
    """name must be 1–50 characters; empty and 51-char names are rejected."""
    ProjectSpec(**{**_BASE_SPEC, "name": "A" * 50})

    with pytest.raises(ValidationError):
        ProjectSpec(**{**_BASE_SPEC, "name": "A" * 51})

    with pytest.raises(ValidationError):
        ProjectSpec(**{**_BASE_SPEC, "name": ""})


def test_invalid_enum_values_rejected():
    """Unrecognised strings for enum fields must raise ValidationError."""
    with pytest.raises(ValidationError):
        ProjectSpec(**{**_BASE_SPEC, "architecture": "monolith"})

    with pytest.raises(ValidationError):
        ProjectSpec(**{**_BASE_SPEC, "scaling_strategy": "magic"})

    with pytest.raises(ValidationError):
        ProjectSpec(**{**_BASE_SPEC, "phase_duration": "3-weeks"})


def test_init_reprompts_on_out_of_range_phases(tmp_path, monkeypatch):
    """init must loop until the user supplies a phases value within [6, 12]."""
    (tmp_path / "phasecompiler").mkdir()
    monkeypatch.chdir(tmp_path)

    # phases sequence: 3 (rejected), 15 (rejected), 9 (accepted)
    user_input = "\n".join([
        "TestProject",  # name
        "A description",  # description
        "",  # main_user — accept default
        "",  # runtime — accept default
        "",  # language — accept default
        "3",  # phases — invalid, triggers re-prompt
        "15",  # phases — invalid, triggers re-prompt
        "9",  # phases — valid
        "done item",  # done condition (required: at least one)
        "",  # end done list
        "",  # end constraints
        "",  # architecture — accept default
        "",  # architecture_notes — skip
        "",  # scaling_strategy — accept default
        "",  # expected_scale — skip
        "",  # end avoid list
        "",  # phase_duration — accept default
        "",  # starting_point — accept default
    ]) + "\n"

    result = runner.invoke(app, ["init"], input=user_input)

    assert result.exit_code == 0
    assert result.output.count("Phases must be between 6 and 12.") == 2

    spec = json.loads((tmp_path / "phasecompiler" / "spec.json").read_text())
    assert spec["phase_count"] == 9
    assert spec["name"] == "TestProject"
