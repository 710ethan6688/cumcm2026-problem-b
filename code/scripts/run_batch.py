"""运行一段随机种子，并可选地为每个场景保存一行 CSV。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from radio_sim.evaluation import run_batch
from radio_sim.strategy import SmokeTestStrategy


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-seed", type=int, default=0)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--problem", choices=("Q3", "Q4"), default="Q3")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.count <= 0:
        parser.error("--count must be positive")

    results = run_batch(
        strategy=SmokeTestStrategy(),
        seeds=range(args.start_seed, args.start_seed + args.count),
        problem=args.problem,
    )
    records = [result.to_record() for result in results]

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)

    summary = {
        "problem": args.problem,
        "run_count": len(results),
        "seed_start": args.start_seed,
        "seed_end": args.start_seed + args.count - 1,
        "mean_cleared_ratio": sum(item.cleared_ratio for item in results) / len(results),
        "mean_virtual_time_s": sum(item.virtual_time_s for item in results) / len(results),
        "output": str(args.output) if args.output is not None else None,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
