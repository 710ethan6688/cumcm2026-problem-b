"""Q1 求解器的命令行入口。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from q1_geometry import solve_observations


EXAMPLE_OBSERVATIONS = [
    {"x": 1000.0, "y": 0.0, "bearing_deg": 180.0},
    {"x": 0.0, "y": 1000.0, "bearing_deg": 270.0},
    {"x": -1000.0, "y": 0.0, "bearing_deg": 0.0},
    {"x": 0.0, "y": -1000.0, "bearing_deg": 90.0},
]


def _parse_observations(payload: Any) -> list[tuple[float, float, float]]:
    rows = payload.get("observations") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("输入必须是列表，或是包含 'observations' 字段的对象")
    observations = []
    for row in rows:
        if isinstance(row, dict):
            observations.append((float(row["x"]), float(row["y"]), float(row["bearing_deg"])))
        elif isinstance(row, list) and len(row) == 3:
            observations.append((float(row[0]), float(row[1]), float(row[2])))
        else:
            raise ValueError("每条观测必须采用 {x,y,bearing_deg} 或 [x,y,bearing_deg] 格式")
    return observations


def main() -> int:
    parser = argparse.ArgumentParser(description="求解 MCM 2026 B 题 Q1 示向几何问题")
    parser.add_argument("--input", type=Path, help="UTF-8 编码的 JSON 观测文件")
    parser.add_argument("--output", type=Path, help="可选的 UTF-8 编码 JSON 结果文件")
    parser.add_argument("--error-deg", type=float, default=1.0)
    parser.add_argument("--tolerance", type=float, default=1e-10)
    args = parser.parse_args()

    if args.input:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
    else:
        payload = {"observations": EXAMPLE_OBSERVATIONS}
    observations = _parse_observations(payload)
    result = solve_observations(
        observations,
        error_deg=args.error_deg,
        tolerance=args.tolerance,
        verify=True,
    )
    text = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if result.status.value == "VALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
