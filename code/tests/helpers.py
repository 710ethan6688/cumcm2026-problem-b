from __future__ import annotations

from radio_sim.domain.models import Position, ProblemType
from radio_sim.environment.local import LocalEnvironment, PhysicsConfig
from radio_sim.scenario.models import Scenario, Source, SourceType


def make_source(
    channel: int = 1,
    position: Position = Position(0.0, 0.0),
    receive_radius_m: float = 1000.0,
    source_type: SourceType = SourceType.OMNIDIRECTIONAL,
    direction_deg: float | None = None,
) -> Source:
    return Source(
        channel=channel,
        position=position,
        receive_radius_m=receive_radius_m,
        source_type=source_type,
        direction_deg=direction_deg,
    )


def make_env(
    *sources: Source,
    seed: int = 123,
    problem: ProblemType = ProblemType.Q3,
    physics: PhysicsConfig | None = None,
) -> LocalEnvironment:
    scenario = Scenario(seed=seed, problem=problem, sources=tuple(sources))
    return LocalEnvironment(scenario, physics=physics)
