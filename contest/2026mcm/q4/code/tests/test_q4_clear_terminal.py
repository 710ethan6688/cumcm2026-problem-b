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

from q3_strategy import ChannelStatus, ChannelTrack  # noqa: E402
from q4_clear_terminal import build_certified_strip_plan  # noqa: E402
from q4_strategy import GuaranteedDirectionalQ4Strategy, Q4StrategyOptions  # noqa: E402


class CertifiedStripTerminalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.polygon = [
            (5.0, -0.1),
            (1500.0, -26.2),
            (1500.0, 26.2),
        ]

    def test_constructive_cells_cover_dense_wedge_points(self) -> None:
        plan = build_certified_strip_plan(
            self.polygon,
            origin=(0.0, 0.0),
            bearing_deg=0.0,
            current=(0.0, 0.0),
            certified_radius_m=19.5,
        )
        self.assertIsNotNone(plan)
        assert plan is not None
        self.assertLessEqual(plan.maximum_cell_radius_m, 19.5 + 1e-9)

        for first_weight in range(51):
            for second_weight in range(51 - first_weight):
                a = first_weight / 50.0
                b = second_weight / 50.0
                c = 1.0 - a - b
                point = (
                    a * self.polygon[0][0]
                    + b * self.polygon[1][0]
                    + c * self.polygon[2][0],
                    a * self.polygon[0][1]
                    + b * self.polygon[1][1]
                    + c * self.polygon[2][1],
                )
                self.assertTrue(
                    any(
                        cell.low_u - 1e-8 <= point[0] <= cell.high_u + 1e-8
                        and cell.low_v - 1e-8 <= point[1] <= cell.high_v + 1e-8
                        for cell in plan.cells
                    )
                )
                nearest = min(
                    math.hypot(point[0] - center[0], point[1] - center[1])
                    for center in plan.points
                )
                self.assertLessEqual(nearest, 19.5 + 1e-7)

    def test_adaptive_plan_beats_fixed_grid_on_first_bearing_wedge(self) -> None:
        track = ChannelTrack(
            channel=1,
            status=ChannelStatus.ALIVE,
            polygon=list(self.polygon),
            first_point=(0.0, 0.0),
            first_bearing_deg=0.0,
        )
        strategy = GuaranteedDirectionalQ4Strategy(
            Q4StrategyOptions(analytic_clear_terminal=True)
        )
        current = (0.0, 0.0)
        grid, _ = strategy._clear_grid_plan(
            track, current, direction_aware=False
        )
        analytic = strategy._analytic_clear_plan(track, current)
        self.assertIsNotNone(analytic)
        assert analytic is not None
        self.assertLess(len(analytic.points), len(grid))
        self.assertLess(
            analytic.estimated_time_s,
            strategy._estimated_grid_time_s(grid, current),
        )

    def test_a2_links_tail_decision_to_the_cheaper_certified_terminal(self) -> None:
        track = ChannelTrack(
            channel=1,
            status=ChannelStatus.ALIVE,
            polygon=list(self.polygon),
            first_point=(0.0, 0.0),
            first_bearing_deg=0.0,
        )
        current = (0.0, 0.0)
        a1 = GuaranteedDirectionalQ4Strategy(
            Q4StrategyOptions(analytic_clear_terminal=True)
        )
        a2 = GuaranteedDirectionalQ4Strategy(
            Q4StrategyOptions(
                analytic_clear_terminal=True,
                tail_terminal_linkage=True,
            )
        )
        grid, _ = a1._clear_grid_plan(track, current, direction_aware=False)
        analytic = a2._analytic_clear_plan(track, current)
        self.assertIsNotNone(analytic)
        assert analytic is not None

        self.assertEqual(
            a1._tail_terminal_cost_s(track, current, grid),
            a1._estimated_grid_time_s(grid, current),
        )
        self.assertAlmostEqual(
            a2._tail_terminal_cost_s(track, current, grid),
            analytic.estimated_time_s,
        )
        diagnostics = a2.analytic_terminal_diagnostics
        self.assertEqual(diagnostics["tail_terminal_linkage_evaluations"], 1)
        self.assertEqual(diagnostics["tail_terminal_analytic_choices"], 1)
        self.assertGreater(
            diagnostics["tail_terminal_estimated_cost_reduction_s"], 0.0
        )

    def test_a2_requires_the_a1_terminal(self) -> None:
        with self.assertRaises(ValueError):
            Q4StrategyOptions(tail_terminal_linkage=True).validate()

    def test_degenerate_point_has_a_valid_one_point_plan(self) -> None:
        plan = build_certified_strip_plan(
            [(12.0, -3.0)],
            origin=(0.0, 0.0),
            bearing_deg=73.0,
            current=(0.0, 0.0),
            certified_radius_m=19.5,
        )
        self.assertIsNotNone(plan)
        assert plan is not None
        self.assertEqual(len(plan.points), 1)
        self.assertLessEqual(plan.maximum_cell_radius_m, 19.5)


if __name__ == "__main__":
    unittest.main()
