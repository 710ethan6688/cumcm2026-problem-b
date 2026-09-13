"""在可复现的本地随机种子区间上批量运行 Q4 策略。"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
import sys

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SHARED_CODE = _PROJECT_ROOT / "code"
if str(_SHARED_CODE) not in sys.path:
    sys.path.insert(0, str(_SHARED_CODE))

from q4_strategy import GuaranteedDirectionalQ4Strategy, Q4StrategyOptions  # noqa: E402
from radio_sim.evaluation import run_single  # noqa: E402


def default_output_path(start_seed: int, count: int) -> Path:
    root = Path(__file__).resolve().parents[1] / "results"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return root / f"q4_batch_seed{start_seed}_n{count}_{stamp}.csv"


def available_path(path: Path) -> Path:
    if not path.exists():
        return path
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return path.with_name(f"{path.stem}_{stamp}{path.suffix}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-seed", type=int, default=0)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--safety-buffer", type=float, default=5.0)
    parser.add_argument("--max-active-measurements", type=int, default=2)
    parser.add_argument(
        "--analytic-clear-terminal",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument(
        "--tail-terminal-linkage",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="启用 A2；同时会启用 A1 解析终端",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--task-insertion", action="store_true")
    parser.add_argument("--joint-direction-ranking", action="store_true")
    parser.add_argument(
        "--adaptive-tail-probe",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--adaptive-tail-min-visibility", type=float, default=0.30
    )
    parser.add_argument("--direction-aware-grid-ordering", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.count <= 0:
        raise SystemExit("--count 必须为正数")

    options = Q4StrategyOptions(
        safety_buffer_m=args.safety_buffer,
        max_active_measurements=args.max_active_measurements,
        analytic_clear_terminal=(
            args.analytic_clear_terminal or args.tail_terminal_linkage
        ),
        tail_terminal_linkage=args.tail_terminal_linkage,
        task_insertion_scheduler=args.task_insertion,
        joint_direction_ranking=args.joint_direction_ranking,
        adaptive_tail_probe=args.adaptive_tail_probe,
        adaptive_tail_min_visibility=args.adaptive_tail_min_visibility,
        direction_aware_grid_ordering=args.direction_aware_grid_ordering,
    )
    results = []
    records = []
    for seed in range(args.start_seed, args.start_seed + args.count):
        strategy = GuaranteedDirectionalQ4Strategy(options)
        result = run_single(strategy=strategy, seed=seed, problem="Q4")
        record = result.to_record()
        record.update(strategy.analytic_terminal_diagnostics)
        results.append(result)
        records.append(record)

    output: Path | None = None
    if not args.no_write:
        output = available_path(
            (args.output or default_output_path(args.start_seed, args.count)).resolve()
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)

    all_cleared_count = sum(result.all_cleared for result in results)
    summary = {
        "problem": "Q4",
        "run_count": len(results),
        "seed_start": args.start_seed,
        "seed_end": args.start_seed + args.count - 1,
        "all_cleared_count": all_cleared_count,
        "all_cleared_rate": all_cleared_count / len(results),
        "strategy_completed_rate": sum(result.strategy_completed for result in results)
        / len(results),
        "mean_virtual_time_s": sum(result.virtual_time_s for result in results)
        / len(results),
        "mean_average_localize_clear_time_s": sum(
            result.average_localize_clear_time_s or 0.0 for result in results
        )
        / len(results),
        "max_virtual_time_s": max(result.virtual_time_s for result in results),
        "mean_wall_time_s": sum(result.wall_time_s for result in results)
        / len(results),
        "mean_failed_clear_count": sum(
            result.failed_clear_count for result in results
        )
        / len(results),
        "analytic_plan_generated_count": sum(
            int(record["analytic_plan_generated"]) for record in records
        ),
        "analytic_plan_certified_count": sum(
            int(record["analytic_plan_certified"]) for record in records
        ),
        "analytic_plan_selected_count": sum(
            int(record["analytic_plan_selected"]) for record in records
        ),
        "analytic_plan_fallback_count": sum(
            int(record["analytic_plan_fallbacks"]) for record in records
        ),
        "analytic_estimated_saving_s": sum(
            float(record["analytic_estimated_saving_s"]) for record in records
        ),
        "tail_terminal_linkage_evaluation_count": sum(
            int(record["tail_terminal_linkage_evaluations"])
            for record in records
        ),
        "tail_terminal_analytic_choice_count": sum(
            int(record["tail_terminal_analytic_choices"])
            for record in records
        ),
        "tail_terminal_estimated_cost_reduction_s": sum(
            float(record["tail_terminal_estimated_cost_reduction_s"])
            for record in records
        ),
        "output": str(output) if output is not None else None,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
