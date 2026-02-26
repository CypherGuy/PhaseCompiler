import json
import tempfile
from pathlib import Path

import pytest

from phasecompiler.cli import _generate_plan


class TestCompileCommand:
    """Test compile command functionality."""

    def test_generate_plan_creates_tbd_values(self):
        """Test that _generate_plan creates TBD placeholders."""
        spec = {
            "name": "TestProject",
            "description": "A test project",
            "main_user": "Test User",
            "runtime": "CLI",
            "language": "Python",
            "phase_count": 6,
            "done": ["Feature complete"],
            "constraints": [],
            "architecture": "other",
            "architecture_notes": "",
            "scaling_strategy": "none",
            "expected_scale": "",
            "avoid": [],
            "phase_duration": "1-2h",
            "starting_point": "nothing",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(spec, f)
            f.flush()

            plan = _generate_plan(Path(f.name))

            assert len(plan["phases"]) == 6
            assert all(p["deliverable"] == "TBD" for p in plan["phases"])
            assert all(p["commit_condition"] == "TBD" for p in plan["phases"])
            assert all(p["example_input"] == "TBD" for p in plan["phases"])
            assert all(p["example_output"] == "TBD" for p in plan["phases"])

    def test_generate_plan_phase_numbering(self):
        """Test that phases are numbered correctly."""
        spec = {
            "name": "Test",
            "description": "Test",
            "main_user": "User",
            "runtime": "CLI",
            "language": "Python",
            "phase_count": 6,
            "done": ["Done"],
            "constraints": [],
            "architecture": "other",
            "scaling_strategy": "none",
            "phase_duration": "1-2h",
            "starting_point": "nothing",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(spec, f)
            f.flush()

            plan = _generate_plan(Path(f.name))

            phase_ids = [p["id"] for p in plan["phases"]]
            assert phase_ids == [1, 2, 3, 4, 5, 6]

    def test_generate_plan_phase_titles(self):
        """Test that phase titles are correct."""
        spec = {
            "name": "Test",
            "description": "Test",
            "main_user": "User",
            "runtime": "CLI",
            "language": "Python",
            "phase_count": 6,
            "done": ["Done"],
            "constraints": [],
            "architecture": "other",
            "scaling_strategy": "none",
            "phase_duration": "1-2h",
            "starting_point": "nothing",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(spec, f)
            f.flush()

            plan = _generate_plan(Path(f.name))

            titles = [p["title"] for p in plan["phases"]]
            assert titles == ["Phase 1", "Phase 2",
                              "Phase 3", "Phase 4", "Phase 5", "Phase 6"]

    def test_generate_plan_empty_tasks(self):
        """Test that tasks list starts empty."""
        spec = {
            "name": "Test",
            "description": "Test",
            "main_user": "User",
            "runtime": "CLI",
            "language": "Python",
            "phase_count": 6,
            "done": ["Done"],
            "constraints": [],
            "architecture": "other",
            "scaling_strategy": "none",
            "phase_duration": "1-2h",
            "starting_point": "nothing",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(spec, f)
            f.flush()

            plan = _generate_plan(Path(f.name))

            assert all(p["tasks"] == [] for p in plan["phases"])

    def test_generate_plan_invalid_spec(self):
        """Test that invalid spec raises error."""
        spec = {
            "name": "Test",
            "description": "Test",
            # Missing required fields
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(spec, f)
            f.flush()

            with pytest.raises(ValueError, match="Spec validation failed"):
                _generate_plan(Path(f.name))

    def test_generate_plan_missing_file(self):
        """Test handling of missing spec file."""
        with pytest.raises(FileNotFoundError):
            _generate_plan(Path("/nonexistent/path/spec.json"))
