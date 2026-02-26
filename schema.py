
from enum import Enum
from pydantic import BaseModel, Field


class ArchitectureStyle(str, Enum):
    microservices = "microservices"
    event_driven = "event_driven"
    serverless = "serverless"
    other = "other"


class ScalingStrategy(str, Enum):
    none = "none"
    vertical = "vertical"
    horizontal = "horizontal"
    serverless = "serverless"
    auto = "auto"


class PhaseDuration(str, Enum):
    one_to_two_hours = "1-2h"
    half_day = "half-day"
    full_day = "full-day"
    multi_day = "multi-day"


class StartingPoint(str, Enum):
    nothing = "nothing"
    existing_codebase = "existing"
    prototype = "prototype"
    mvp = "mvp"


class ProjectSpec(BaseModel):
    name: str = Field(..., title="Project name",
                      description="Name of the project", min_length=1, max_length=50)
    description: str = Field(..., title="Project description",
                             description="Description of the project", min_length=1, max_length=1000)
    main_user: str = Field(..., title="Primary user",
                           description="Who is the project's main kind of user?")
    runtime: str = Field(..., title="Runtime environment",
                         description="The runtime of the project")
    language: str = Field("python", title="The programming language used",
                          description="The language of the project")
    phase_count: int = Field(7, title="Number of phases",
                             description="The number of phases in the project", ge=6, le=12)
    done: list[str] = Field(title="Project completion requirements",
                            description="Conditions for the project to be considered finished")
    constraints: list[str] = Field([], title="Project constraints",
                                   description="The constraints of the project")

    # Architecture
    architecture: ArchitectureStyle = Field(
        ArchitectureStyle.other,
        title="Architecture style",
        description="The high-level architecture pattern for the project",
    )
    architecture_notes: str = Field(
        "",
        title="Architecture notes",
        description="Any extra detail about the planned architecture (e.g. specific frameworks, layers, patterns)",
        max_length=500,
    )

    # Scaling
    scaling_strategy: ScalingStrategy = Field(
        ScalingStrategy.none,
        title="Scaling strategy",
        description="How the project is expected to scale",
    )
    expected_scale: str = Field(
        "",
        title="Expected scale",
        description="Rough description of expected load or user count (e.g. 'single user', '10k daily active users')",
        max_length=200,
    )

    # Avoidances
    avoid: list[str] = Field(
        [],
        title="Things to avoid",
        description="Technologies, libraries, patterns, or practices the project should NOT use",
    )

    phase_duration: PhaseDuration = Field(
        PhaseDuration.half_day,
        title="Target duration per phase",
        description=(
            "Rough time budget for each phase. "
            "Claude uses this to scope the amount of work packed into a single phase."
        ),
    )
    starting_point: StartingPoint = Field(
        StartingPoint.nothing,
        title="Starting point",
        description=(
            "Describe where the project is right now."
            "Affects what the earliest phases look like — e.g. scaffolding vs. audit-and-extend."
        ),
    )


class PhaseItem(BaseModel):
    id: int
    title: str
    deliverable: str
    tasks: list[str]
    commit_condition: str
    example_input: str
    example_output: str


class PhasePlan(BaseModel):
    phases: list[PhaseItem]