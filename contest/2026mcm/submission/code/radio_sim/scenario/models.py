from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from radio_sim.domain.models import Position, ProblemType


class SourceType(str, Enum):
    OMNIDIRECTIONAL = "omnidirectional"
    DIRECTIONAL = "directional"


@dataclass(frozen=True, slots=True)
class Source:
    channel: int
    position: Position
    receive_radius_m: float
    source_type: SourceType
    direction_deg: float | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.channel <= 20:
            raise ValueError("source channel must be in 1..20")
        if self.receive_radius_m <= 0:
            raise ValueError("receive radius must be positive")
        if self.source_type is SourceType.DIRECTIONAL:
            if self.direction_deg is None:
                raise ValueError("directional source requires direction_deg")
            object.__setattr__(self, "direction_deg", self.direction_deg % 360.0)
        elif self.direction_deg is not None:
            raise ValueError("omnidirectional source must not have direction_deg")


@dataclass(frozen=True, slots=True)
class Scenario:
    seed: int
    problem: ProblemType
    sources: tuple[Source, ...]

    def __post_init__(self) -> None:
        channels = [source.channel for source in self.sources]
        if len(channels) != len(set(channels)):
            raise ValueError("scenario source channels must be unique")

    def source_by_channel(self) -> dict[int, Source]:
        return {source.channel: source for source in self.sources}
