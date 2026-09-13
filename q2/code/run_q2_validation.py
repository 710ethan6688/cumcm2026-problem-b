"""用于 Q2 第四阶段验证的多场景批量收敛运行程序。"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import time
import uuid

from q2_regions import ResolutionLevel, solve_numerical_regions
from q2_state import FirstObservation, Q2Config


DEFAULT_RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


@dataclass(frozen=True)
class Scenario:
    name: str
    first: FirstObservation


SCENARIOS = (
    Scenario("center", FirstObservation((0.0, 0.0), 0.0)),
    Scenario("offset", FirstObservation((300.0, 500.0), 125.0)),
    Scenario("edge_inward", FirstObservation((1600.0, 0.0), 180.0)),
    Scenario("edge_tangent", FirstObservation((1600.0, 0.0), 90.0)),
    Scenario("outside_inward", FirstObservation((2000.0, 0.0), 180.0)),
    Scenario("wraparound", FirstObservation((0.0, 0.0), 359.5)),
)


def _levels(profile: str) -> tuple[ResolutionLevel, ...]:
    if profile == "quick":
        return (
            ResolutionLevel(1000.0, 9, 8, 5, 2.0),
            ResolutionLevel(500.0, 13, 12, 7, 1.0),
            ResolutionLevel(250.0, 17, 16, 9, 0.5),
        )
    return (
        ResolutionLevel(500.0, 25, 24, 9, 1.0),
        ResolutionLevel(250.0, 37, 36, 13, 0.5),
        ResolutionLevel(125.0, 49, 48, 17, 0.25),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="运行 Q2 多场景收敛验证")
    parser.add_argument("--profile", choices=("quick", "formal"), default="quick")
    parser.add_argument("--scenario", action="append", choices=tuple(item.name for item in SCENARIOS))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--max-candidates", type=int, default=2200)
    return parser


def main() -> None:
    args = _parser().parse_args()
    selected = [item for item in SCENARIOS if not args.scenario or item.name in args.scenario]
    run_id = f"q2_validation_{datetime.now():%Y%m%d_%H%M%S}_{str(uuid.uuid4())[:8]}"
    run_dir = args.output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    levels = _levels(args.profile)
    config = Q2Config()
    index: dict[str, object] = {
        "run_id": run_id,
        "profile": args.profile,
        "evidence": "DIAGNOSTIC" if args.profile == "quick" else "STAGE4_NUMERICAL_VALIDATION",
        "levels": [level.to_dict() for level in levels],
        "scenarios": [],
    }
    started = time.perf_counter()
    for scenario in selected:
        result = solve_numerical_regions(
            scenario.first, config, levels, max_candidates=args.max_candidates
        )
        result["scenario"] = {
            "name": scenario.name,
            "first_point": list(scenario.first.point),
            "first_bearing_deg": scenario.first.bearing_deg,
        }
        path = run_dir / f"{scenario.name}.json"
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        index["scenarios"].append({
            "name": scenario.name,
            "file": path.name,
            "status": result["result_status"],
            "converged": result.get("convergence_assessment", {}).get("converged", False),
            "convergence": result.get("convergence", []),
        })
    index["elapsed_seconds"] = time.perf_counter() - started
    index_path = run_dir / "index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({"run_id": run_id, "profile": args.profile, "scenario_count": len(selected),
                      "elapsed_seconds": index["elapsed_seconds"], "index": str(index_path)},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
