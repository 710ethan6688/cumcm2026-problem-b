"""Q1 的确定性差分验证与蜕变性质验证程序。"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import platform
import random
import sys
import time

from q1_geometry import RegionStatus, bearing_halfplanes, contains, solve_observations


def random_ring_case(seed: int) -> tuple[list[tuple[float, float, float]], tuple[float, float]]:
    rng = random.Random(seed)
    source = (rng.uniform(-500.0, 500.0), rng.uniform(-500.0, 500.0))
    count = rng.randint(5, 14)
    phase = rng.uniform(0.0, 2.0 * math.pi)
    observations = []
    for index in range(count):
        angle = phase + 2.0 * math.pi * index / count + rng.uniform(-0.12, 0.12)
        radius = rng.uniform(500.0, 1500.0)
        detector = (
            source[0] + radius * math.cos(angle),
            source[1] + radius * math.sin(angle),
        )
        true_bearing = math.degrees(
            math.atan2(source[1] - detector[1], source[0] - detector[0])
        )
        observed_bearing = true_bearing + rng.uniform(-0.95, 0.95)
        observations.append((detector[0], detector[1], observed_bearing))
    return observations, source


def _assert_close(first: float, second: float, label: str) -> None:
    if not math.isclose(first, second, rel_tol=1e-8, abs_tol=1e-7):
        raise AssertionError(f"{label}: {first!r} != {second!r}")


def run_verification(random_cases: int, base_seed: int) -> dict:
    started = time.perf_counter()
    counts = {
        "valid_cases": 0,
        "covered_cases": 0,
        "not_covered_cases": 0,
        "order_checks": 0,
        "duplicate_checks": 0,
        "rigid_transform_checks": 0,
        "monotonicity_checks": 0,
        "tolerance_sensitivity_checks": 0,
    }
    maximum_diameter_difference = 0.0

    for case_index in range(random_cases):
        case_seed = base_seed + case_index
        observations, source = random_ring_case(case_seed)
        result = solve_observations(observations)
        if result.status is not RegionStatus.VALID:
            raise AssertionError(f"种子 {case_seed}：预期状态为 VALID，实际为 {result.status.value}")
        counts["valid_cases"] += 1
        counts["covered_cases" if result.covered else "not_covered_cases"] += 1

        if not all(contains(line, source, 1e-8) for line in bearing_halfplanes(observations)):
            raise AssertionError(f"种子 {case_seed}：生成的源点落在示向区域之外")
        required_diagnostics = (
            "main_reference_vertex_agreement",
            "calipers_bruteforce_diameter_agreement",
            "coverage_formula_agreement",
        )
        if not all(result.diagnostics.get(name) for name in required_diagnostics):
            raise AssertionError(f"种子 {case_seed}：内部差分检查失败")

        shuffled = observations[:]
        random.Random(case_seed ^ 0x5A5A5A5A).shuffle(shuffled)
        reordered = solve_observations(shuffled)
        if reordered.status is not RegionStatus.VALID or reordered.covered != result.covered:
            raise AssertionError(f"种子 {case_seed}：观测顺序不变性检查失败")
        difference = abs((reordered.diameter or 0.0) - (result.diameter or 0.0))
        maximum_diameter_difference = max(maximum_diameter_difference, difference)
        _assert_close(reordered.diameter or 0.0, result.diameter or 0.0, "顺序变换后的直径")
        counts["order_checks"] += 1

        duplicated = solve_observations(observations + [observations[0]])
        if duplicated.status is not RegionStatus.VALID or duplicated.covered != result.covered:
            raise AssertionError(f"种子 {case_seed}：重复约束不变性检查失败")
        _assert_close(duplicated.diameter or 0.0, result.diameter or 0.0, "重复约束后的直径")
        counts["duplicate_checks"] += 1

        previous_diameter = None
        for prefix_size in range(2, len(observations) + 1):
            prefix = solve_observations(observations[:prefix_size])
            if prefix.status is RegionStatus.VALID:
                if previous_diameter is not None and (prefix.diameter or 0.0) > previous_diameter + 1e-7:
                    raise AssertionError(f"种子 {case_seed}：增加约束后直径反而增大")
                previous_diameter = prefix.diameter
                counts["monotonicity_checks"] += 1

        if case_index % 10 == 0:
            angle_deg = 37.0
            angle = math.radians(angle_deg)
            cosine, sine = math.cos(angle), math.sin(angle)
            transformed = [
                (
                    cosine * x - sine * y + 1234.5,
                    sine * x + cosine * y - 987.25,
                    bearing + angle_deg,
                )
                for x, y, bearing in observations
            ]
            moved = solve_observations(transformed)
            if moved.status is not RegionStatus.VALID or moved.covered != result.covered:
                raise AssertionError(f"种子 {case_seed}：刚体变换不变性检查失败")
            _assert_close(moved.diameter or 0.0, result.diameter or 0.0, "刚体变换后的直径")
            counts["rigid_transform_checks"] += 1

        if case_index % 20 == 0:
            loose = solve_observations(observations, tolerance=1e-9)
            tight = solve_observations(observations, tolerance=1e-11)
            if loose.status is not RegionStatus.VALID or tight.status is not RegionStatus.VALID:
                raise AssertionError(f"种子 {case_seed}：容差改变了正常案例的状态")
            if loose.covered != tight.covered:
                raise AssertionError(f"种子 {case_seed}：容差改变了覆盖判定")
            _assert_close(loose.diameter or 0.0, tight.diameter or 0.0, "不同容差下的直径")
            counts["tolerance_sensitivity_checks"] += 1

    elapsed = time.perf_counter() - started
    return {
        "verification_status": "PASS",
        "model_scope": "angle-only bearing intersection; no distance or artificial box clipping",
        "base_seed": base_seed,
        "random_case_count": random_cases,
        "counts": counts,
        "maximum_order_diameter_difference_m": maximum_diameter_difference,
        "elapsed_seconds": elapsed,
        "mean_seconds_per_random_case": elapsed / random_cases if random_cases else 0.0,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="验证 Q1 几何算法实现")
    parser.add_argument("--random-cases", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260911)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "results" / "q1_verification.json",
    )
    args = parser.parse_args()
    if args.random_cases <= 0:
        parser.error("--random-cases 必须为正数")

    summary = run_verification(args.random_cases, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
