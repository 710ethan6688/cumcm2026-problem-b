"""Q2 多分辨率数值前沿带的命令行入口。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
import uuid

from q2_regions import ResolutionLevel, solve_numerical_regions
from q2_state import FirstObservation, Q2Config


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "results"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="构建具有非零面积的 Q2 多分辨率数值候选带。"
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
    parser.add_argument("--coarse-step", type=float, default=500.0)
    parser.add_argument("--fine-step", type=float, default=250.0)
    parser.add_argument("--finest-step", type=float, default=125.0)
    parser.add_argument("--front-buffer-cells", type=int, default=1)
    parser.add_argument("--max-candidates", type=int, default=2000)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--no-write", action="store_true")
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
    levels = (
        ResolutionLevel(args.coarse_step, 25, 24, 9, 1.0),
        ResolutionLevel(args.fine_step, 37, 36, 13, 0.5),
        ResolutionLevel(args.finest_step, 49, 48, 17, 0.25),
    )
    started = time.perf_counter()
    result = solve_numerical_regions(
        first,
        config,
        levels,
        max_candidates=args.max_candidates,
        front_buffer_cells=args.front_buffer_cells,
    )
    result["input_note"] = (
        "CLI defaults are a demonstration scenario, not an official Q2 numerical instance."
    )
    result["first_observation"] = {
        "point": list(first.point),
        "bearing_deg": first.bearing_deg,
    }
    result["physical_config"] = {
        "center": list(config.center),
        "target_radius_m": config.target_radius,
        "bearing_error_deg": config.error_deg,
        "near_radius_m": config.near_radius,
        "receive_radius_range_m": [config.receive_min, config.receive_max],
    }
    result["total_elapsed_seconds"] = time.perf_counter() - started

    if args.no_write:
        output_path = None
    else:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = args.output_dir / f"q2_regions_{str(uuid.uuid4())[:8]}.json"
        output_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False),
            encoding="utf-8",
        )

    summary = {
        "result_status": result["result_status"],
        "level_counts": [level["counts"] for level in result["levels"]],
        "convergence": result.get("convergence", []),
        "convergence_assessment": result.get("convergence_assessment"),
        "region_summary": {
            name: {
                "retained_cell_count": region["retained_cell_count"],
                "component_count": region["component_count"],
                "area_m2": region["area_m2"],
                "bounds_m": region["bounds_m"],
            }
            for name, region in result.get("regions", {}).items()
        },
        "total_elapsed_seconds": result["total_elapsed_seconds"],
        "output": None if output_path is None else str(output_path),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
