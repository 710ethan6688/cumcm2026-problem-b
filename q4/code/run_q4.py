"""Run the Q4 strategy on one reproducible local scenario."""
from __future__ import annotations

import argparse
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


def default_output_path(seed: int) -> Path:
    root = Path(__file__).resolve().parents[1] / "results"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return root / f"q4_single_seed{seed}_{stamp}.json"


def available_path(path: Path) -> Path:
    if not path.exists():
        return path
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return path.with_name(f"{path.stem}_{stamp}{path.suffix}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=12345)
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
        help="enable A2; this also enables the A1 analytic terminal",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    options = Q4StrategyOptions(
        safety_buffer_m=args.safety_buffer,
        max_active_measurements=args.max_active_measurements,
        analytic_clear_terminal=(
            args.analytic_clear_terminal or args.tail_terminal_linkage
        ),
        tail_terminal_linkage=args.tail_terminal_linkage,
    )
    strategy = GuaranteedDirectionalQ4Strategy(options)
    metrics = run_single(
        strategy=strategy,
        seed=args.seed,
        problem="Q4",
    )
    record = metrics.to_record()
    record.update(strategy.analytic_terminal_diagnostics)

    output: Path | None = None
    if not args.no_write:
        output = available_path((args.output or default_output_path(args.seed)).resolve())
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    payload = dict(record)
    payload["output"] = str(output) if output is not None else None
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
