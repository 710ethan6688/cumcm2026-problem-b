from __future__ import annotations

import math
import unittest

from q2_curve import StepCurve, curve_dominates, empirical_step_curve, lower_envelope
from q2_evaluator import CandidateEvaluation, dominates, evaluate_candidate
from q2_geometry import Branch, classify_branch, pure_angle_diameter, ray_disk_interval
from q2_measures import branch_areas
from q2_regions import (
    ResolutionLevel,
    expanded_front_cells,
    hausdorff_distance,
    raster_region,
    solve_numerical_regions,
)
from q2_state import (
    DomainStatus,
    FirstObservation,
    Q2Config,
    build_state_domain,
    candidate_grid,
    radius_grid,
)
from q2_safety import GammaStatus, certify_gamma
from run_q2_prototype import run_prototype


class GeometryTests(unittest.TestCase):
    def test_ray_disk_interval_from_center(self) -> None:
        interval = ray_disk_interval((0.0, 0.0), 0.0, (0.0, 0.0), 1800.0)
        self.assertIsNotNone(interval)
        self.assertAlmostEqual(interval[0], 0.0)
        self.assertAlmostEqual(interval[1], 1800.0)

    def test_branch_boundaries(self) -> None:
        source = (0.0, 0.0)
        self.assertIs(classify_branch(source, (5.0, 0.0), 1000.0, 5.0), Branch.NEAR)
        self.assertIs(classify_branch(source, (1000.0, 0.0), 1000.0, 5.0), Branch.DIRECTION)
        self.assertIs(classify_branch(source, (1000.1, 0.0), 1000.0, 5.0), Branch.NO_SIGNAL)

    def test_perpendicular_bearings_are_bounded(self) -> None:
        diameter, status = pure_angle_diameter(
            (0.0, 0.0), 0.0, (1000.0, -1000.0), 90.0, error_deg=1.0
        )
        self.assertEqual(status, "VALID")
        self.assertTrue(math.isfinite(diameter))

    def test_parallel_bearings_are_unbounded(self) -> None:
        diameter, status = pure_angle_diameter(
            (0.0, 0.0), 0.0, (0.0, 100.0), 0.0, error_deg=1.0
        )
        self.assertNotEqual(status, "VALID")
        self.assertTrue(math.isinf(diameter))


class StateDomainTests(unittest.TestCase):
    def test_default_center_scenario_has_positive_area(self) -> None:
        domain = build_state_domain(
            FirstObservation((0.0, 0.0), 0.0),
            Q2Config(),
            angle_cells=7,
            radial_cells=5,
        )
        self.assertIs(domain.status, DomainStatus.REGULAR)
        self.assertEqual(len(domain.samples), 35)
        self.assertIsNotNone(domain.possible_radius_range)
        self.assertIsNotNone(domain.area_radius_range)

    def test_tangent_only_state_is_degenerate_not_empty(self) -> None:
        config = Q2Config(
            center=(0.0, 0.0),
            target_radius=1.0,
            error_deg=1.0,
            near_radius=0.1,
            receive_min=1.0,
            receive_max=2.0,
        )
        domain = build_state_domain(
            FirstObservation((-2.0, 1.0), 1.0),
            config,
            angle_cells=8,
            radial_cells=4,
        )
        self.assertIs(domain.status, DomainStatus.DEGENERATE)
        self.assertEqual(domain.samples, ())
        self.assertIsNotNone(domain.possible_radius_range)
        self.assertIsNone(domain.area_radius_range)

    def test_candidate_grid_is_stable_under_quadrature_refinement(self) -> None:
        first = FirstObservation((0.0, 0.0), 0.0)
        config = Q2Config()
        coarse = build_state_domain(first, config, angle_cells=5, radial_cells=4)
        fine = build_state_domain(first, config, angle_cells=17, radial_cells=16)
        self.assertEqual(
            candidate_grid(coarse, first, config, step_m=500.0),
            candidate_grid(fine, first, config, step_m=500.0),
        )


class SafetyCertificationTests(unittest.TestCase):
    def test_clearly_safe_candidate_is_certified(self) -> None:
        certificate = certify_gamma(
            (500.0, 500.0), FirstObservation((0.0, 0.0), 0.0), Q2Config()
        )
        self.assertIs(certificate.status, GammaStatus.CERTIFIED_SAFE)
        self.assertLessEqual(certificate.upper_bound_m, 0.0)

    def test_clearly_unsafe_candidate_is_certified(self) -> None:
        certificate = certify_gamma(
            (3000.0, 0.0), FirstObservation((0.0, 0.0), 0.0), Q2Config()
        )
        self.assertIs(certificate.status, GammaStatus.CERTIFIED_UNSAFE)
        self.assertGreater(certificate.lower_bound_m, 0.0)


class EvaluatorTests(unittest.TestCase):
    def test_small_evaluation_has_consistent_shares_and_curve(self) -> None:
        first = FirstObservation((0.0, 0.0), 0.0)
        config = Q2Config()
        domain = build_state_domain(first, config, angle_cells=5, radial_cells=4)
        radii = radius_grid(domain, 3)
        evaluation = evaluate_candidate(
            (750.0, 750.0), first, config, domain, radii,
            (20.0, 100.0, 1000.0, 5000.0), angle_step_deg=5.0,
        )
        self.assertTrue(evaluation.evaluable)
        self.assertIsNotNone(evaluation.robust_curve)
        curve = evaluation.robust_curve
        self.assertTrue(all(left <= right + 1e-12 for left, right in zip(curve, curve[1:])))
        for item in evaluation.radius_evaluations:
            self.assertAlmostEqual(
                item.near_share + item.direction_share + item.no_signal_share, 1.0, places=10
            )
            self.assertAlmostEqual(
                item.effective_coverage, item.near_share + item.direction_share, places=10
            )

    def test_near_share_prevents_false_dominance(self) -> None:
        common = dict(
            movement_m=10.0,
            gamma_point_estimate_m=1.0,
            sampled_safe=False,
            evaluable=True,
            sampled_near_only=False,
            robust_effective_coverage=0.9,
            robust_curve=(0.8, 1.0),
            robust_step_curve=StepCurve((20.0, 100.0), (0.8, 1.0), 1.0),
            robust_platform=1.0,
            sampled_tail_diameter_m=100.0,
            radius_evaluations=(),
            angle_table_status_counts={},
        )
        low_near = CandidateEvaluation(point=(0.0, 0.0), robust_near_share=0.1, **common)
        high_near = CandidateEvaluation(point=(1.0, 0.0), robust_near_share=0.2, **common)
        self.assertTrue(dominates(high_near, low_near))
        self.assertFalse(dominates(low_near, high_near))

    def test_full_curve_prevents_threshold_aliasing(self) -> None:
        common = dict(
            movement_m=10.0,
            gamma_point_estimate_m=1.0,
            sampled_safe=False,
            evaluable=True,
            sampled_near_only=False,
            robust_effective_coverage=0.9,
            robust_near_share=0.1,
            robust_curve=(0.0, 1.0),
            robust_platform=1.0,
            sampled_tail_diameter_m=100.0,
            radius_evaluations=(),
            angle_table_status_counts={},
        )
        early = CandidateEvaluation(
            point=(0.0, 0.0),
            robust_step_curve=StepCurve((40.0, 100.0), (0.5, 1.0), 1.0),
            **common,
        )
        late = CandidateEvaluation(
            point=(1.0, 0.0),
            robust_step_curve=StepCurve((60.0, 100.0), (0.5, 1.0), 1.0),
            **common,
        )
        self.assertTrue(dominates(early, late))
        self.assertFalse(dominates(late, early))

    def test_center_scenario_is_reflection_symmetric(self) -> None:
        first = FirstObservation((0.0, 0.0), 0.0)
        config = Q2Config()
        domain = build_state_domain(first, config, angle_cells=5, radial_cells=4)
        radii = radius_grid(domain, 3)
        arguments = (first, config, domain, radii, (50.0, 200.0, 1000.0, 5000.0))
        upper = evaluate_candidate((1000.0, 500.0), *arguments, angle_step_deg=2.0)
        lower = evaluate_candidate((1000.0, -500.0), *arguments, angle_step_deg=2.0)
        self.assertAlmostEqual(
            upper.robust_effective_coverage, lower.robust_effective_coverage, places=10
        )
        self.assertAlmostEqual(upper.robust_near_share, lower.robust_near_share, places=10)
        for first_value, second_value in zip(upper.robust_curve, lower.robust_curve):
            self.assertAlmostEqual(first_value, second_value, places=10)

    def test_degenerate_input_returns_structured_result(self) -> None:
        config = Q2Config(
            center=(0.0, 0.0), target_radius=1.0, error_deg=1.0,
            near_radius=0.1, receive_min=1.0, receive_max=2.0,
        )
        result = run_prototype(
            FirstObservation((-2.0, 1.0), 1.0), config,
            angle_cells=8, radial_cells=4, radius_count=3,
            candidate_step_m=1.0, angle_step_deg=1.0,
        )
        self.assertEqual(result["result_status"], "DEGENERATE_INPUT_NO_AREA_CURVE")
        self.assertEqual(result["counts"]["candidate_points"], 0)
        self.assertEqual(result["counts"]["global_front_certified_safe_points"], 0)
        self.assertEqual(result["global_front_certified_safe_intersection"], [])


class MeasureTests(unittest.TestCase):
    def test_center_active_area_matches_annular_sector(self) -> None:
        config = Q2Config()
        first = FirstObservation((0.0, 0.0), 0.0)
        areas = branch_areas((1000.0, 0.0), first, config, 1500.0)
        expected = 0.5 * (1500.0 ** 2 - 5.0 ** 2) * math.radians(2.0)
        self.assertAlmostEqual(areas.active_area_m2, expected, delta=1e-4)

    def test_near_disk_is_resolved_without_sample_hits(self) -> None:
        config = Q2Config()
        first = FirstObservation((0.0, 0.0), 0.0)
        areas = branch_areas((1000.0, 0.0), first, config, 1500.0)
        self.assertAlmostEqual(areas.near_area_m2, math.pi * 5.0 ** 2, delta=1e-4)
        self.assertGreater(areas.near_area_m2 / areas.active_area_m2, 0.0)

    def test_branch_areas_are_nonnegative_and_complete(self) -> None:
        config = Q2Config()
        first = FirstObservation((0.0, 0.0), 0.0)
        areas = branch_areas((750.0, 600.0), first, config, 1250.0)
        self.assertTrue(all(value >= 0.0 for value in (
            areas.near_area_m2,
            areas.direction_area_m2,
            areas.no_signal_area_m2,
        )))
        self.assertAlmostEqual(
            areas.near_area_m2 + areas.direction_area_m2 + areas.no_signal_area_m2,
            areas.active_area_m2,
            delta=1e-6,
        )


class StepCurveTests(unittest.TestCase):
    def test_empirical_curve_keeps_every_breakpoint(self) -> None:
        curve = empirical_step_curve((10.0, 20.0, math.inf), (1.0, 2.0, 1.0))
        self.assertIsNotNone(curve)
        assert curve is not None
        self.assertEqual(curve.breakpoints_m, (10.0, 20.0))
        self.assertEqual(curve.attainment, (0.25, 0.75))
        self.assertEqual(curve.platform, 0.75)

    def test_lower_envelope_uses_breakpoint_union(self) -> None:
        first = StepCurve((10.0, 30.0), (0.4, 1.0), 1.0)
        second = StepCurve((20.0, 40.0), (0.6, 1.0), 1.0)
        envelope = lower_envelope((first, second))
        self.assertIsNotNone(envelope)
        assert envelope is not None
        self.assertEqual(envelope.breakpoints_m, (20.0, 30.0, 40.0))
        self.assertEqual(envelope.attainment, (0.4, 0.6, 1.0))
        self.assertEqual(curve_dominates(first, second), (False, False))

    def test_float_jitter_is_not_false_strict_dominance(self) -> None:
        first = StepCurve((10.0, 20.0), (0.5, 1.0), 1.0)
        second = StepCurve((10.0 + 1e-10, 20.0 + 1e-10), (0.5, 1.0), 1.0)
        self.assertEqual(curve_dominates(first, second), (True, False))
        self.assertEqual(curve_dominates(second, first), (True, False))


class RegionTests(unittest.TestCase):
    def test_adjacent_cells_form_nonzero_area_component(self) -> None:
        region = raster_region({(0, 0), (1, 0)}, 10.0, buffer_cells=0, label="TEST")
        self.assertEqual(region["retained_cell_count"], 2)
        self.assertEqual(region["component_count"], 1)
        self.assertEqual(region["area_m2"], 200.0)
        self.assertEqual(len(region["components"][0]["boundary_segments"]), 6)

    def test_diagonal_cells_remain_separate_components(self) -> None:
        region = raster_region({(0, 0), (1, 1)}, 10.0, buffer_cells=0, label="TEST")
        self.assertEqual(region["component_count"], 2)

    def test_front_expansion_is_clipped_to_evaluated_centers(self) -> None:
        allowed = [(0.0, 0.0), (10.0, 0.0), (0.0, 10.0)]
        cells = expanded_front_cells([(0.0, 0.0)], allowed, 10.0, buffer_cells=1)
        self.assertEqual(cells, {(0, 0), (1, 0), (0, 1)})

    def test_hausdorff_distance(self) -> None:
        self.assertEqual(hausdorff_distance([(0.0, 0.0)], [(3.0, 4.0)]), 5.0)
        self.assertIsNone(hausdorff_distance([], [(0.0, 0.0)]))

    def test_multiresolution_requires_nested_candidate_steps(self) -> None:
        levels = (
            ResolutionLevel(900.0, 5, 4, 3, 2.0),
            ResolutionLevel(500.0, 5, 4, 3, 2.0),
        )
        with self.assertRaises(ValueError):
            solve_numerical_regions(
                FirstObservation((0.0, 0.0), 0.0), Q2Config(), levels
            )

    def test_small_multiresolution_solver_outputs_regions(self) -> None:
        levels = (
            ResolutionLevel(1000.0, 5, 4, 3, 2.0),
            ResolutionLevel(500.0, 7, 5, 3, 2.0),
        )
        result = solve_numerical_regions(
            FirstObservation((0.0, 0.0), 0.0),
            Q2Config(),
            levels,
            max_candidates=400,
            front_buffer_cells=1,
        )
        self.assertEqual(result["result_status"], "MULTIRESOLUTION_NUMERICAL_FRONT_BANDS")
        global_region = result["regions"]["global_front_band"]
        self.assertGreater(global_region["retained_cell_count"], 0)
        self.assertGreater(global_region["area_m2"], 0.0)
        self.assertEqual(
            global_region["geometry_type"],
            "UNION_OF_AXIS_ALIGNED_SQUARE_CELLS",
        )
        self.assertAlmostEqual(global_region["bounds_m"][1], -global_region["bounds_m"][3])
        self.assertIn("global_front_hausdorff_m", result["convergence"][0])

    def test_degenerate_input_does_not_invent_region(self) -> None:
        config = Q2Config(
            center=(0.0, 0.0), target_radius=1.0, error_deg=1.0,
            near_radius=0.1, receive_min=1.0, receive_max=2.0,
        )
        levels = (
            ResolutionLevel(1.0, 8, 4, 3, 1.0),
            ResolutionLevel(0.5, 8, 4, 3, 1.0),
        )
        result = solve_numerical_regions(
            FirstObservation((-2.0, 1.0), 1.0), config, levels,
            max_candidates=400,
        )
        self.assertEqual(result["result_status"], "REGION_UNDEFINED_FOR_NONREGULAR_INPUT")
        self.assertEqual(result["regions"], {})


if __name__ == "__main__":
    unittest.main()
