from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from q1_geometry import RegionStatus, solve_observations
from verify_q1 import random_ring_case


def main() -> int:
    q1_dir = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="准备 Q1 验证图所需数据")
    parser.add_argument(
        "--summary",
        type=Path,
        default=q1_dir / "results" / "q1_verification.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=q1_dir / "results" / "q1_validation_cases.csv",
    )
    args = parser.parse_args()

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    base_seed = int(summary["base_seed"])
    case_count = int(summary["random_case_count"])
    rows = []

    for offset in range(case_count):
        case_seed = base_seed + offset
        observations, _ = random_ring_case(case_seed)
        result = solve_observations(observations, verify=True)
        if result.status is not RegionStatus.VALID:
            raise RuntimeError(f"种子 {case_seed} 返回状态 {result.status.value}")
        assert result.diameter is not None
        assert result.diameter_pair is not None
        assert result.circle_center is not None
        assert result.covered is not None

        radius = result.diameter / 2.0
        first, second = result.diameter_pair
        non_endpoints = [
            vertex
            for vertex in result.vertices
            if min(
                math.dist(vertex, first),
                math.dist(vertex, second),
            )
            > 1e-7
        ]
        relative_excess = max(
            (
                math.dist(vertex, result.circle_center) / radius - 1.0
                for vertex in non_endpoints
            ),
            default=0.0,
        )
        if result.covered != (relative_excess <= 1e-8):
            raise RuntimeError(f"种子 {case_seed} 的覆盖诊断结果不一致")
        rows.append(
            {
                "seed": case_seed,
                "covered": int(result.covered),
                "relative_radius_excess": relative_excess,
                "diameter_m": result.diameter,
                "vertex_count": len(result.vertices),
            }
        )

    rows.sort(key=lambda row: row["relative_radius_excess"])
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=(
                "rank",
                "seed",
                "covered",
                "relative_radius_excess",
                "diameter_m",
                "vertex_count",
            ),
        )
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
