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

from radio_sim.evaluation import run_batch  # noqa: E402
from q3_strategy import GuaranteedRollingQ3Strategy, Q3StrategyOptions  # noqa: E402


def default_output_path(start_seed: int, count: int) -> Path:
    root = Path(__file__).resolve().parents[1] / "results"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return root / f"q3_batch_seed{start_seed}_n{count}_{stamp}.csv"


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
    parser.add_argument("--max-active-measurements", type=int, default=4)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.count <= 0:
        raise SystemExit("--count 必须为正数")

    strategy = GuaranteedRollingQ3Strategy(
        Q3StrategyOptions(
            safety_buffer_m=args.safety_buffer,
            max_active_measurements=args.max_active_measurements,
        )
    )
    results = run_batch(
        strategy=strategy,
        seeds=range(args.start_seed, args.start_seed + args.count),
        problem="Q3",
    )
    records = [result.to_record() for result in results]

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
        "problem": "Q3",
        "run_count": len(results),
        "seed_start": args.start_seed,
        "seed_end": args.start_seed + args.count - 1,
        "all_cleared_count": all_cleared_count,
        "all_cleared_rate": all_cleared_count / len(results),
        "strategy_completed_rate": sum(result.strategy_completed for result in results) / len(results),
        "mean_virtual_time_s": sum(result.virtual_time_s for result in results) / len(results),
        "mean_average_localize_clear_time_s": sum(
            result.average_localize_clear_time_s or 0.0 for result in results
        ) / len(results),
        "max_virtual_time_s": max(result.virtual_time_s for result in results),
        "mean_wall_time_s": sum(result.wall_time_s for result in results) / len(results),
        "mean_failed_clear_count": sum(result.failed_clear_count for result in results) / len(results),
        "output": str(output) if output is not None else None,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
