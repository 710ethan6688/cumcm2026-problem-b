from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
import matplotlib as mpl
from matplotlib import font_manager
import numpy as np
import ultraplot as uplt
EXPORT_DPI = 1000

def _resolve_chinese_font() -> str:
    system_font = Path(r"C:\Windows\Fonts\msyh.ttc")
    if system_font.exists():
        font_manager.fontManager.addfont(system_font)
        return font_manager.FontProperties(fname=system_font).get_name()
    for family in ("Microsoft YaHei", "Microsoft YaHei UI"):
        try:
            path = font_manager.findfont(family, fallback_to_default=False)
        except ValueError:
            continue
        font_manager.fontManager.addfont(path)
        return family
    raise RuntimeError("中文图注需要安装 Microsoft YaHei 字体")

def main() -> int:
    q1_dir = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="绘制 Q1 验证图")
    parser.add_argument(
        "--example",
        type=Path,
        default=q1_dir / "results" / "q1_example_result.json",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=q1_dir / "results" / "q1_validation_cases.csv",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=q1_dir / "results" / "q1_verification.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=q1_dir / "output" / "figures" / "q1_validation.png",
    )
    args = parser.parse_args()

    example = json.loads(args.example.read_text(encoding="utf-8"))
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    if example["status"] != "VALID":
        raise ValueError("示例结果的状态必须为 VALID")
    vertices = np.asarray(example["vertices"], dtype=float)
    diameter_pair = np.asarray(example["diameter_pair"], dtype=float)
    center = np.asarray(example["circle_center"], dtype=float)
    diameter = float(example["diameter"])
    if vertices.ndim != 2 or vertices.shape[1] != 2 or not np.isfinite(vertices).all():
        raise ValueError("示例顶点必须是元素有限的 n×2 数组")

    with args.cases.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != int(summary["random_case_count"]):
        raise ValueError("案例数据数量与验证摘要不一致")
    ranks = np.asarray([int(row["rank"]) for row in rows])
    covered = np.asarray([bool(int(row["covered"])) for row in rows])
    excess_percent = 100.0 * np.asarray(
        [float(row["relative_radius_excess"]) for row in rows]
    )
    if not np.isfinite(excess_percent).all():
        raise ValueError("覆盖诊断值必须是有限数")

    with uplt.rc.context({}):
        family = _resolve_chinese_font()
        mpl.rcParams["font.family"] = [family, "DejaVu Sans"]
        fig, ax = uplt.subplots(
            ncols=1,
            journal="nat2",
            share=False,
            tight=True,
        )

        covered_count = int(covered.sum())
        not_covered_count = int((~covered).sum())
        ax.scatter(
            ranks[covered],
            excess_percent[covered],
            s=8,
            color="tab:blue",
            label=f"覆盖 ({covered_count})",
        )
        ax.scatter(
            ranks[~covered],
            excess_percent[~covered],
            s=8,
            color="tab:orange",
            label=f"不覆盖 ({not_covered_count})",
        )
        ax.axhline(0.0, color="black", linewidth=0.9)
        ax.legend(loc="ul", ncols=1, frame=False)
        ax.format(
            xlabel="按覆盖余量排序的验证实例",
            ylabel="最大相对半径超量 (%)",
            xlim=(0, len(rows) + 1),
            grid=True,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        fig.save(args.output, dpi=EXPORT_DPI)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
