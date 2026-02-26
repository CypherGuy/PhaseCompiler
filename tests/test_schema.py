import pytest
from pydantic import ValidationError
from phasecompiler.schema import (
    ProjectSpec,
    PhasePlan,
    ArchitectureStyle,
    ScalingStrategy,
    PhaseDuration,
    StartingPoint,
)


class TestProjectSpec:
    """Test ProjectSpec validation."""

    def test_valid_spec(self):
        """Test creating a valid spec."""
        spec = ProjectSpec(
            name="TestProject",
            description="A test project",
            main_user="Test User",
            runtime="CLI",
            language="Python",
            phase_count=6,
            done=["Feature 1", "Feature 2"],
            constraints=[],
            architecture=ArchitectureStyle.other,
            architecture_notes="",
            scaling_strategy=ScalingStrategy.none,
            expected_scale="",
            avoid=[],
            phase_duration=PhaseDuration.half_day,
            starting_point=StartingPoint.nothing,
        )
        assert spec.name == "TestProject"
        assert spec.phase_count == 6
        assert len(spec.done) == 2

    def test_phase_count_range(self):
        """Test phase count must be between 6 and 12."""
        with pytest.raises(ValidationError):
            ProjectSpec(
                name="Test",
                description="Test",
                main_user="User",
                runtime="CLI",
                language="Python",
                phase_count=3,  # Too low
                done=["Done"],
                constraints=[],
                architecture=ArchitectureStyle.other,
                scaling_strategy=ScalingStrategy.none,
                phase_duration=PhaseDuration.half_day,
                starting_point=StartingPoint.nothing,
            )

    def test_phase_count_too_high(self):
        """Test phase count cannot exceed 12."""
        with pytest.raises(ValidationError):
            ProjectSpec(
                name="Test",
                description="Test",
                main_user="User",
                runtime="CLI",
                language="Python",
                phase_count=15,  # Too high
                done=["Done"],
                constraints=[],
                architecture=ArchitectureStyle.other,
                scaling_strategy=ScalingStrategy.none,
                phase_duration=PhaseDuration.half_day,
                starting_point=StartingPoint.nothing,
            )

    def test_done_criteria_can_be_empty(self):
        """Test that done criteria can be empty."""
        spec = ProjectSpec(
            name="Test",
            description="Test",
            main_user="User",
            runtime="CLI",
            language="Python",
            phase_count=6,
            done=[],  # Empty is allowed
            constraints=[],
            architecture=ArchitectureStyle.other,
            scaling_strategy=ScalingStrategy.none,
            phase_duration=PhaseDuration.half_day,
            starting_point=StartingPoint.nothing,
        )
        assert spec.done == []

    def test_architecture_enum_values(self):
        """Test valid architecture values."""
        valid_architectures = [
            ArchitectureStyle.microservices,
            ArchitectureStyle.event_driven,
            ArchitectureStyle.serverless,
            ArchitectureStyle.other,
        ]
        for arch in valid_architectures:
            spec = ProjectSpec(
                name="Test",
                description="Test",
                main_user="User",
                runtime="CLI",
                language="Python",
                phase_count=6,
                done=["Done"],
                constraints=[],
                architecture=arch,
                scaling_strategy=ScalingStrategy.none,
                phase_duration=PhaseDuration.half_day,
                starting_point=StartingPoint.nothing,
            )
            assert spec.architecture == arch

    def test_phase_duration_enum_values(self):
        """Test valid phase duration values."""
        valid_durations = [
            PhaseDuration.one_to_two_hours,
            PhaseDuration.half_day,
            PhaseDuration.full_day,
            PhaseDuration.multi_day,
        ]
        for duration in valid_durations:
            spec = ProjectSpec(
                name="Test",
                description="Test",
                main_user="User",
                runtime="CLI",
                language="Python",
                phase_count=6,
                done=["Done"],
                constraints=[],
                architecture=ArchitectureStyle.other,
                scaling_strategy=ScalingStrategy.none,
                phase_duration=duration,
                starting_point=StartingPoint.nothing,
            )
            assert spec.phase_duration == duration


class TestPhasePlan:
    """Test PhasePlan validation."""

    def test_valid_plan(self):
        """Test creating a valid plan."""
        plan_data = {
            "phases": [
                {
                    "id": 1,
                    "title": "Phase 1",
                    "deliverable": "Deliverable",
                    "tasks": ["Task 1"],
                    "commit_condition": "Condition",
                    "example_input": "Input",
                    "example_output": "Output",
                }
            ]
        }
        plan = PhasePlan(**plan_data)
        assert len(plan.phases) == 1
        assert plan.phases[0].id == 1

    def test_plan_phase_has_id(self):
        """Test that phases must have an id."""
        plan_data = {
            "phases": [
                {
                    "title": "Phase 1",
                    "deliverable": "Deliverable",
                    "tasks": [],
                    "commit_condition": "Condition",
                    "example_input": "Input",
                    "example_output": "Output",
                }
            ]
        }
        with pytest.raises(ValidationError):
            PhasePlan(**plan_data)

    def test_plan_with_multiple_phases(self):
        """Test plan with multiple phases."""
        plan_data = {
            "phases": [
                {
                    "id": i,
                    "title": f"Phase {i}",
                    "deliverable": "Deliverable",
                    "tasks": ["Task 1"],
                    "commit_condition": "Condition",
                    "example_input": "Input",
                    "example_output": "Output",
                }
                for i in range(1, 7)
            ]
        }
        plan = PhasePlan(**plan_data)
        assert len(plan.phases) == 6
        assert [p.id for p in plan.phases] == [1, 2, 3, 4, 5, 6]
