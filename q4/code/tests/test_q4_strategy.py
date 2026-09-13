from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest

_CODE_DIR = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SHARED_CODE = _PROJECT_ROOT / "code"
_Q3_CODE = _PROJECT_ROOT / "q3" / "code"
for _path in (_CODE_DIR, _SHARED_CODE, _Q3_CODE):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from q3_strategy import (  # noqa: E402
    ChannelStatus,
    ChannelTrack,
    SEARCH_ROUTE as Q3_SEARCH_ROUTE,
)
from q4_strategy import (  # noqa: E402
    DIRECTIONAL_SEARCH_POINTS,
    DIRECTIONAL_SEARCH_ROUTE_INDICES,
    GuaranteedDirectionalQ4Strategy,
    Q4StrategyOptions,
    _directional_visibility_fraction,
    _reflect_across_bearing_axis,
    _source_before_search,
    directional_search_certificate,
    directional_search_route_length_m,
)
from radio_sim.domain.models import (
    ClearResult,
    ClearStatus,
    MeasureStatus,
    Position,
    ProblemType,
)  # noqa: E402
from radio_sim.environment.local import LocalEnvironment  # noqa: E402
from radio_sim.scenario.models import Scenario, Source, SourceType  # noqa: E402


def make_source(
    channel: int,
    position: Position,
    direction_deg: float | None,
    receive_radius_m: float = 1000.0,
) -> Source:
    source_type = (
        SourceType.OMNIDIRECTIONAL
        if direction_deg is None
        else SourceType.DIRECTIONAL
    )
    return Source(
        channel=channel,
        position=position,
        receive_radius_m=receive_radius_m,
        source_type=source_type,
        direction_deg=direction_deg,
    )


def make_env(*sources: Source, seed: int = 123) -> LocalEnvironment:
    scenario = Scenario(seed=seed, problem=ProblemType.Q4, sources=tuple(sources))
    return LocalEnvironment(scenario)


class DirectionalSearchSkeletonTests(unittest.TestCase):
    def test_v3_defaults_enable_validated_tail_probe(self) -> None:
        options = Q4StrategyOptions()
        self.assertEqual(options.max_active_measurements, 2)
        self.assertFalse(options.task_insertion_scheduler)
        self.assertFalse(options.joint_direction_ranking)
        self.assertTrue(options.adaptive_tail_probe)
        self.assertEqual(options.adaptive_tail_min_visibility, 0.30)
        self.assertFalse(options.direction_aware_grid_ordering)

    def test_adaptive_tail_visibility_threshold_is_validated(self) -> None:
        with self.assertRaises(ValueError):
            Q4StrategyOptions(adaptive_tail_min_visibility=1.01).validate()

    def test_reflection_uses_latest_bearing_axis(self) -> None:
        reflected = _reflect_across_bearing_axis((30.0, 40.0), (10.0, 10.0), 0.0)
        self.assertAlmostEqual(reflected[0], 30.0)
        self.assertAlmostEqual(reflected[1], -20.0)

    def test_fixed_route_preserves_every_certificate_point(self) -> None:
        self.assertEqual(set(DIRECTIONAL_SEARCH_ROUTE_INDICES), set(range(25)))
        self.assertEqual(len(DIRECTIONAL_SEARCH_ROUTE_INDICES), 25)
        self.assertAlmostEqual(
            directional_search_route_length_m(),
            17990.731819,
            places=5,
        )

    def test_two_task_insertion_uses_shorter_order(self) -> None:
        self.assertEqual(
            _source_before_search(
                (0.0, 0.0),
                (10.0, 0.0),
                {3: (2.0, 0.0)},
            ),
            3,
        )
        self.assertIsNone(
            _source_before_search(
                (0.0, 0.0),
                (10.0, 0.0),
                {3: (20.0, 0.0)},
            )
        )

    def test_joint_state_prefers_the_feasible_emission_side(self) -> None:
        toward = _directional_visibility_fraction(
            (10.0, -10.0),
            [(0.0, 0.0)],
            [(10.0, 0.0)],
            [(0.0, 10.0)],
            72,
        )
        away = _directional_visibility_fraction(
            (-10.0, 10.0),
            [(0.0, 0.0)],
            [(10.0, 0.0)],
            [(0.0, 10.0)],
            72,
        )
        self.assertIsNotNone(toward)
        self.assertIsNotNone(away)
        self.assertGreater(toward, away)

    def test_twenty_five_point_certificate_has_strict_margin(self) -> None:
        certificate = directional_search_certificate()
        self.assertEqual(len(DIRECTIONAL_SEARCH_POINTS), 25)
        self.assertEqual(len(set(DIRECTIONAL_SEARCH_POINTS)), 25)
        self.assertEqual(certificate["triangle_count"], 36)
        self.assertTrue(certificate["covers_target_disk"])
        self.assertTrue(certificate["all_triangle_edges_below_receive_min"])
        self.assertGreater(certificate["strict_receive_margin_m"], 15.0)

    def test_dense_positions_and_headings_have_a_visible_point(self) -> None:
        for radius in (0.0, 450.0, 900.0, 1350.0, 1800.0):
            for position_index in range(0, 360, 5):
                position_angle = math.radians(position_index)
                source = (
                    radius * math.cos(position_angle),
                    radius * math.sin(position_angle),
                )
                for heading_index in range(0, 360, 10):
                    heading = math.radians(heading_index)
                    ux, uy = math.cos(heading), math.sin(heading)
                    visible = any(
                        math.hypot(point[0] - source[0], point[1] - source[1])
                        <= 1000.0 + 1e-8
                        and ux * (point[0] - source[0])
                        + uy * (point[1] - source[1])
                        >= -1e-8
                        for point in DIRECTIONAL_SEARCH_POINTS
                    )
                    self.assertTrue(visible)

    def test_q3_seven_points_fail_on_outward_boundary_source(self) -> None:
        source = make_source(
            channel=1,
            position=Position(1800.0, 0.0),
            direction_deg=0.0,
        )
        env = make_env(source)
        env.enter()
        for point in Q3_SEARCH_ROUTE:
            result = env.measure(Position(*point), 1)
            self.assertEqual(result.status, MeasureStatus.NO_SIGNAL)


class GuaranteedDirectionalStrategyTests(unittest.TestCase):
    def test_filtered_clear_grid_still_covers_feasible_polygon(self) -> None:
        class RecordingEnvironment:
            def __init__(self) -> None:
                self.current_position = Position(0.0, 0.0)
                self.points: list[Position] = []
                self.virtual_time_s = 0.0

            def clear(self, position: Position, channel: int) -> ClearResult:
                self.current_position = position
                self.points.append(position)
                self.virtual_time_s += 3.0
                return ClearResult(
                    ClearStatus.NO_TARGET_IN_RANGE,
                    3.0,
                    self.virtual_time_s,
                )

        polygon = [(0.0, 0.0), (1000.0, -100.0), (1000.0, 100.0)]
        track = ChannelTrack(
            channel=1,
            status=ChannelStatus.ALIVE,
            polygon=polygon,
            first_point=(0.0, 0.0),
            first_bearing_deg=0.0,
        )
        env = RecordingEnvironment()
        strategy = GuaranteedDirectionalQ4Strategy()
        strategy._clear_by_grid(env, track)
        self.assertLess(len(env.points), math.ceil(1000.0 / 26.0) * math.ceil(200.0 / 26.0))
        for first_weight in range(21):
            for second_weight in range(21 - first_weight):
                a = first_weight / 20.0
                b = second_weight / 20.0
                point = (
                    a * polygon[1][0] + b * polygon[2][0],
                    a * polygon[1][1] + b * polygon[2][1],
                )
                nearest = min(
                    math.hypot(point[0] - probe.x, point[1] - probe.y)
                    for probe in env.points
                )
                self.assertLessEqual(nearest, 20.0)

    def test_direction_aware_grid_preserves_every_fallback_cell(self) -> None:
        polygon = [(0.0, 0.0), (1000.0, -100.0), (1000.0, 100.0)]
        track = ChannelTrack(
            channel=1,
            status=ChannelStatus.ALIVE,
            polygon=polygon,
            first_point=(0.0, 0.0),
            first_bearing_deg=0.0,
        )
        strategy = GuaranteedDirectionalQ4Strategy()
        strategy._visible_points_by_channel[1] = [(0.0, 0.0)]
        strategy._blind_points_by_channel[1] = [(0.0, 1000.0)]
        baseline, _ = strategy._clear_grid_plan(
            track,
            (0.0, 0.0),
            direction_aware=False,
        )
        reordered, used_direction = strategy._clear_grid_plan(
            track,
            (0.0, 0.0),
            direction_aware=True,
        )
        rounded = lambda points: {
            (round(point[0], 8), round(point[1], 8)) for point in points
        }
        self.assertTrue(used_direction)
        self.assertEqual(len(reordered), len(baseline))
        self.assertEqual(rounded(reordered), rounded(baseline))

    def test_outward_boundary_source_is_found_and_cleared(self) -> None:
        env = make_env(
            make_source(
                channel=7,
                position=Position(1800.0, 0.0),
                direction_deg=0.0,
            ),
            seed=20260912,
        )
        options = Q4StrategyOptions(
            q2_circle_sides=32,
            q2_source_samples=12,
            q2_seed_count=2,
            q2_local_rounds=1,
        )
        result = GuaranteedDirectionalQ4Strategy(options).run(env)
        diagnostics = env._evaluation_snapshot()
        self.assertTrue(result.completed)
        self.assertEqual(diagnostics.cleared_count, 1)

    def test_absent_channels_require_all_twenty_five_points(self) -> None:
        env = make_env()
        strategy = GuaranteedDirectionalQ4Strategy(
            Q4StrategyOptions(max_active_measurements=0)
        )
        result = strategy.run(env)
        diagnostics = env._evaluation_snapshot()
        self.assertTrue(result.completed)
        self.assertEqual(diagnostics.measure_count, 25 * 20)
        self.assertIn("visited_search_points=25", result.note)

    def test_grid_fallback_clears_a_visible_directional_source(self) -> None:
        env = make_env(
            make_source(
                channel=11,
                position=Position(760.0, 120.0),
                direction_deg=190.0,
            ),
            seed=44,
        )
        options = Q4StrategyOptions(
            max_active_measurements=0,
            q2_circle_sides=32,
            q2_source_samples=8,
            q2_seed_count=1,
            q2_local_rounds=0,
        )
        result = GuaranteedDirectionalQ4Strategy(options).run(env)
        diagnostics = env._evaluation_snapshot()
        self.assertTrue(result.completed)
        self.assertEqual(diagnostics.cleared_count, 1)
        self.assertGreater(diagnostics.clear_count, 1)


if __name__ == "__main__":
    unittest.main()
