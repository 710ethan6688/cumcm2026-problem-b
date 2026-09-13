"""为 Q2 原型构造第一次观测后的状态域。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from q2_geometry import Point, distance, normalize_angle_deg, ray_disk_interval


class DomainStatus(str, Enum):
    EMPTY = "EMPTY"
    DEGENERATE = "DEGENERATE"
    REGULAR = "REGULAR"


@dataclass(frozen=True)
class Q2Config:
    center: Point = (0.0, 0.0)
    target_radius: float = 1800.0
    error_deg: float = 1.0
    near_radius: float = 5.0
    receive_min: float = 1000.0
    receive_max: float = 1500.0

    def validate(self) -> None:
        values = (*self.center, self.target_radius, self.error_deg, self.near_radius,
                  self.receive_min, self.receive_max)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("配置值必须是有限数")
        if self.target_radius <= 0.0 or self.error_deg < 0.0:
            raise ValueError("target_radius 必须为正数，error_deg 必须非负")
        if not 0.0 <= self.near_radius < self.receive_min < self.receive_max:
            raise ValueError("参数必须满足 0 <= near_radius < receive_min < receive_max")


@dataclass(frozen=True)
class FirstObservation:
    point: Point
    bearing_deg: float

    def validate(self) -> None:
        if not all(math.isfinite(value) for value in (*self.point, self.bearing_deg)):
            raise ValueError("第一次观测值必须是有限数")


@dataclass(frozen=True)
class SourceCell:
    point: Point
    distance_from_first: float
    weight_m2: float


@dataclass(frozen=True)
class StateDomain:
    status: DomainStatus
    samples: tuple[SourceCell, ...]
    support_points: tuple[Point, ...]
    possible_radius_range: tuple[float, float] | None
    area_radius_range: tuple[float, float] | None
    approximate_area_m2: float
    angle_cells: int
    radial_cells: int

    @property
    def has_positive_area(self) -> bool:
        return self.status is DomainStatus.REGULAR and bool(self.samples)


def _clip_interval(
    interval: tuple[float, float] | None,
    lower: float,
    upper: float,
    *,
    tolerance: float,
) -> tuple[float, float] | None:
    if interval is None:
        return None
    lo = max(interval[0], lower)
    hi = min(interval[1], upper)
    # 第一次观测返回 direction，因此 ||s-A|| > near_radius。
    # 恰好位于 near 边界上的单点在逻辑上并不相容。
    if hi <= lower + tolerance or hi < lo - tolerance:
        return None
    return (lo, hi)


def _point_on_ray(origin: Point, angle_rad: float, radius: float) -> Point:
    return (
        origin[0] + radius * math.cos(angle_rad),
        origin[1] + radius * math.sin(angle_rad),
    )


def build_state_domain(
    first: FirstObservation,
    config: Q2Config,
    *,
    angle_cells: int = 25,
    radial_cells: int = 20,
    tolerance: float = 1e-9,
) -> StateDomain:
    """近似构造 K1，同时单独保留零面积的可能状态。"""

    first.validate()
    config.validate()
    if angle_cells <= 0 or radial_cells <= 0:
        raise ValueError("angle_cells 和 radial_cells 必须为正数")

    center_rad = math.radians(normalize_angle_deg(first.bearing_deg))
    half_width = math.radians(config.error_deg)
    angle_width = 2.0 * half_width / angle_cells if angle_cells else 0.0
    sample_cells: list[SourceCell] = []
    support_points: list[Point] = []
    logical_radii: list[float] = []

    # 边界对 I_poss 很重要：切点或单个径向端点即使 Lebesgue 面积为零，
    # 在逻辑上仍可能出现。
    boundary_angles = [center_rad - half_width, center_rad + half_width]
    if config.error_deg == 0.0:
        boundary_angles = [center_rad]
    for angle in boundary_angles:
        interval = _clip_interval(
            ray_disk_interval(first.point, angle, config.center, config.target_radius),
            config.near_radius,
            config.receive_max,
            tolerance=tolerance,
        )
        if interval is None:
            continue
        logical_radii.extend(interval)
        support_points.extend(
            [_point_on_ray(first.point, angle, interval[0]),
             _point_on_ray(first.point, angle, interval[1])]
        )

    if config.error_deg == 0.0:
        mid_angles = [center_rad]
        cell_widths = [0.0]
    else:
        mid_angles = [center_rad - half_width + (index + 0.5) * angle_width
                      for index in range(angle_cells)]
        cell_widths = [angle_width] * angle_cells

    for angle, cell_width in zip(mid_angles, cell_widths):
        interval = _clip_interval(
            ray_disk_interval(first.point, angle, config.center, config.target_radius),
            config.near_radius,
            config.receive_max,
            tolerance=tolerance,
        )
        if interval is None:
            continue
        lo, hi = interval
        logical_radii.extend((lo, hi))
        support_points.extend(
            [_point_on_ray(first.point, angle, lo), _point_on_ray(first.point, angle, hi)]
        )
        if cell_width <= 0.0 or hi <= lo + tolerance:
            continue
        lo2 = lo * lo
        hi2 = hi * hi
        for radial_index in range(radial_cells):
            left2 = lo2 + (hi2 - lo2) * radial_index / radial_cells
            right2 = lo2 + (hi2 - lo2) * (radial_index + 1) / radial_cells
            radius = math.sqrt(0.5 * (left2 + right2))
            weight = 0.5 * (right2 - left2) * cell_width
            sample_cells.append(
                SourceCell(_point_on_ray(first.point, angle, radius), radius, weight)
            )

    if not logical_radii:
        return StateDomain(
            DomainStatus.EMPTY, (), (), None, None, 0.0, angle_cells, radial_cells
        )

    possible_low = max(config.receive_min, min(logical_radii))
    possible_range = (
        (possible_low, config.receive_max)
        if possible_low <= config.receive_max + tolerance
        else None
    )
    positive_samples = tuple(cell for cell in sample_cells if cell.weight_m2 > 0.0)
    if not positive_samples:
        status = DomainStatus.DEGENERATE if possible_range is not None else DomainStatus.EMPTY
        return StateDomain(
            status, (), tuple(support_points), possible_range, None, 0.0,
            angle_cells, radial_cells
        )

    area_low = max(config.receive_min, min(cell.distance_from_first for cell in positive_samples))
    area_range = (
        (area_low, config.receive_max)
        if area_low <= config.receive_max + tolerance
        else None
    )
    if possible_range is None or area_range is None:
        return StateDomain(
            DomainStatus.EMPTY, (), tuple(support_points), possible_range, area_range,
            0.0, angle_cells, radial_cells
        )
    return StateDomain(
        DomainStatus.REGULAR,
        positive_samples,
        tuple(support_points),
        possible_range,
        area_range,
        sum(cell.weight_m2 for cell in positive_samples),
        angle_cells,
        radial_cells,
    )


def radius_grid(domain: StateDomain, count: int) -> tuple[float, ...]:
    if count < 2:
        raise ValueError("接收半径节点数必须至少为 2")
    if domain.area_radius_range is None:
        return ()
    lo, hi = domain.area_radius_range
    if math.isclose(lo, hi):
        return (lo,)
    return tuple(lo + (hi - lo) * index / (count - 1) for index in range(count))


def candidate_grid(
    domain: StateDomain,
    first: FirstObservation,
    config: Q2Config,
    *,
    step_m: float,
    max_candidates: int = 400,
) -> tuple[Point, ...]:
    """在 K1 周围构建粗粒度 B0 栅格，但不声称覆盖连续空间。"""

    if not math.isfinite(step_m) or step_m <= 0.0:
        raise ValueError("step_m 必须是正有限数")
    if max_candidates <= 0:
        raise ValueError("max_candidates 必须为正数")
    # 使用边界支撑点而非求积单元中心，避免角度或径向积分分辨率变化时
    # 栅格原点发生漂移。
    points = list(domain.support_points) or [cell.point for cell in domain.samples]
    if not points:
        return ()
    min_x = math.floor((min(point[0] for point in points) - config.receive_max) / step_m) * step_m
    max_x = math.ceil((max(point[0] for point in points) + config.receive_max) / step_m) * step_m
    min_y = math.floor((min(point[1] for point in points) - config.receive_max) / step_m) * step_m
    max_y = math.ceil((max(point[1] for point in points) + config.receive_max) / step_m) * step_m
    nx = math.floor((max_x - min_x) / step_m) + 1
    ny = math.floor((max_y - min_y) / step_m) + 1
    if nx * ny > max_candidates:
        required = math.sqrt((max_x - min_x) * (max_y - min_y) / max_candidates)
        raise ValueError(
            f"候选栅格将包含 {nx * ny} 个点；"
            f"请将 --candidate-step 增大到约 {required:.1f} m，或提高数量上限"
        )
    candidates: list[Point] = []
    for ix in range(nx):
        x = min_x + ix * step_m
        for iy in range(ny):
            point = (x, min_y + iy * step_m)
            # 该包围盒是 B0 的保守有限超集；诊断原型有意避免按样本剪枝。
            if distance(point, first.point) > 1e-9:
                candidates.append(point)
    return tuple(candidates)


__all__ = [
    "DomainStatus",
    "FirstObservation",
    "Q2Config",
    "SourceCell",
    "StateDomain",
    "build_state_domain",
    "candidate_grid",
    "radius_grid",
]
