"""轻量策略协议。"""

from __future__ import annotations

from typing import Protocol

from radio_sim.domain.models import StrategyResult
from radio_sim.environment.base import Environment


class Strategy(Protocol):
    def run(self, env: Environment) -> StrategyResult:
        ...
