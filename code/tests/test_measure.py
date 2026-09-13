from __future__ import annotations

import unittest

from radio_sim.domain.models import MeasureStatus, Position
from radio_sim.utils.geometry import bearing_deg, circular_difference_deg
from tests.helpers import make_env, make_source


class MeasureTests(unittest.TestCase):
    def test_missing_channel_returns_no_signal(self) -> None:
        env = make_env()
        env.enter()
        result = env.measure(Position(0, 0), 1)
        self.assertEqual(result.status, MeasureStatus.NO_SIGNAL)
        self.assertIsNone(result.angle_deg)

    def test_receive_radius_boundary_is_inclusive(self) -> None:
        env = make_env(make_source(position=Position(1000, 0), receive_radius_m=1000))
        env.enter()
        self.assertEqual(env.measure(Position(0, 0), 1).status, MeasureStatus.DIRECTION)

    def test_beyond_receive_radius_returns_no_signal(self) -> None:
        env = make_env(make_source(position=Position(1000.0001, 0), receive_radius_m=1000))
        env.enter()
        self.assertEqual(env.measure(Position(0, 0), 1).status, MeasureStatus.NO_SIGNAL)

    def test_five_meter_boundary_returns_near(self) -> None:
        env = make_env(make_source(position=Position(5, 0)))
        env.enter()
        result = env.measure(Position(0, 0), 1)
        self.assertEqual(result.status, MeasureStatus.NEAR)
        self.assertIsNone(result.angle_deg)

    def test_just_beyond_five_meters_returns_direction(self) -> None:
        env = make_env(make_source(position=Position(5.0001, 0)))
        env.enter()
        self.assertEqual(env.measure(Position(0, 0), 1).status, MeasureStatus.DIRECTION)

    def test_same_place_measurement_is_exactly_repeatable(self) -> None:
        env = make_env(make_source(position=Position(100, 40)))
        env.enter()
        first = env.measure(Position(10, 5), 1)
        second = env.measure(Position(10, 5), 1)
        self.assertEqual(first.angle_deg, second.angle_deg)

    def test_different_places_can_have_different_error(self) -> None:
        source = make_source(position=Position(500, 500), receive_radius_m=1500)
        env = make_env(source)
        env.enter()
        first = env.measure(Position(0, 0), 1)
        second = env.measure(Position(10, 0), 1)
        first_error = circular_difference_deg(
            first.angle_deg,
            bearing_deg(Position(0, 0), source.position),
        )
        second_error = circular_difference_deg(
            second.angle_deg,
            bearing_deg(Position(10, 0), source.position),
        )
        self.assertNotEqual(first_error, second_error)

    def test_reported_direction_error_is_within_rounding_tolerance(self) -> None:
        source = make_source(position=Position(-300, -500), receive_radius_m=1500)
        env = make_env(source)
        env.enter()
        point = Position(0, 0)
        result = env.measure(point, 1)
        true_bearing = bearing_deg(point, source.position)
        self.assertLessEqual(abs(circular_difference_deg(result.angle_deg, true_bearing)), 1.005)
        self.assertGreaterEqual(result.angle_deg, 0.0)
        self.assertLess(result.angle_deg, 360.0)


if __name__ == "__main__":
    unittest.main()
