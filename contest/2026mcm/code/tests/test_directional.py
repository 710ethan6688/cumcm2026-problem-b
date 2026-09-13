from __future__ import annotations

import unittest

from radio_sim.domain.models import MeasureStatus, Position, ProblemType
from radio_sim.scenario.models import SourceType
from tests.helpers import make_env, make_source


class DirectionalCoverageTests(unittest.TestCase):
    def _measure_from(self, receiver: Position, direction_deg: float = 0.0) -> MeasureStatus:
        source = make_source(
            position=Position(0, 0),
            receive_radius_m=1000,
            source_type=SourceType.DIRECTIONAL,
            direction_deg=direction_deg,
        )
        env = make_env(source, problem=ProblemType.Q4)
        env.enter()
        return env.measure(receiver, 1).status

    def test_positive_ninety_degree_boundary_is_included(self) -> None:
        self.assertEqual(self._measure_from(Position(0, 100)), MeasureStatus.DIRECTION)

    def test_negative_ninety_degree_boundary_is_included(self) -> None:
        self.assertEqual(self._measure_from(Position(0, -100)), MeasureStatus.DIRECTION)

    def test_just_outside_directional_boundary_has_no_signal(self) -> None:
        self.assertEqual(self._measure_from(Position(-0.01, 100)), MeasureStatus.NO_SIGNAL)

    def test_crossing_zero_degrees_is_handled(self) -> None:
        self.assertEqual(
            self._measure_from(Position(100, 0), direction_deg=359.0),
            MeasureStatus.DIRECTION,
        )

    def test_source_center_is_treated_as_covered_and_near(self) -> None:
        self.assertEqual(self._measure_from(Position(0, 0)), MeasureStatus.NEAR)


if __name__ == "__main__":
    unittest.main()
