"""Q2 接收安全性的认证界。

上界使用极坐标单元覆盖 K1 的超集。由于
g_B(s)=||s-B||-max(R_min,||s-A||) 满足 2-Lipschitz 条件，
每个保留单元都有严格的几何上界（浮点运算误差除外）。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from q2_geometry import Point, distance
from q2_state import FirstObservation, Q2Config


class GammaStatus(str, Enum):
    CERTIFIED_SAFE = "CERTIFIED_SAFE"
    CERTIFIED_UNSAFE = "CERTIFIED_UNSAFE"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class GammaCertificate:
    status: GammaStatus
    lower_bound_m: float
    upper_bound_m: float
    refinement_rounds: int
    retained_cell_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "lower_bound_m": self.lower_bound_m,
            "upper_bound_m": self.upper_bound_m,
            "refinement_rounds": self.refinement_rounds,
            "retained_cell_count": self.retained_cell_count,
            "method": "polar-cell cover with 2-Lipschitz upper bounds",
        }


@dataclass(frozen=True)
class _Cell:
    angle_lo: float
    angle_hi: float
    radius_lo: float
    radius_hi: float


def _point(first: Point, angle: float, radius: float) -> Point:
    return (first[0] + radius * math.cos(angle), first[1] + radius * math.sin(angle))


def _cell_geometry(cell: _Cell, origin: Point) -> tuple[Point, float]:
    angle = 0.5 * (cell.angle_lo + cell.angle_hi)
    radius = 0.5 * (cell.radius_lo + cell.radius_hi)
    center = _point(origin, angle, radius)
    corners = (
        _point(origin, cell.angle_lo, cell.radius_lo),
        _point(origin, cell.angle_lo, cell.radius_hi),
        _point(origin, cell.angle_hi, cell.radius_lo),
        _point(origin, cell.angle_hi, cell.radius_hi),
    )
    return center, max(distance(center, corner) for corner in corners)


def _g(source: Point, candidate: Point, first: Point, receive_min: float) -> float:
    return distance(source, candidate) - max(receive_min, distance(source, first))


def _split(cell: _Cell) -> tuple[_Cell, ...]:
    angle_mid = 0.5 * (cell.angle_lo + cell.angle_hi)
    radius_mid = 0.5 * (cell.radius_lo + cell.radius_hi)
    if cell.angle_hi == cell.angle_lo:
        return (
            _Cell(cell.angle_lo, cell.angle_hi, cell.radius_lo, radius_mid),
            _Cell(cell.angle_lo, cell.angle_hi, radius_mid, cell.radius_hi),
        )
    return (
        _Cell(cell.angle_lo, angle_mid, cell.radius_lo, radius_mid),
        _Cell(cell.angle_lo, angle_mid, radius_mid, cell.radius_hi),
        _Cell(angle_mid, cell.angle_hi, cell.radius_lo, radius_mid),
        _Cell(angle_mid, cell.angle_hi, radius_mid, cell.radius_hi),
    )


def certify_gamma(
    candidate: Point,
    first: FirstObservation,
    config: Q2Config,
    *,
    initial_angle_cells: int = 8,
    initial_radial_cells: int = 12,
    max_rounds: int = 8,
    max_cells: int = 200_000,
) -> GammaCertificate:
    """计算 Gamma 在 K1 上的上下界，并在可行时认证其符号。"""

    first.validate()
    config.validate()
    if initial_angle_cells <= 0 or initial_radial_cells <= 0:
        raise ValueError("初始单元数量必须为正数")
    half = math.radians(config.error_deg)
    center_angle = math.radians(first.bearing_deg % 360.0)
    angle_count = 1 if half == 0.0 else initial_angle_cells
    cells: list[_Cell] = []
    for ai in range(angle_count):
        alo = center_angle - half + 2.0 * half * ai / angle_count
        ahi = center_angle - half + 2.0 * half * (ai + 1) / angle_count
        for ri in range(initial_radial_cells):
            rlo = config.near_radius + (config.receive_max - config.near_radius) * ri / initial_radial_cells
            rhi = config.near_radius + (config.receive_max - config.near_radius) * (ri + 1) / initial_radial_cells
            cells.append(_Cell(alo, ahi, rlo, rhi))

    lower = -math.inf
    upper = math.inf
    retained_count = 0
    for round_index in range(max_rounds + 1):
        retained: list[tuple[_Cell, float]] = []
        upper = -math.inf
        for cell in cells:
            center, cell_radius = _cell_geometry(cell, first.point)
            # 若包围球与目标圆盘不相交，则该单元不可能包含可行源，
            # 因而无需计入。
            if distance(center, config.center) - cell_radius > config.target_radius:
                continue
            value = _g(center, candidate, first.point, config.receive_min)
            cell_upper = value + 2.0 * cell_radius
            upper = max(upper, cell_upper)
            retained.append((cell, cell_upper))
            if (
                distance(center, config.center) <= config.target_radius
                and distance(center, first.point) > config.near_radius
            ):
                lower = max(lower, value)
        retained_count = len(retained)
        if upper <= 0.0:
            return GammaCertificate(
                GammaStatus.CERTIFIED_SAFE, lower, upper, round_index, retained_count
            )
        if lower > 0.0:
            return GammaCertificate(
                GammaStatus.CERTIFIED_UNSAFE, lower, upper, round_index, retained_count
            )
        if round_index == max_rounds or retained_count == 0:
            break
        # 只有上界仍可能跨过零点的单元才会影响符号判定。
        next_cells: list[_Cell] = []
        for cell, cell_upper in retained:
            if cell_upper > 0.0:
                next_cells.extend(_split(cell))
        if not next_cells or len(next_cells) > max_cells:
            break
        cells = next_cells

    return GammaCertificate(
        GammaStatus.UNRESOLVED, lower, upper, round_index, retained_count
    )


__all__ = ["GammaCertificate", "GammaStatus", "certify_gamma"]
