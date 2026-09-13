"""可复现的实验调度。"""

from __future__ import annotations

import copy
from collections.abc import Iterable
from time import perf_counter

from radio_sim.domain.models import ProblemType, SimulationMetrics
from radio_sim.environment.local import LocalEnvironment, PhysicsConfig
from radio_sim.evaluation.metrics import build_metrics
from radio_sim.scenario.config import ScenarioConfig
from radio_sim.strategy.base import Strategy


def run_single(
    strategy: Strategy,
    seed: int,
    problem: ProblemType | str,
    scenario_config: ScenarioConfig | None = None,
    physics: PhysicsConfig | None = None,
) -> SimulationMetrics:
    problem_type = ProblemType.coerce(problem)
    env = LocalEnvironment.from_seed(
        seed=seed,
        problem=problem_type,
        scenario_config=scenario_config,
        physics=physics,
    )
    started = perf_counter()
    strategy_result = strategy.run(env)
    wall_time_s = perf_counter() - started
    return build_metrics(env, seed, problem_type, strategy_result, wall_time_s)


def run_batch(
    strategy: Strategy,
    seeds: Iterable[int],
    problem: ProblemType | str,
    scenario_config: ScenarioConfig | None = None,
    physics: PhysicsConfig | None = None,
) -> list[SimulationMetrics]:
    """按给定顺序在各随机种子上运行克隆的策略实例。"""
    results: list[SimulationMetrics] = []
    for seed in seeds:
        strategy_instance = copy.deepcopy(strategy)
        results.append(
            run_single(
                strategy=strategy_instance,
                seed=seed,
                problem=problem,
                scenario_config=scenario_config,
                physics=physics,
            )
        )
    return results
