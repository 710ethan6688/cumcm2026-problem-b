"""独立于策略实现的评价指标构造。"""

from __future__ import annotations

from radio_sim.domain.models import ProblemType, SimulationMetrics, StrategyResult
from radio_sim.environment.local import LocalEnvironment


def build_metrics(
    env: LocalEnvironment,
    seed: int,
    problem: ProblemType,
    strategy_result: StrategyResult,
    wall_time_s: float,
) -> SimulationMetrics:
    diagnostics = env._evaluation_snapshot()
    cleared_ratio = diagnostics.cleared_count / diagnostics.source_count
    average_time = (
        env.virtual_time_s / diagnostics.cleared_count
        if diagnostics.cleared_count
        else None
    )
    return SimulationMetrics(
        seed=seed,
        problem=problem,
        strategy_name=strategy_result.strategy_name,
        source_count=diagnostics.source_count,
        cleared_count=diagnostics.cleared_count,
        cleared_ratio=cleared_ratio,
        all_cleared=diagnostics.cleared_count == diagnostics.source_count,
        virtual_time_s=env.virtual_time_s,
        average_localize_clear_time_s=average_time,
        total_distance_m=diagnostics.total_distance_m,
        measure_count=diagnostics.measure_count,
        clear_count=diagnostics.clear_count,
        failed_clear_count=diagnostics.failed_clear_count,
        channel_switch_count=diagnostics.channel_switch_count,
        strategy_completed=strategy_result.completed,
        wall_time_s=wall_time_s,
    )
