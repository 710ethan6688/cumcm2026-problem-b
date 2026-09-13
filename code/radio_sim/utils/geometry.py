"""题目角度约定下的二维几何函数。"""

from __future__ import annotations

from math import atan2, degrees, hypot

from radio_sim.domain.models import Position

_EPSILON = 1e-9


def distance(a: Position, b: Position) -> float:
    return hypot(b.x - a.x, b.y - a.y)


def bearing_deg(origin: Position, target: Position) -> float:
    """返回以正东为 0、逆时针为正且位于 [0, 360) 的示向角。"""
    if distance(origin, target) <= _EPSILON:
        raise ValueError("bearing is undefined for coincident points")
    return degrees(atan2(target.y - origin.y, target.x - origin.x)) % 360.0


def circular_difference_deg(a: float, b: float) -> float:
    """返回位于 [-180, 180) 的带符号最短角差 a-b。"""
    return (a - b + 180.0) % 360.0 - 180.0


def in_directional_coverage(
    source_position: Position,
    source_direction_deg: float,
    receiver_position: Position,
    half_angle_deg: float = 90.0,
) -> bool:
    # 在干扰源中心，极角没有定义。将该点视为处于覆盖范围内，
    # 是已记录的本地仿真约定，而不是官方场景生成事实。
    if distance(source_position, receiver_position) <= _EPSILON:
        return True
    receiver_bearing = bearing_deg(source_position, receiver_position)
    return abs(circular_difference_deg(receiver_bearing, source_direction_deg)) <= (
        half_angle_deg + _EPSILON
    )
