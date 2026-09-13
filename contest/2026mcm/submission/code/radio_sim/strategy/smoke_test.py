from __future__ import annotations

from radio_sim.domain.models import Position, StrategyResult
from radio_sim.environment.base import Environment


class SmokeTestStrategy:
    def run(self, env: Environment) -> StrategyResult:
        env.enter()
        env.measure(Position(300.0, 400.0), 1)
        env.measure(Position(300.0, 400.0), 2)
        env.clear(Position(300.0, 0.0), 3)
        env.measure(Position(300.0, 0.0), 2)
        env.exit()
        return StrategyResult(
            strategy_name=type(self).__name__,
            completed=True,
            note="environment lifecycle smoke test only",
        )
