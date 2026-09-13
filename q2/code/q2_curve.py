"""Q2 测点评价器使用的加权经验阶梯曲线。

本模块中的曲线对当前离散源状态模型是完整的：所有有限直径断点均被保留。
这些曲线并不是经过区间认证的连续状态曲线。
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
import math
from typing import Iterable, Sequence


@dataclass(frozen=True)
class StepCurve:
    """右连续、单调不减的加权经验累积分布函数。"""

    breakpoints_m: tuple[float, ...]
    attainment: tuple[float, ...]
    platform: float

    def __post_init__(self) -> None:
        if len(self.breakpoints_m) != len(self.attainment):
            raise ValueError("曲线断点与达到率序列的长度必须相同")
        if any(not math.isfinite(value) or value < 0.0 for value in self.breakpoints_m):
            raise ValueError("曲线断点必须是非负有限数")
        if tuple(sorted(self.breakpoints_m)) != self.breakpoints_m:
            raise ValueError("曲线断点必须按升序排列")
        if any(right <= left for left, right in zip(self.breakpoints_m, self.breakpoints_m[1:])):
            raise ValueError("曲线断点必须严格递增")
        if not 0.0 <= self.platform <= 1.0:
            raise ValueError("曲线平台值必须位于 [0, 1] 内")
        previous = 0.0
        for value in self.attainment:
            if not previous <= value <= self.platform + 1e-12:
                raise ValueError("曲线达到率必须单调不减且不超过平台值")
            previous = value

    def at(self, threshold_m: float) -> float:
        if math.isnan(threshold_m) or threshold_m < 0.0:
            raise ValueError("曲线阈值必须非负")
        index = bisect_right(self.breakpoints_m, threshold_m) - 1
        return 0.0 if index < 0 else self.attainment[index]

    def to_dict(self) -> dict[str, object]:
        return {
            "breakpoints_m": list(self.breakpoints_m),
            "attainment": list(self.attainment),
            "platform": self.platform,
        }


def empirical_step_curve(
    diameters_m: Sequence[float],
    weights_m2: Sequence[float],
) -> StepCurve | None:
    """为一组离散的 direction 状态构建完整加权曲线。"""

    if len(diameters_m) != len(weights_m2):
        raise ValueError("直径序列与权重序列的长度必须相同")
    if not diameters_m:
        return None
    if any(weight < 0.0 or not math.isfinite(weight) for weight in weights_m2):
        raise ValueError("权重必须是非负有限数")
    denominator = sum(weights_m2)
    if denominator <= 0.0:
        return None

    grouped: dict[float, float] = {}
    finite_weight = 0.0
    for diameter, weight in zip(diameters_m, weights_m2):
        if math.isnan(diameter) or diameter < 0.0:
            raise ValueError("直径必须非负，或为正无穷")
        if math.isfinite(diameter):
            grouped[diameter] = grouped.get(diameter, 0.0) + weight
            finite_weight += weight

    cumulative = 0.0
    breakpoints: list[float] = []
    attainment: list[float] = []
    for diameter in sorted(grouped):
        cumulative += grouped[diameter]
        breakpoints.append(diameter)
        attainment.append(min(1.0, cumulative / denominator))
    return StepCurve(
        tuple(breakpoints),
        tuple(attainment),
        min(1.0, finite_weight / denominator),
    )


def lower_envelope(curves: Sequence[StepCurve]) -> StepCurve | None:
    """返回全部经验断点上的逐点下包络。"""

    if not curves:
        return None
    breakpoints = sorted({point for curve in curves for point in curve.breakpoints_m})
    platform = min(curve.platform for curve in curves)
    kept_points: list[float] = []
    kept_values: list[float] = []
    previous = 0.0
    for point in breakpoints:
        value = min(curve.at(point) for curve in curves)
        if value > previous + 1e-15:
            kept_points.append(point)
            kept_values.append(value)
            previous = value
    return StepCurve(tuple(kept_points), tuple(kept_values), platform)


def curve_dominates(
    first: StepCurve,
    second: StepCurve,
    *,
    tolerance: float = 1e-10,
    horizontal_tolerance_m: float = 1e-6,
) -> tuple[bool, bool]:
    """返回在所有数值可区分断点位置上的支配关系。

    间距小于 ``horizontal_tolerance_m`` 的断点视为同一数值事件，
    并在两个跳变都发生后立即评价。该参数是算术相等容差，
    不是物理定位阈值。
    """

    if horizontal_tolerance_m < 0.0 or not math.isfinite(horizontal_tolerance_m):
        raise ValueError("水平容差必须是非负有限数")

    raw_points: Iterable[float] = sorted(set(first.breakpoints_m) | set(second.breakpoints_m))
    points: list[float] = []
    for point in raw_points:
        if points and point - points[-1] <= horizontal_tolerance_m:
            points[-1] = point
        else:
            points.append(point)
    strictly_better = False
    for point in points:
        left = first.at(point)
        right = second.at(point)
        if left < right - tolerance:
            return False, False
        if left > right + tolerance:
            strictly_better = True
    if first.platform < second.platform - tolerance:
        return False, False
    if first.platform > second.platform + tolerance:
        strictly_better = True
    return True, strictly_better


__all__ = [
    "StepCurve",
    "curve_dominates",
    "empirical_step_curve",
    "lower_envelope",
]
