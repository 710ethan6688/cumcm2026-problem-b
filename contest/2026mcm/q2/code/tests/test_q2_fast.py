"""Q2 轻量选点器测试。"""
from __future__ import annotations

import math
import unittest

from q2_fast import (
    FastOptions,
    build_position_outer_polygon,
    conservative_safety_margin,
    generate_sparse_candidates,
    posterior_polygon,
    solve_fast_q2,
)
from q2_state import FirstObservation, Q2Config


class FastQ2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = Q2Config()
        self.first = FirstObservation((0.0, 0.0), 0.0)

    def test_sparse_candidates_are_conservatively_safe(self) -> None:
        polygon = build_position_outer_polygon(self.first, self.config, 32)
        candidates, circle = generate_sparse_candidates(
            self.first, self.config, polygon
        )
        self.assertTrue(candidates)
        self.assertLessEqual(circle.radius, self.config.receive_min + 1e-7)
        for point in candidates:
            self.assertGreaterEqual(
                conservative_safety_margin(
                    point, polygon, self.config.receive_min
                ),
                -1e-7,
            )

    def test_posterior_contains_consistent_source(self) -> None:
        polygon = build_position_outer_polygon(self.first, self.config, 32)
        source = (800.0, 0.0)
        candidate = (700.0, 400.0)
        true_bearing = math.degrees(
            math.atan2(source[1] - candidate[1], source[0] - candidate[0])
        )
        posterior = posterior_polygon(
            polygon, candidate, true_bearing + 0.5, self.config.error_deg
        )
        self.assertGreaterEqual(len(posterior), 3)

    def test_end_to_end_returns_safe_recommendations(self) -> None:
        options = FastOptions(
            circle_sides=32,
            state_angle_cells=15,
            state_radial_cells=12,
            coarse_source_count=12,
            final_source_count=24,
            local_rounds=2,
        )
        result = solve_fast_q2(self.first, self.config, options)
        self.assertEqual(result["result_status"], "FAST_NUMERICAL_SOLUTION")
        recommendations = result["recommendations"]
        self.assertTrue(recommendations)
        for item in recommendations:
            self.assertGreaterEqual(
                item["conservative_safety_margin_m"], -1e-7
            )

    def test_safety_buffer_is_enforced_without_changing_physical_config(self) -> None:
        options = FastOptions(
            circle_sides=32,
            state_angle_cells=15,
            state_radial_cells=12,
            coarse_source_count=12,
            final_source_count=24,
            local_rounds=2,
        )
        buffer_m = 10.0
        result = solve_fast_q2(
            self.first, self.config, options, safety_buffer_m=buffer_m
        )
        self.assertEqual(result["result_status"], "FAST_NUMERICAL_SOLUTION")
        self.assertEqual(
            result["safe_region"]["minimum_receive_radius_m"],
            self.config.receive_min,
        )
        self.assertEqual(result["safe_region"]["safety_buffer_m"], buffer_m)
        for item in result["recommendations"]:
            physical_margin = item["conservative_safety_margin_m"] + buffer_m
            self.assertGreaterEqual(physical_margin, buffer_m - 1e-7)

    def test_excessive_safety_buffer_returns_no_candidate(self) -> None:
        result = solve_fast_q2(self.first, safety_buffer_m=250.0)
        self.assertEqual(result["result_status"], "NO_CONSERVATIVELY_SAFE_CANDIDATE")


if __name__ == "__main__":
    unittest.main()
