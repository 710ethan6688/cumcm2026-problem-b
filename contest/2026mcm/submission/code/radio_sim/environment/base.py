from __future__ import annotations

from typing import Protocol, runtime_checkable

from radio_sim.domain.models import (
    ClearResult,
    EnvironmentState,
    MeasureResult,
    Position,
)


class EnvironmentStateError(RuntimeError):
    """当动作不符合环境生命周期时抛出"""


class InvalidActionError(ValueError):
    """当动作参数超出公开协议约束时抛出"""


@runtime_checkable
class Environment(Protocol):
    @property
    def state(self) -> EnvironmentState:
        ...

    @property
    def current_position(self) -> Position:
        ...

    @property
    def current_channel(self) -> int:
        ...

    @property
    def virtual_time_s(self) -> float:
        ...

    def enter(self) -> EnvironmentState:
        ...

    def measure(self, position: Position, channel: int) -> MeasureResult:
        ...

    def clear(self, position: Position, channel: int) -> ClearResult:
        ...

    def exit(self) -> EnvironmentState:
        ...
