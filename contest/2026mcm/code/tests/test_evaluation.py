from __future__ import annotations

import unittest

from radio_sim.domain.models import StrategyResult
from radio_sim.environment.base import Environment
from radio_sim.evaluation.runner import run_batch, run_single


class EnterExitStrategy:
    def run(self, env: Environment) -> StrategyResult:
        env.enter()
        env.exit()
        return StrategyResult(strategy_name=type(self).__name__)


class EvaluationTests(unittest.TestCase):
    def test_single_run_reports_zero_clear_metrics_safely(self) -> None:
        result = run_single(EnterExitStrategy(), seed=1, problem="Q3")
        self.assertEqual(result.cleared_count, 0)
        self.assertEqual(result.cleared_ratio, 0.0)
        self.assertIsNone(result.average_localize_clear_time_s)

    def test_batch_preserves_seed_order_and_reproducibility(self) -> None:
        first = run_batch(EnterExitStrategy(), seeds=[3, 1, 2], problem="Q4")
        second = run_batch(EnterExitStrategy(), seeds=[3, 1, 2], problem="Q4")
        self.assertEqual([item.seed for item in first], [3, 1, 2])
        comparable_first = [(item.seed, item.source_count) for item in first]
        comparable_second = [(item.seed, item.source_count) for item in second]
        self.assertEqual(comparable_first, comparable_second)


if __name__ == "__main__":
    unittest.main()
