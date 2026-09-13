from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from time import perf_counter

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SHARED_CODE = _PROJECT_ROOT / "code"
if str(_SHARED_CODE) not in sys.path:
    sys.path.insert(0, str(_SHARED_CODE))

from radio_sim.environment.base import EnvironmentStateError  # noqa: E402
from radio_sim.environment.official import OfficialEnvironment  # noqa: E402
from q3_strategy import GuaranteedRollingQ3Strategy, Q3StrategyOptions  # noqa: E402


def available_path(path: Path) -> Path:
    if not path.exists():
        return path
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return path.with_name(f"{path.stem}_{stamp}{path.suffix}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--robot-id", required=True, help="当前登录模拟器的参赛队号")
    parser.add_argument("--base-url", default="http://127.0.0.1:2026")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--retry-backoff", type=float, default=0.2)
    parser.add_argument("--exit-reserve", type=float, default=15.0)
    parser.add_argument("--safety-buffer", type=float, default=5.0)
    parser.add_argument("--max-active-measurements", type=int, default=4)
    parser.add_argument("--log", type=Path, help="逐请求 JSONL 日志路径")
    parser.add_argument("--output", type=Path, help="运行摘要 JSON 路径")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    results_dir = Path(__file__).resolve().parents[1] / "results"
    log_path = available_path(
        (args.log or results_dir / f"q3_official_{stamp}.jsonl").resolve()
    )
    output_path = available_path(
        (args.output or results_dir / f"q3_official_{stamp}.json").resolve()
    )

    env = OfficialEnvironment(
        robot_id=args.robot_id,
        base_url=args.base_url,
        timeout_s=args.timeout,
        max_retries=args.max_retries,
        retry_backoff_s=args.retry_backoff,
        exit_reserve_s=args.exit_reserve,
        log_path=log_path,
    )
    strategy = GuaranteedRollingQ3Strategy(
        Q3StrategyOptions(
            safety_buffer_m=args.safety_buffer,
            max_active_measurements=args.max_active_measurements,
        )
    )

    started = perf_counter()
    result = strategy.run(env)
    cleanup_error: str | None = None
    if env.state.is_active:
        if env.has_pending_request:
            cleanup_error = (
                "unresolved request retained; no new /exit was sent: "
                f"{env.pending_request}"
            )
        else:
            try:
                env.exit()
            except EnvironmentStateError as exc:
                cleanup_error = f"{type(exc).__name__}: {exc}"
    wall_time_s = perf_counter() - started

    state = env.state
    summary = {
        "result_status": "COMPLETE" if result.completed else "INCOMPLETE",
        "strategy_name": result.strategy_name,
        "strategy_completed": result.completed,
        "strategy_note": result.note,
        "successful_clear_count": env.successful_clear_count,
        "measure_count": env.measure_count,
        "clear_count": env.clear_count,
        "unique_request_count": env.request_count,
        "http_attempt_count": env.http_attempt_count,
        "virtual_time_s": state.virtual_time_s,
        "wall_time_s": wall_time_s,
        "entered_remaining_real_duration_s": env.entered_remaining_real_duration_s,
        "remaining_real_duration_s": env.remaining_real_duration_s,
        "final_position": {"x": state.current_position.x, "y": state.current_position.y},
        "final_measurement_channel": state.current_channel,
        "environment_finished": state.is_finished,
        "cleanup_error": cleanup_error,
        "pending_request": env.pending_request,
        "completion_certificate": (
            strategy.completion_certificate.to_record()
            if strategy.completion_certificate is not None
            else None
        ),
        "request_log": str(log_path),
        "output": str(output_path),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if result.completed and cleanup_error is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
