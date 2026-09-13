from __future__ import annotations

import unittest

from radio_sim.domain.models import ClearStatus, MeasureStatus, Position, ProblemType
from radio_sim.scenario.models import SourceType
from tests.helpers import make_env, make_source


class ClearTests(unittest.TestCase):
    def test_twenty_meter_boundary_succeeds(self) -> None:
        env = make_env(make_source(position=Position(20, 0)))
        env.enter()
        self.assertEqual(env.clear(Position(0, 0), 1).status, ClearStatus.SUCCESS)

    def test_just_beyond_twenty_meters_fails(self) -> None:
        env = make_env(make_source(position=Position(20.0001, 0)))
        env.enter()
        self.assertEqual(
            env.clear(Position(0, 0), 1).status,
            ClearStatus.NO_TARGET_IN_RANGE,
        )

    def test_cleared_source_cannot_be_measured_or_cleared_again(self) -> None:
        env = make_env(make_source(position=Position(0, 0)))
        env.enter()
        self.assertEqual(env.clear(Position(0, 0), 1).status, ClearStatus.SUCCESS)
        self.assertEqual(env.measure(Position(0, 0), 1).status, MeasureStatus.NO_SIGNAL)
        self.assertEqual(
            env.clear(Position(0, 0), 1).status,
            ClearStatus.NO_TARGET_IN_RANGE,
        )

    def test_clear_does_not_change_current_measurement_channel(self) -> None:
        env = make_env(
            make_source(channel=1, position=Position(0, 0)),
            make_source(channel=2, position=Position(100, 0)),
        )
        env.enter()
        env.measure(Position(0, 0), 2)
        env.clear(Position(0, 0), 1)
        self.assertEqual(env.current_channel, 2)

    def test_directional_clear_ignores_signal_coverage(self) -> None:
        source = make_source(
            position=Position(0, 0),
            source_type=SourceType.DIRECTIONAL,
            direction_deg=0.0,
        )
        env = make_env(source, problem=ProblemType.Q4)
        env.enter()
        self.assertEqual(env.measure(Position(-10, 0), 1).status, MeasureStatus.NO_SIGNAL)
        self.assertEqual(env.clear(Position(-10, 0), 1).status, ClearStatus.SUCCESS)


if __name__ == "__main__":
    unittest.main()
