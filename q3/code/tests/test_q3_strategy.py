from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

_CODE_DIR = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SHARED_CODE = _PROJECT_ROOT / "code"
for _path in (_CODE_DIR, _SHARED_CODE):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from q3_strategy import (  # noqa: E402
    AbsenceReason,
    ChannelStatus,
    SEARCH_ROUTE,
    GuaranteedRollingQ3Strategy,
    Q3StrategyOptions,
    RegionHealth,
    _fallback_initial_polygon,
    search_cover_bound_m,
)
from radio_sim.domain.models import (  # noqa: E402
    ClearResult,
    ClearStatus,
    MeasureResult,
    MeasureStatus,
    Position,
    ProblemType,
)
from radio_sim.environment.base import EnvironmentStateError  # noqa: E402
from radio_sim.environment.local import LocalEnvironment  # noqa: E402
from radio_sim.scenario.models import Scenario, Source, SourceType  # noqa: E402


def make_source(
    channel: int = 1,
    position: Position = Position(0.0, 0.0),
    receive_radius_m: float = 1000.0,
) -> Source:
    return Source(
        channel=channel,
        position=position,
        receive_radius_m=receive_radius_m,
        source_type=SourceType.OMNIDIRECTIONAL,
        direction_deg=None,
    )


def make_env(*sources: Source, seed: int = 123) -> LocalEnvironment:
    scenario = Scenario(seed=seed, problem=ProblemType.Q3, sources=tuple(sources))
    return LocalEnvironment(scenario)


class SearchSkeletonTests(unittest.TestCase):
    def test_seven_point_skeleton_has_strict_receive_margin(self) -> None:
        self.assertEqual(len(SEARCH_ROUTE), 7)
        self.assertLess(search_cover_bound_m(), 1000.0)

        for radius in (0.0, 450.0, 900.0, 1350.0, 1800.0):
            for index in range(360):
                angle = math.radians(index)
                point = (radius * math.cos(angle), radius * math.sin(angle))
                nearest = min(
                    math.hypot(point[0] - x, point[1] - y)
                    for x, y in SEARCH_ROUTE
                )
                self.assertLess(nearest, 1000.0)

    def test_fallback_triangle_contains_the_outer_sector_tip(self) -> None:
        polygon = _fallback_initial_polygon((0.0, 0.0), 0.0, 1.005, 1500.0)
        self.assertAlmostEqual(polygon[1][0], 1500.0, places=9)
        self.assertAlmostEqual(polygon[2][0], 1500.0, places=9)
        self.assertLess(polygon[1][1], 0.0)
        self.assertGreater(polygon[2][1], 0.0)


class GuaranteedRollingStrategyTests(unittest.TestCase):
    def test_near_source_is_cleared_and_absence_is_certified(self) -> None:
        env = make_env(make_source(channel=1, position=Position(0.0, 0.0)))
        strategy = GuaranteedRollingQ3Strategy()
        result = strategy.run(env)
        diagnostics = env._evaluation_snapshot()
        self.assertTrue(result.completed)
        self.assertEqual(diagnostics.cleared_count, 1)
        self.assertEqual(diagnostics.failed_clear_count, 0)
        certificate = strategy.completion_certificate
        self.assertIsNotNone(certificate)
        self.assertTrue(certificate.valid)
        for channel in range(2, 21):
            track = strategy._tracks[channel]
            self.assertIs(track.status, ChannelStatus.ABSENT_CERTIFIED)
            self.assertIs(
                track.absence_reason,
                AbsenceReason.COVER_COMPLETE_NO_SIGNAL,
            )
            self.assertEqual(len(track.absence_evidence_event_ids), len(SEARCH_ROUTE))

    def test_count_upper_bound_absence_records_the_sixteen_channels(self) -> None:
        env = make_env(
            *(make_source(channel=channel) for channel in range(1, 17))
        )
        strategy = GuaranteedRollingQ3Strategy()
        result = strategy.run(env)
        self.assertTrue(result.completed)
        for channel in range(17, 21):
            track = strategy._tracks[channel]
            self.assertIs(
                track.absence_reason,
                AbsenceReason.GLOBAL_COUNT_UPPER_BOUND,
            )
            self.assertEqual(len(track.absence_confirmed_channels), 16)

    def test_near_clear_failure_is_not_converted_to_a_fake_bearing(self) -> None:
        class FailingClearEnvironment:
            def clear(self, position: Position, channel: int) -> ClearResult:
                return ClearResult(
                    ClearStatus.NO_TARGET_IN_RANGE,
                    action_time_s=3.0,
                    virtual_time_s=8.0,
                )

        strategy = GuaranteedRollingQ3Strategy()
        track = strategy._tracks[1]
        point = (10.0, 20.0)
        observation = MeasureResult(
            MeasureStatus.NEAR,
            angle_deg=None,
            action_time_s=5.0,
            virtual_time_s=5.0,
        )
        strategy._record_observation(track, point, observation, "test")
        with self.assertRaises(EnvironmentStateError):
            strategy._handle_measurement(
                FailingClearEnvironment(), track, point, observation
            )
        self.assertIs(track.region_health, RegionHealth.INVALID)
        self.assertIsNone(track.first_bearing_deg)
        self.assertIsNone(track.last_bearing_deg)

    def test_failed_rebuild_keeps_the_prior_certified_outer_bound(self) -> None:
        strategy = GuaranteedRollingQ3Strategy()
        track = strategy._tracks[1]
        first = MeasureResult(
            MeasureStatus.DIRECTION,
            angle_deg=0.0,
            action_time_s=5.0,
            virtual_time_s=5.0,
        )
        strategy._record_observation(track, (0.0, 0.0), first, "test")
        strategy._handle_measurement(object(), track, (0.0, 0.0), first)
        prior = list(track.polygon)

        second = MeasureResult(
            MeasureStatus.DIRECTION,
            angle_deg=180.0,
            action_time_s=5.0,
            virtual_time_s=10.0,
        )
        strategy._record_observation(track, (100.0, 0.0), second, "test")
        with patch("q3_strategy.posterior_polygon", return_value=[]):
            strategy._handle_measurement(object(), track, (100.0, 0.0), second)
        self.assertEqual(track.polygon, prior)
        self.assertIs(track.region_health, RegionHealth.SAFE_STALE)

    def test_direction_source_is_eventually_cleared(self) -> None:
        env = make_env(
            make_source(
                channel=7,
                position=Position(760.0, 120.0),
                receive_radius_m=1000.0,
            ),
            seed=20260912,
        )
        options = Q3StrategyOptions(
            q2_circle_sides=32,
            q2_source_samples=16,
            q2_error_nodes=3,
            q2_seed_count=2,
            q2_local_rounds=2,
        )
        result = GuaranteedRollingQ3Strategy(options).run(env)
        diagnostics = env._evaluation_snapshot()
        self.assertTrue(result.completed)
        self.assertEqual(diagnostics.cleared_count, 1)
        self.assertGreaterEqual(diagnostics.measure_count, 1)

    def test_grid_fallback_clears_when_active_localization_is_disabled(self) -> None:
        env = make_env(
            make_source(
                channel=11,
                position=Position(900.0, -210.0),
                receive_radius_m=1000.0,
            ),
            seed=44,
        )
        options = Q3StrategyOptions(
            max_active_measurements=0,
            q2_circle_sides=32,
            q2_source_samples=8,
            q2_seed_count=1,
            q2_local_rounds=0,
        )
        result = GuaranteedRollingQ3Strategy(options).run(env)
        diagnostics = env._evaluation_snapshot()
        self.assertTrue(result.completed)
        self.assertEqual(diagnostics.cleared_count, 1)
        self.assertGreater(diagnostics.clear_count, 1)


if __name__ == "__main__":
    unittest.main()
