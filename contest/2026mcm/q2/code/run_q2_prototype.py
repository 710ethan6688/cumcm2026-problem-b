"""Q2 低分辨率诊断原型的命令行入口。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import time
from typing import Sequence
from q2_evaluator import evaluate_candidate, nondominated, representative_indices
from q2_safety import GammaStatus, certify_gamma
from q2_state import (
    FirstObservation,
    Q2Config,
    build_state_domain,
    candidate_grid,
    radius_grid,
)
import uuid
DEFAULT_THRESHOLDS_M = (20.0, 50.0, 100.0, 200.0, 500.0, 1000.0, 2000.0, 5000.0)
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "results"
def run_prototype(
    first: FirstObservation,
    config: Q2Config,
    *,
    angle_cells: int,
    radial_cells: int,
    radius_count: int,
    candidate_step_m: float,
    angle_step_deg: float,
    thresholds_m: Sequence[float] = DEFAULT_THRESHOLDS_M,
    max_candidates: int = 400,
    include_radius_details: bool = False,
) -> dict[str, object]:
    started = time.perf_counter()
    domain = build_state_domain(
        first,
        config,
        angle_cells=angle_cells,
        radial_cells=radial_cells,
    )
    if not domain.has_positive_area:
        return {
            "result_status": f"{domain.status.value}_INPUT_NO_AREA_CURVE",
            "evidence_level": {
                "curves_and_fronts": "UNDEFINED_FOR_NON_POSITIVE_AREA_STATE",
                "front_membership": "NOT_EVALUATED",
                "sampled_safe": "NOT_EVALUATED",
                "continuous_candidate_space": "NOT_EVALUATED",
            },
            "input_note": "CLI defaults are a demonstration scenario, not an official Q2 numerical instance.",
            "first_observation": {
                "point": list(first.point),
                "bearing_deg": first.bearing_deg,
            },
            "physical_config": {
                "center": list(config.center),
                "target_radius_m": config.target_radius,
                "bearing_error_deg": config.error_deg,
                "near_radius_m": config.near_radius,
                "receive_radius_range_m": [config.receive_min, config.receive_max],
            },
            "numerical_config": {
                "angle_cells": angle_cells,
                "radial_cells": radial_cells,
                "radius_count": radius_count,
                "candidate_step_m": candidate_step_m,
                "angle_table_step_deg": angle_step_deg,
                "diameter_thresholds_m": list(thresholds_m),
                "branch_area_method": "NOT_EVALUATED",
                "dominance_curve_method": "NOT_EVALUATED",
                "max_candidates": max_candidates,
            },
            "state_domain": {
                "status": domain.status.value,
                "source_sample_count": len(domain.samples),
                "support_point_count": len(domain.support_points),
                "possible_radius_range_m": domain.possible_radius_range,
                "positive_area_radius_range_m": domain.area_radius_range,
                "approximate_area_m2": domain.approximate_area_m2,
                "sampled_receive_radii_m": [],
            },
            "counts": {
                "candidate_points": 0,
                "evaluable_points": 0,
                "sampled_safe_points": 0,
                "certified_safe_points": 0,
                "certified_unsafe_points": 0,
                "unresolved_safety_points": 0,
                "global_front_points": 0,
                "safe_internal_front_points": 0,
                "sampled_safe_internal_front_points": 0,
                "global_front_sampled_safe_points": 0,
                "global_front_certified_safe_points": 0,
                "sampled_safe_near_only_points": 0,
            },
            "representative_indices_within_front": {
                "global": {"coverage": None, "near": None, "tail": None},
                "sampled_safe_internal": {"coverage": None, "near": None, "tail": None},
            },
            "global_front": [],
            "sampled_safe_internal_front": [],
            "certified_safe_internal_front": [],
            "global_front_sampled_safe_intersection": [],
            "global_front_certified_safe_intersection": [],
            "sampled_safe_near_only": [],
            "all_candidates": [],
            "elapsed_seconds": time.perf_counter() - started,
        }
    radii = radius_grid(domain, radius_count)
    candidate_points = candidate_grid(
        domain,
        first,
        config,
        step_m=candidate_step_m,
        max_candidates=max_candidates,
    )
    evaluations = [
        evaluate_candidate(
            point,
            first,
            config,
            domain,
            radii,
            thresholds_m,
            angle_step_deg=angle_step_deg,
        )
        for point in candidate_points
    ]
    certificates = {
        item.point: certify_gamma(item.point, first, config)
        for item in evaluations
    }
    global_front = nondominated(evaluations)
    sampled_safe_evaluable = [item for item in evaluations if item.sampled_safe and item.evaluable]
    sampled_safe_front = nondominated(sampled_safe_evaluable, safety_front=True)
    certified_safe_evaluable = [
        item for item in evaluations
        if item.evaluable and certificates[item.point].status is GammaStatus.CERTIFIED_SAFE
    ]
    safe_front = nondominated(certified_safe_evaluable, safety_front=True)
    global_sampled_safe = [item for item in global_front if item.sampled_safe]
    global_safe = [
        item for item in global_front
        if certificates[item.point].status is GammaStatus.CERTIFIED_SAFE
    ]
    sampled_near_only = [item for item in evaluations if item.sampled_safe and item.sampled_near_only]
    def serialize(items):
        serialized = []
        for item in items:
            value = item.to_dict(thresholds_m, include_radii=include_radius_details)
            value["gamma_certificate"] = certificates[item.point].to_dict()
            serialized.append(value)
        return serialized
    global_representatives = representative_indices(global_front)
    safe_representatives = representative_indices(safe_front)
    result: dict[str, object] = {
        "result_status": "PROTOTYPE_DIAGNOSTIC_ONLY",
        "evidence_level": {
            "curves_and_fronts": "LOW_RESOLUTION_POINT_ESTIMATE",
            "branch_areas": "ADAPTIVE_NUMERICAL_INTEGRATION",
            "curve_breakpoints": "COMPLETE_FOR_SAMPLED_SOURCE_AND_RADIUS_STATES",
            "front_membership": "NOT_CERTIFIED_REQUIRES_MULTIRESOLUTION_CHECK",
            "sampled_safe": "NOT_A_STRICT_GAMMA_CERTIFICATE",
            "continuous_candidate_space": "NOT_EXHAUSTIVELY_COVERED",
        },
        "input_note": "CLI defaults are a demonstration scenario, not an official Q2 numerical instance.",
        "first_observation": {
            "point": list(first.point),
            "bearing_deg": first.bearing_deg,
        },
        "physical_config": {
            "center": list(config.center),
            "target_radius_m": config.target_radius,
            "bearing_error_deg": config.error_deg,
            "near_radius_m": config.near_radius,
            "receive_radius_range_m": [config.receive_min, config.receive_max],
        },
        "numerical_config": {
            "angle_cells": angle_cells,
            "radial_cells": radial_cells,
            "radius_count": radius_count,
            "candidate_step_m": candidate_step_m,
            "angle_table_step_deg": angle_step_deg,
            "diameter_thresholds_m": list(thresholds_m),
            "branch_area_method": "ADAPTIVE_POLAR_RADIAL_INTERSECTION",
            "dominance_curve_method": "FULL_SAMPLED_BREAKPOINT_UNION",
            "max_candidates": max_candidates,
        },
        "state_domain": {
            "status": domain.status.value,
            "source_sample_count": len(domain.samples),
            "support_point_count": len(domain.support_points),
            "possible_radius_range_m": domain.possible_radius_range,
            "positive_area_radius_range_m": domain.area_radius_range,
            "approximate_area_m2": domain.approximate_area_m2,
            "sampled_receive_radii_m": list(radii),
        },
        "counts": {
            "candidate_points": len(evaluations),
            "evaluable_points": sum(item.evaluable for item in evaluations),
            "sampled_safe_points": sum(item.sampled_safe for item in evaluations),
            "certified_safe_points": sum(
                certificate.status is GammaStatus.CERTIFIED_SAFE
                for certificate in certificates.values()
            ),
            "certified_unsafe_points": sum(
                certificate.status is GammaStatus.CERTIFIED_UNSAFE
                for certificate in certificates.values()
            ),
            "unresolved_safety_points": sum(
                certificate.status is GammaStatus.UNRESOLVED
                for certificate in certificates.values()
            ),
            "global_front_points": len(global_front),
            "safe_internal_front_points": len(safe_front),
            "sampled_safe_internal_front_points": len(sampled_safe_front),
            "global_front_sampled_safe_points": len(global_sampled_safe),
            "global_front_certified_safe_points": len(global_safe),
            "sampled_safe_near_only_points": len(sampled_near_only),
        },
        "representative_indices_within_front": {
            "global": global_representatives,
            "sampled_safe_internal": safe_representatives,
        },
        "global_front": serialize(global_front),
        "sampled_safe_internal_front": serialize(sampled_safe_front),
        "certified_safe_internal_front": serialize(safe_front),
        "sampled_safe_diagnostic_front": serialize(sampled_safe_front),
        "global_front_sampled_safe_intersection": serialize(global_sampled_safe),
        "global_front_certified_safe_intersection": serialize(global_safe),
        "sampled_safe_near_only": serialize(sampled_near_only),
        "all_candidates": serialize(evaluations),
        "elapsed_seconds": time.perf_counter() - started,
    }
    return result
def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="运行 Q2 低分辨率诊断原型。"
    )
    parser.add_argument("--first-x", type=float, default=0.0)
    parser.add_argument("--first-y", type=float, default=0.0)
    parser.add_argument("--first-bearing", type=float, default=0.0)
    parser.add_argument("--center-x", type=float, default=0.0)
    parser.add_argument("--center-y", type=float, default=0.0)
    parser.add_argument("--target-radius", type=float, default=1800.0)
    parser.add_argument("--error-deg", type=float, default=1.0)
    parser.add_argument("--near-radius", type=float, default=5.0)
    parser.add_argument("--receive-min", type=float, default=1000.0)
    parser.add_argument("--receive-max", type=float, default=1500.0)
    parser.add_argument("--angle-cells", type=int, default=25)
    parser.add_argument("--radial-cells", type=int, default=24)
    parser.add_argument("--radius-count", type=int, default=9)
    parser.add_argument("--candidate-step", type=float, default=500.0)
    parser.add_argument("--angle-step-deg", type=float, default=1.0)
    parser.add_argument("--max-candidates", type=int, default=400)
    parser.add_argument("--include-radius-details", action="store_true")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="输出目录（默认：../results）",
    )
    parser.add_argument("--no-write", action="store_true", help="只打印摘要，不写入 JSON")
    return parser
def main() -> None:
    args = _parser().parse_args()
    first = FirstObservation((args.first_x, args.first_y), args.first_bearing)
    config = Q2Config(
        center=(args.center_x, args.center_y),
        target_radius=args.target_radius,
        error_deg=args.error_deg,
        near_radius=args.near_radius,
        receive_min=args.receive_min,
        receive_max=args.receive_max,
    )
    result = run_prototype(
        first,
        config,
        angle_cells=args.angle_cells,
        radial_cells=args.radial_cells,
        radius_count=args.radius_count,
        candidate_step_m=args.candidate_step,
        angle_step_deg=args.angle_step_deg,
        thresholds_m=DEFAULT_THRESHOLDS_M,
        max_candidates=args.max_candidates,
        include_radius_details=args.include_radius_details,
    )
    if args.no_write:
        output_path = None
    else:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        uid = str(uuid.uuid4())[:8]
        output_path = args.output_dir / f"q2_prototype_{uid}.json"
        output_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False),
            encoding="utf-8",
        )
    summary = {
        "result_status": result["result_status"],
        "state_domain": result["state_domain"],
        "counts": result["counts"],
        "elapsed_seconds": result["elapsed_seconds"],
        "output": str(output_path) if output_path is not None else None,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False))
if __name__ == "__main__":
    main()
