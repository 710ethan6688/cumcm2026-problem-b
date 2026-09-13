from __future__ import annotations

import unittest

from radio_sim.domain.models import Position
from radio_sim.environment.base import EnvironmentStateError, InvalidActionError
from radio_sim.environment.local import PhysicsConfig
from radio_sim.strategy.smoke_test import SmokeTestStrategy
from tests.helpers import make_env, make_source


class TimingAndStateTests(unittest.TestCase):
    def test_official_timing_example_totals_199_seconds(self) -> None:
        env = make_env()
        SmokeTestStrategy().run(env)
        diagnostics = env._evaluation_snapshot()
        self.assertAlmostEqual(env.virtual_time_s, 199.0)
        self.assertAlmostEqual(diagnostics.total_distance_m, 900.0)
        self.assertEqual(diagnostics.channel_switch_count, 1)
        self.assertEqual(diagnostics.measure_count, 3)
        self.assertEqual(diagnostics.clear_count, 1)
        self.assertEqual(diagnostics.failed_clear_count, 1)

    def test_successful_clear_adds_five_seconds(self) -> None:
        env = make_env(make_source(position=Position(0, 0)))
        env.enter()
        result = env.clear(Position(0, 0), 1)
        self.assertEqual(result.action_time_s, 5.0)

    def test_failed_clear_adds_three_seconds(self) -> None:
        env = make_env()
        env.enter()
        result = env.clear(Position(0, 0), 1)
        self.assertEqual(result.action_time_s, 3.0)

    def test_measure_move_switch_and_action_time(self) -> None:
        env = make_env()
        env.enter()
        result = env.measure(Position(30, 40), 2)
        self.assertEqual(result.action_time_s, 16.0)
        self.assertEqual(env.current_position, Position(30, 40))
        self.assertEqual(env.current_channel, 2)

    def test_action_before_enter_is_rejected_without_time_change(self) -> None:
        env = make_env()
        with self.assertRaises(EnvironmentStateError):
            env.measure(Position(0, 0), 1)
        self.assertEqual(env.virtual_time_s, 0.0)

    def test_invalid_coordinate_is_rejected_without_state_change(self) -> None:
        env = make_env()
        env.enter()
        with self.assertRaises(InvalidActionError):
            env.measure(Position(2_000_000.1, 0), 1)
        self.assertEqual(env.virtual_time_s, 0.0)
        self.assertEqual(env.current_position, Position(0, 0))

    def test_position_outside_target_disk_is_allowed(self) -> None:
        env = make_env()
        env.enter()
        result = env.measure(Position(2000, 0), 1)
        self.assertEqual(result.action_time_s, 405.0)

    def test_virtual_time_limit_finishes_after_accepted_action(self) -> None:
        env = make_env(physics=PhysicsConfig(max_virtual_duration_s=5.0))
        env.enter()
        result = env.measure(Position(0, 0), 1)
        self.assertEqual(result.virtual_time_s, 5.0)
        self.assertTrue(env.state.is_finished)
        with self.assertRaises(EnvironmentStateError):
            env.measure(Position(0, 0), 1)


if __name__ == "__main__":
    unittest.main()
