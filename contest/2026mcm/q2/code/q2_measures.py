"""Q2 三类反馈分支的自适应面积测度。"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

from q2_geometry import Point, distance, ray_disk_interval
from q2_state import FirstObservation, Q2Config


@dataclass(frozen=True)
class BranchAreas:
    active_area_m2: float
    near_area_m2: float
    direction_area_m2: float
    no_signal_area_m2: float

    @property
    def effective_area_m2(self) -> float:
        return self.near_area_m2 + self.direction_area_m2


def _intersection_interval(
    first: Point,
    angle_rad: float,
    config: Q2Config,
    receive_radius: float,
    disk_center: Point | None,
    disk_radius: float | None,
) -> tuple[float, float] | None:
    target = ray_disk_interval(first, angle_rad, config.center, config.target_radius)
    if target is None:
        return None
    lower = max(config.near_radius, target[0])
    upper = min(receive_radius, target[1])
    if disk_center is not None and disk_radius is not None:
        if disk_radius <= 0.0:
            return None
        disk = ray_disk_interval(first, angle_rad, disk_center, disk_radius)
        if disk is None:
            return None
        lower = max(lower, disk[0])
        upper = min(upper, disk[1])
    return None if upper <= lower else (lower, upper)


def _radial_area_integrand(
    angle_rad: float,
    first: Point,
    config: Q2Config,
    receive_radius: float,
    disk_center: Point | None,
    disk_radius: float | None,
) -> float:
    interval = _intersection_interval(
        first, angle_rad, config, receive_radius, disk_center, disk_radius
    )
    if interval is None:
        return 0.0
    return 0.5 * (interval[1] * interval[1] - interval[0] * interval[0])


def _relative_angle(angle: float, center: float) -> float:
    return math.atan2(math.sin(angle - center), math.cos(angle - center))


def _disk_tangent_breakpoints(
    origin: Point,
    disk_center: Point,
    disk_radius: float,
    wedge_center: float,
    half_width: float,
) -> list[float]:
    separation = distance(origin, disk_center)
    if separation <= disk_radius or separation == 0.0:
        return []
    center_angle = math.atan2(disk_center[1] - origin[1], disk_center[0] - origin[0])
    relative_center = _relative_angle(center_angle, wedge_center)
    tangent = math.asin(min(1.0, disk_radius / separation))
    values: list[float] = []
    for base in (relative_center - tangent, relative_center + tangent):
        for shift in (-2.0 * math.pi, 0.0, 2.0 * math.pi):
            value = base + shift
            if -half_width < value < half_width:
                values.append(value)
    return values


def _simpson(function: Callable[[float], float], left: float, right: float) -> tuple[float, float, float, float]:
    middle = 0.5 * (left + right)
    f_left = function(left)
    f_middle = function(middle)
    f_right = function(right)
    value = (right - left) * (f_left + 4.0 * f_middle + f_right) / 6.0
    return value, f_left, f_middle, f_right


def _adaptive_simpson(
    function: Callable[[float], float],
    left: float,
    right: float,
    tolerance: float,
    max_depth: int,
) -> float:
    whole, f_left, f_middle, f_right = _simpson(function, left, right)

    def recurse(
        a: float,
        b: float,
        fa: float,
        fm: float,
        fb: float,
        estimate: float,
        local_tolerance: float,
        depth: int,
    ) -> float:
        middle = 0.5 * (a + b)
        left_middle = 0.5 * (a + middle)
        right_middle = 0.5 * (middle + b)
        f_left_middle = function(left_middle)
        f_right_middle = function(right_middle)
        left_estimate = (middle - a) * (fa + 4.0 * f_left_middle + fm) / 6.0
        right_estimate = (b - middle) * (fm + 4.0 * f_right_middle + fb) / 6.0
        refined = left_estimate + right_estimate
        if depth <= 0 or abs(refined - estimate) <= 15.0 * local_tolerance:
            return refined + (refined - estimate) / 15.0
        return recurse(
            a, middle, fa, f_left_middle, fm, left_estimate,
            0.5 * local_tolerance, depth - 1,
        ) + recurse(
            middle, b, fm, f_right_middle, fb, right_estimate,
            0.5 * local_tolerance, depth - 1,
        )

    return recurse(
        left, right, f_left, f_middle, f_right, whole, tolerance, max_depth
    )


def _area_in_disk(
    first: FirstObservation,
    config: Q2Config,
    receive_radius: float,
    disk_center: Point | None,
    disk_radius: float | None,
    *,
    base_segments: int,
    relative_tolerance: float,
    max_depth: int,
) -> float:
    center_angle = math.radians(first.bearing_deg)
    half_width = math.radians(config.error_deg)
    if half_width <= 0.0:
        return 0.0
    points = [
        -half_width + 2.0 * half_width * index / base_segments
        for index in range(base_segments + 1)
    ]
    points.extend(
        _disk_tangent_breakpoints(
            first.point, config.center, config.target_radius, center_angle, half_width
        )
    )
    if disk_center is not None and disk_radius is not None and disk_radius > 0.0:
        points.extend(
            _disk_tangent_breakpoints(
                first.point, disk_center, disk_radius, center_angle, half_width
            )
        )
    points = sorted(set(points))
    scale = max(1.0, config.target_radius * config.target_radius * 2.0 * half_width)
    interval_tolerance = relative_tolerance * scale / max(1, len(points) - 1)

    def integrand(delta: float) -> float:
        return _radial_area_integrand(
            center_angle + delta,
            first.point,
            config,
            receive_radius,
            disk_center,
            disk_radius,
        )

    return max(
        0.0,
        sum(
            _adaptive_simpson(
                integrand, left, right, interval_tolerance, max_depth
            )
            for left, right in zip(points, points[1:])
            if right > left
        ),
    )


def branch_areas(
    candidate: Point,
    first: FirstObservation,
    config: Q2Config,
    receive_radius: float,
    *,
    base_segments: int = 128,
    relative_tolerance: float = 1e-9,
    max_depth: int = 12,
) -> BranchAreas:
    """计算固定 R 下 S1、near、direction 与 no_signal 分支的面积。"""

    first.validate()
    config.validate()
    if not config.receive_min <= receive_radius <= config.receive_max:
        raise ValueError("接收半径必须位于配置范围内")
    if base_segments <= 0 or relative_tolerance <= 0.0 or max_depth < 0:
        raise ValueError("面积积分控制参数无效")

    active = _area_in_disk(
        first, config, receive_radius, None, None,
        base_segments=base_segments,
        relative_tolerance=relative_tolerance,
        max_depth=max_depth,
    )
    if active <= 0.0:
        return BranchAreas(0.0, 0.0, 0.0, 0.0)
    effective = _area_in_disk(
        first, config, receive_radius, candidate, receive_radius,
        base_segments=base_segments,
        relative_tolerance=relative_tolerance,
        max_depth=max_depth,
    )
    near = _area_in_disk(
        first, config, receive_radius, candidate, config.near_radius,
        base_segments=base_segments,
        relative_tolerance=relative_tolerance,
        max_depth=max_depth,
    )
    effective = min(active, max(0.0, effective))
    near = min(effective, max(0.0, near))
    direction = max(0.0, effective - near)
    no_signal = max(0.0, active - effective)
    return BranchAreas(active, near, direction, no_signal)


__all__ = ["BranchAreas", "branch_areas"]
