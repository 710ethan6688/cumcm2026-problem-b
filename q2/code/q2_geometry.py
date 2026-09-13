"""Q2 的几何基础函数与 Q1 示向交会适配器。

高频路径以 ``verify=False`` 调用已经验证的 Q1 求解器；
部分测试可启用 Q1 的独立复核。
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
import math
from pathlib import Path
import sys
from typing import Sequence


Point = tuple[float, float]

_Q1_CODE = Path(__file__).resolve().parents[2] / "q1" / "code"
if str(_Q1_CODE) not in sys.path:
    sys.path.insert(0, str(_Q1_CODE))

from q1_geometry import RegionStatus, solve_observations  # noqa: E402


class Branch(str, Enum):
    NEAR = "near"
    DIRECTION = "direction"
    NO_SIGNAL = "no_signal"


def _require_finite(values: Sequence[float], name: str) -> None:
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"{name} 只能包含有限数")


def normalize_angle_deg(angle: float) -> float:
    if not math.isfinite(angle):
        raise ValueError("角度必须是有限数")
    return angle % 360.0


def circular_distance_deg(first: float, second: float) -> float:
    delta = (normalize_angle_deg(first) - normalize_angle_deg(second) + 180.0) % 360.0
    return abs(delta - 180.0)


def distance(first: Point, second: Point) -> float:
    _require_finite((*first, *second), "points")
    return math.hypot(first[0] - second[0], first[1] - second[1])


def bearing_deg(origin: Point, target: Point) -> float:
    _require_finite((*origin, *target), "points")
    dx = target[0] - origin[0]
    dy = target[1] - origin[1]
    if dx == 0.0 and dy == 0.0:
        raise ValueError("两点重合时示向角没有定义")
    return normalize_angle_deg(math.degrees(math.atan2(dy, dx)))


def ray_disk_interval(
    origin: Point,
    direction_rad: float,
    center: Point,
    radius: float,
    *,
    tolerance: float = 1e-12,
) -> tuple[float, float] | None:
    """返回射线落在闭圆盘内的非负参数区间。"""

    _require_finite((*origin, direction_rad, *center, radius, tolerance), "ray/disk data")
    if radius <= 0.0:
        raise ValueError("半径必须为正数")
    if tolerance <= 0.0:
        raise ValueError("容差必须为正数")
    ux = math.cos(direction_rad)
    uy = math.sin(direction_rad)
    vx = origin[0] - center[0]
    vy = origin[1] - center[1]
    projection = vx * ux + vy * uy
    discriminant = projection * projection - (vx * vx + vy * vy - radius * radius)
    if discriminant < -tolerance:
        return None
    root = math.sqrt(max(0.0, discriminant))
    lower_raw = -projection - root
    upper_raw = -projection + root
    if upper_raw < -tolerance:
        return None
    lower = max(0.0, lower_raw)
    upper = max(0.0, upper_raw)
    if lower > upper + tolerance:
        return None
    return (lower, upper)


def classify_branch(
    source: Point,
    candidate: Point,
    receive_radius: float,
    near_radius: float,
    *,
    tolerance: float = 1e-9,
) -> Branch:
    _require_finite(
        (*source, *candidate, receive_radius, near_radius, tolerance),
        "branch data",
    )
    if near_radius < 0.0 or receive_radius <= near_radius:
        raise ValueError("参数必须满足 0 <= near_radius < receive_radius")
    separation = distance(source, candidate)
    if separation <= near_radius + tolerance:
        return Branch.NEAR
    if separation <= receive_radius + tolerance:
        return Branch.DIRECTION
    return Branch.NO_SIGNAL


def pure_angle_diameter(
    first_point: Point,
    first_bearing_deg: float,
    second_point: Point,
    second_bearing_deg: float,
    *,
    error_deg: float = 1.0,
    tolerance: float = 1e-10,
    verify: bool = False,
) -> tuple[float, str]:
    """返回扩展直径及底层 Q1 状态。"""

    result = solve_observations(
        [
            (first_point[0], first_point[1], first_bearing_deg),
            (second_point[0], second_point[1], second_bearing_deg),
        ],
        error_deg=error_deg,
        tolerance=tolerance,
        verify=verify,
    )
    if result.status is RegionStatus.VALID and result.diameter is not None:
        return (result.diameter, result.status.value)
    return (math.inf, result.status.value)


@dataclass(frozen=True)
class AngleQualityTable:
    """函数 f_B(theta) 的周期性点估计表。"""

    step_deg: float
    diameters: tuple[float, ...]
    statuses: tuple[str, ...]

    @classmethod
    def build(
        cls,
        first_point: Point,
        first_bearing_deg: float,
        second_point: Point,
        *,
        error_deg: float,
        requested_step_deg: float,
        tolerance: float = 1e-10,
        verify: bool = False,
    ) -> "AngleQualityTable":
        if not math.isfinite(requested_step_deg) or requested_step_deg <= 0.0:
            raise ValueError("requested_step_deg 必须是正有限数")
        # 误差区间为正时，若节点间距大于区间全宽，
        # [true-error, true+error] 内可能没有有效表格节点。
        effective_step = (
            min(requested_step_deg, 2.0 * error_deg)
            if error_deg > 0.0
            else requested_step_deg
        )
        count = max(8, math.ceil(360.0 / effective_step))
        step = 360.0 / count
        diameters: list[float] = []
        statuses: list[str] = []
        for index in range(count):
            value, status = pure_angle_diameter(
                first_point,
                first_bearing_deg,
                second_point,
                index * step,
                error_deg=error_deg,
                tolerance=tolerance,
                verify=verify,
            )
            diameters.append(value)
            statuses.append(status)
        return cls(step, tuple(diameters), tuple(statuses))

    def worst_for_true_bearing(self, true_bearing_deg: float, error_deg: float) -> float:
        if not math.isfinite(error_deg) or error_deg < 0.0:
            raise ValueError("error_deg 必须是非负有限数")
        count = len(self.diameters)
        center = int(round(normalize_angle_deg(true_bearing_deg) / self.step_deg)) % count
        span = math.ceil(error_deg / self.step_deg) + 1
        selected: list[float] = []
        for offset in range(-span, span + 1):
            index = (center + offset) % count
            angle = index * self.step_deg
            if circular_distance_deg(angle, true_bearing_deg) <= error_deg + 1e-12:
                selected.append(self.diameters[index])
        if not selected:
            selected.append(self.diameters[center])
        return max(selected)

    def status_counts(self) -> dict[str, int]:
        return dict(sorted(Counter(self.statuses).items()))


__all__ = [
    "AngleQualityTable",
    "Branch",
    "Point",
    "bearing_deg",
    "circular_distance_deg",
    "classify_branch",
    "distance",
    "normalize_angle_deg",
    "pure_angle_diameter",
    "ray_disk_interval",
]
