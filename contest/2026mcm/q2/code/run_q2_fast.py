"""Q2 轻量选点器的命令行入口。"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4

from q2_fast import FastOptions, solve_fast_q2
from q2_state import FirstObservation, Q2Config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Q2 快速保守下一测点选择器"
    )
    parser.add_argument("--first-x", type=float, default=0.0)
    parser.add_argument("--first-y", type=float, default=0.0)
    parser.add_argument("--first-bearing", type=float, default=0.0)
    parser.add_argument("--circle-sides", type=int, default=48)
    parser.add_argument("--coarse-sources", type=int, default=24)
    parser.add_argument("--final-sources", type=int, default=64)
    parser.add_argument("--local-rounds", type=int, default=4)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-write", action="store_true")
    return parser.parse_args()


def default_output_path() -> Path:
    root = Path(__file__).resolve().parents[1] / "results"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return root / f"q2_fast_{stamp}_{uuid4().hex[:8]}.json"


def main() -> int:
    args = parse_args()
    first = FirstObservation((args.first_x, args.first_y), args.first_bearing)
    options = FastOptions(
        circle_sides=args.circle_sides,
        coarse_source_count=args.coarse_sources,
        final_source_count=args.final_sources,
        local_rounds=args.local_rounds,
    )
    result = solve_fast_q2(first, Q2Config(), options)
    output = None if args.no_write else (args.output or default_output_path()).resolve()
    result["output"] = str(output) if output is not None else None
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
