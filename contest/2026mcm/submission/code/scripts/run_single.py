from __future__ import annotations

import argparse
import json

from radio_sim.evaluation import run_single
from radio_sim.strategy import SmokeTestStrategy


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--problem", choices=("Q3", "Q4"), default="Q3")
    args = parser.parse_args()

    metrics = run_single(
        strategy=SmokeTestStrategy(),
        seed=args.seed,
        problem=args.problem,
    )
    print(json.dumps(metrics.to_record(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
