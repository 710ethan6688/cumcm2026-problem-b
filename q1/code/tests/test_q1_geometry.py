from __future__ import annotations

import math
import random
import unittest

from q1_geometry import (
    RegionStatus,
    bearing_halfplanes,
    contains,
    coverage_by_dot_product,
    diameter_bruteforce,
    diameter_rotating_calipers,
    make_halfplane,
    solve_halfplanes,
    solve_observations,
)


def square_halfplanes() -> list:
    return [
        make_halfplane((-1.0, 0.0), (0.0, -1.0), "x >= -1"),
        make_halfplane((1.0, 0.0), (0.0, 1.0), "x <= 1"),
        make_halfplane((0.0, -1.0), (1.0, 0.0), "y >= -1"),
        make_halfplane((0.0, 1.0), (-1.0, 0.0), "y <= 1"),
    ]


def ring_observations(seed: int, count: int = 8) -> tuple[list[tuple[float, float, float]], tuple[float, float]]:
    rng = random.Random(seed)
    source = (rng.uniform(-100.0, 100.0), rng.uniform(-100.0, 100.0))
    observations = []
    phase = rng.uniform(0.0, 2.0 * math.pi)
    for index in range(count):
        angle = phase + 2.0 * math.pi * index / count + rng.uniform(-0.08, 0.08)
        radius = rng.uniform(600.0, 1400.0)
        detector = (
            source[0] + radius * math.cos(angle),
            source[1] + radius * math.sin(angle),
        )
        true_bearing = math.degrees(
            math.atan2(source[1] - detector[1], source[0] - detector[0])
        )
        observed = true_bearing + rng.uniform(-0.8, 0.8)
        observations.append((detector[0], detector[1], observed))
    return observations, source


class BearingConversionTests(unittest.TestCase):
    def test_wraparound_and_forward_direction(self) -> None:
        lines = bearing_halfplanes([(0.0, 0.0, 0.0)])
        self.assertTrue(all(contains(line, (10.0, 0.0)) for line in lines))
        self.assertFalse(all(contains(line, (-10.0, 0.0)) for line in lines))

    def test_true_source_satisfies_all_random_observations(self) -> None:
        for seed in range(50):
            observations, source = ring_observations(seed)
            self.assertTrue(
                all(contains(line, source, 1e-8) for line in bearing_halfplanes(observations))
            )


class StateClassificationTests(unittest.TestCase):
    def test_square_is_valid(self) -> None:
        result = solve_halfplanes(square_halfplanes())
        self.assertEqual(result.status, RegionStatus.VALID)
        self.assertEqual(len(result.vertices), 4)
        self.assertAlmostEqual(result.diameter, math.sqrt(8.0), places=9)
        self.assertTrue(result.covered)

    def test_fast_mode_skips_reference_checks(self) -> None:
        result = solve_halfplanes(square_halfplanes(), verify=False)
        self.assertEqual(result.status, RegionStatus.VALID)
        self.assertFalse(result.diagnostics["reference_checks_run"])
        self.assertNotIn("calipers_bruteforce_diameter_agreement", result.diagnostics)

    def test_empty_parallel_constraints(self) -> None:
        lines = [
            make_halfplane((1.0, 0.0), (0.0, -1.0)),  # x >= 1
            make_halfplane((0.0, 0.0), (0.0, 1.0)),   # x <= 0
        ]
        self.assertEqual(solve_halfplanes(lines).status, RegionStatus.EMPTY)

    def test_unbounded_wedge(self) -> None:
        lines = [
            make_halfplane((0.0, 0.0), (0.0, -1.0)),  # x >= 0
            make_halfplane((0.0, 0.0), (1.0, 0.0)),   # y >= 0
        ]
        self.assertEqual(solve_halfplanes(lines).status, RegionStatus.UNBOUNDED)

    def test_unbounded_strip(self) -> None:
        lines = [
            make_halfplane((-1.0, 0.0), (0.0, -1.0)),
            make_halfplane((1.0, 0.0), (0.0, 1.0)),
        ]
        self.assertEqual(solve_halfplanes(lines).status, RegionStatus.UNBOUNDED)

    def test_degenerate_segment(self) -> None:
        lines = [
            make_halfplane((0.0, 0.0), (0.0, -1.0)),
            make_halfplane((0.0, 0.0), (0.0, 1.0)),
            make_halfplane((0.0, -1.0), (1.0, 0.0)),
            make_halfplane((0.0, 1.0), (-1.0, 0.0)),
        ]
        self.assertEqual(solve_halfplanes(lines).status, RegionStatus.DEGENERATE)

    def test_degenerate_single_point(self) -> None:
        lines = [
            make_halfplane((0.0, 0.0), (0.0, -1.0)),
            make_halfplane((0.0, 0.0), (1.0, 0.0)),
            make_halfplane((0.0, 0.0), (-1.0, 1.0)),
        ]
        self.assertEqual(solve_halfplanes(lines).status, RegionStatus.DEGENERATE)

    def test_same_direction_redundancy_keeps_stricter_constraint(self) -> None:
        lines = square_halfplanes() + [
            make_halfplane((-2.0, 0.0), (0.0, -1.0)),
            square_halfplanes()[0],
        ]
        result = solve_halfplanes(lines)
        self.assertEqual(result.status, RegionStatus.VALID)
        self.assertEqual(len(result.vertices), 4)
        self.assertAlmostEqual(result.diameter, math.sqrt(8.0), places=9)


class DiameterAndCoverageTests(unittest.TestCase):
    def test_equilateral_triangle_is_not_covered(self) -> None:
        vertices = [(0.0, 0.0), (2.0, 0.0), (1.0, math.sqrt(3.0))]
        diameter, pair = diameter_rotating_calipers(vertices)
        reference, _ = diameter_bruteforce(vertices)
        self.assertAlmostEqual(diameter, reference, places=12)
        covered, violation, witness = coverage_by_dot_product(vertices, pair)
        self.assertFalse(covered)
        self.assertGreater(violation, 0.0)
        self.assertIsNotNone(witness)

    def test_rectangle_is_covered_by_diagonal_circle(self) -> None:
        vertices = [(-2.0, -1.0), (2.0, -1.0), (2.0, 1.0), (-2.0, 1.0)]
        _, pair = diameter_rotating_calipers(vertices)
        covered, _, _ = coverage_by_dot_product(vertices, pair)
        self.assertTrue(covered)


class EndToEndPropertyTests(unittest.TestCase):
    def test_random_valid_instances_close_all_checks(self) -> None:
        for seed in range(100):
            observations, source = ring_observations(seed)
            result = solve_observations(observations)
            self.assertEqual(result.status, RegionStatus.VALID, msg=f"seed={seed}")
            self.assertTrue(
                all(contains(line, source, 1e-7) for line in bearing_halfplanes(observations))
            )
            self.assertTrue(result.diagnostics["main_reference_vertex_agreement"])
            self.assertTrue(result.diagnostics["calipers_bruteforce_diameter_agreement"])
            self.assertTrue(result.diagnostics["coverage_formula_agreement"])

    def test_order_and_duplicate_invariance(self) -> None:
        observations, _ = ring_observations(90210)
        baseline = solve_observations(observations)
        shuffled = observations[:]
        random.Random(42).shuffle(shuffled)
        reordered = solve_observations(shuffled)
        duplicated = solve_observations(observations + [observations[0]])
        self.assertEqual(baseline.status, RegionStatus.VALID)
        self.assertEqual(reordered.status, RegionStatus.VALID)
        self.assertEqual(duplicated.status, RegionStatus.VALID)
        self.assertAlmostEqual(baseline.diameter, reordered.diameter, places=7)
        self.assertAlmostEqual(baseline.diameter, duplicated.diameter, places=7)
        self.assertEqual(baseline.covered, reordered.covered)
        self.assertEqual(baseline.covered, duplicated.covered)

    def test_translation_and_rotation_invariance(self) -> None:
        observations, _ = ring_observations(2026)
        baseline = solve_observations(observations)
        angle = math.radians(37.0)
        cosine, sine = math.cos(angle), math.sin(angle)
        transformed = []
        for x, y, bearing in observations:
            transformed.append(
                (
                    cosine * x - sine * y + 1234.0,
                    sine * x + cosine * y - 987.0,
                    bearing + 37.0,
                )
            )
        moved = solve_observations(transformed)
        self.assertEqual(baseline.status, RegionStatus.VALID)
        self.assertEqual(moved.status, RegionStatus.VALID)
        self.assertAlmostEqual(baseline.diameter, moved.diameter, places=7)
        self.assertEqual(baseline.covered, moved.covered)


if __name__ == "__main__":
    unittest.main()
