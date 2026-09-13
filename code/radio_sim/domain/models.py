"""模拟器公开且低依赖的数据对象。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite


class ProblemType(str, Enum):
    Q3 = "Q3"
    Q4 = "Q4"

    @classmethod
    def coerce(cls, value: "ProblemType | str") -> "ProblemType":
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).upper())
        except ValueError as exc:
            raise ValueError("problem must be 'Q3' or 'Q4'") from exc


class MeasureStatus(str, Enum):
    NO_SIGNAL = "no_signal"
    NEAR = "near"
    DIRECTION = "direction"


class ClearStatus(str, Enum):
    SUCCESS = "success"
    NO_TARGET_IN_RANGE = "no_target_in_range"


@dataclass(frozen=True, slots=True)
class Position:
    x: float
    y: float

    def __post_init__(self) -> None:
        x = float(self.x)
        y = float(self.y)
        if not isfinite(x) or not isfinite(y):
            raise ValueError("position coordinates must be finite")
        object.__setattr__(self, "x", 0.0 if x == 0.0 else x)
        object.__setattr__(self, "y", 0.0 if y == 0.0 else y)


@dataclass(frozen=True, slots=True)
class EnvironmentState:
    current_position: Position
    current_channel: int
    virtual_time_s: float
    is_active: bool
    is_finished: bool


@dataclass(frozen=True, slots=True)
class MeasureResult:
    status: MeasureStatus
    angle_deg: float | None
    action_time_s: float
    virtual_time_s: float


@dataclass(frozen=True, slots=True)
class ClearResult:
    status: ClearStatus
    action_time_s: float
    virtual_time_s: float


@dataclass(frozen=True, slots=True)
class StrategyResult:
    strategy_name: str
    completed: bool = True
    note: str = ""


@dataclass(frozen=True, slots=True)
class SimulationMetrics:
    seed: int
    problem: ProblemType
    strategy_name: str
    source_count: int
    cleared_count: int
    cleared_ratio: float
    all_cleared: bool
    virtual_time_s: float
    average_localize_clear_time_s: float | None
    total_distance_m: float
    measure_count: int
    clear_count: int
    failed_clear_count: int
    channel_switch_count: int
    strategy_completed: bool
    wall_time_s: float

    def to_record(self) -> dict[str, object]:
        return {
            "seed": self.seed,
            "problem": self.problem.value,
            "strategy_name": self.strategy_name,
            "source_count": self.source_count,
            "cleared_count": self.cleared_count,
            "cleared_ratio": self.cleared_ratio,
            "all_cleared": self.all_cleared,
            "virtual_time_s": self.virtual_time_s,
            "average_localize_clear_time_s": self.average_localize_clear_time_s,
            "total_distance_m": self.total_distance_m,
            "measure_count": self.measure_count,
            "clear_count": self.clear_count,
            "failed_clear_count": self.failed_clear_count,
            "channel_switch_count": self.channel_switch_count,
            "strategy_completed": self.strategy_completed,
            "wall_time_s": self.wall_time_s,
        }
