from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

Point = tuple[float, float]


@dataclass(frozen=True, slots=True)
class LocalCoverCell:
    low_u: float
    high_u: float
    low_v: float
    high_v: float

    @property
    def center(self) -> Point:
        return (
            0.5 * (self.low_u + self.high_u),
            0.5 * (self.low_v + self.high_v),
        )

    @property
    def covering_radius_m(self) -> float:
        return math.hypot(
            0.5 * (self.high_u - self.low_u),
            0.5 * (self.high_v - self.low_v),
        )


@dataclass(frozen=True, slots=True)
class CertifiedStripPlan:
    points: tuple[Point, ...]
    cells: tuple[LocalCoverCell, ...]
    estimated_time_s: float
    certified_radius_m: float
    maximum_cell_radius_m: float
    longitudinal_step_m: float


def _distance(first: Point, second: Point) -> float:
    return math.hypot(first[0] - second[0], first[1] - second[1])


def estimate_full_clear_time_s(points: Sequence[Point], current: Point) -> float:
    """最坏路线代价"""
    if not points:
        return 0.0
    distance_m = _distance(current, points[0]) + sum(
        _distance(first, second)
        for first, second in zip(points, points[1:])
    )
    return distance_m / 5.0 + 3.0 * max(0, len(points) - 1) + 5.0


def _clip_at_u(
    polygon: Sequence[Point], boundary: float, *, keep_greater: bool
) -> list[Point]:
    if not polygon:
        return []

    def inside(point: Point) -> bool:
        if keep_greater:
            return point[0] >= boundary - 1e-10
        return point[0] <= boundary + 1e-10

    result: list[Point] = []
    previous = polygon[-1]
    previous_inside = inside(previous)
    for current in polygon:
        current_inside = inside(current)
        if current_inside != previous_inside:
            denominator = current[0] - previous[0]
            if abs(denominator) > 1e-15:
                fraction = (boundary - previous[0]) / denominator
                result.append(
                    (
                        boundary,
                        previous[1] + fraction * (current[1] - previous[1]),
                    )
                )
        if current_inside:
            result.append(current)
        previous = current
        previous_inside = current_inside
    return result


def _clip_to_strip(
    polygon: Sequence[Point], low_u: float, high_u: float
) -> list[Point]:
    return _clip_at_u(
        _clip_at_u(polygon, low_u, keep_greater=True),
        high_u,
        keep_greater=False,
    )


def _localize(
    polygon: Sequence[Point], origin: Point, bearing_deg: float
) -> tuple[list[Point], tuple[float, float, float, float]]:
    angle = math.radians(bearing_deg)
    ux, uy = math.cos(angle), math.sin(angle)
    vx, vy = -uy, ux
    local = [
        (
            (point[0] - origin[0]) * ux + (point[1] - origin[1]) * uy,
            (point[0] - origin[0]) * vx + (point[1] - origin[1]) * vy,
        )
        for point in polygon
    ]
    return local, (ux, uy, vx, vy)


def _globalize(
    point: Point,
    origin: Point,
    frame: tuple[float, float, float, float],
) -> Point:
    ux, uy, vx, vy = frame
    return (
        origin[0] + point[0] * ux + point[1] * vx,
        origin[1] + point[0] * uy + point[1] * vy,
    )


def _ordered_points(
    cells_by_strip: Sequence[Sequence[LocalCoverCell]],
    *,
    reverse_strips: bool,
    origin: Point,
    frame: tuple[float, float, float, float],
    current: Point,
) -> tuple[Point, ...]:
    strips: Iterable[Sequence[LocalCoverCell]] = cells_by_strip
    if reverse_strips:
        strips = reversed(cells_by_strip)
    route: list[Point] = []
    cursor = current
    for strip in strips:
        candidates = sorted(
            (_globalize(cell.center, origin, frame) for cell in strip),
            key=lambda point: (
                (point[0] - origin[0]) * frame[2]
                + (point[1] - origin[1]) * frame[3]
            ),
        )
        if not candidates:
            continue
        if _distance(cursor, candidates[-1]) < _distance(cursor, candidates[0]):
            candidates.reverse()
        route.extend(candidates)
        cursor = candidates[-1]
    return tuple(route)


def _candidate_steps(radius_m: float) -> tuple[float, ...]:
    raw = (
        0.80 * radius_m,
        1.00 * radius_m,
        1.20 * radius_m,
        26.0,
        1.40 * radius_m,
        1.60 * radius_m,
        1.80 * radius_m,
    )
    return tuple(
        sorted(
            {
                round(step, 10)
                for step in raw
                if 0.0 < step < 2.0 * radius_m
            }
        )
    )


def build_certified_strip_plan(
    polygon: Sequence[Point],
    *,
    origin: Point,
    bearing_deg: float,
    current: Point,
    certified_radius_m: float = 19.5,
) -> CertifiedStripPlan | None:
    if not polygon or certified_radius_m <= 0.0:
        return None
    if any(not (math.isfinite(x) and math.isfinite(y)) for x, y in polygon):
        return None

    local, frame = _localize(polygon, origin, bearing_deg)
    min_u = min(point[0] for point in local)
    max_u = max(point[0] for point in local)
    span_u = max_u - min_u
    best: CertifiedStripPlan | None = None
    padding_m = 1e-7

    for requested_step in _candidate_steps(certified_radius_m):
        strip_count = max(1, math.ceil(span_u / requested_step))
        step = span_u / strip_count if span_u > 1e-12 else 0.0
        half_step = 0.5 * step
        if half_step >= certified_radius_m:
            continue
        maximum_band_height = 2.0 * math.sqrt(
            max(0.0, certified_radius_m**2 - half_step**2)
        )
        if maximum_band_height <= 0.0:
            continue

        cells_by_strip: list[list[LocalCoverCell]] = []
        valid = True
        for index in range(strip_count):
            low_u = min_u + index * step
            high_u = max_u if index + 1 == strip_count else low_u + step
            clipped = _clip_to_strip(local, low_u, high_u)
            if not clipped:
                cells_by_strip.append([])
                continue
            low_v = min(point[1] for point in clipped) - padding_m
            high_v = max(point[1] for point in clipped) + padding_m
            width_v = max(0.0, high_v - low_v)
            band_count = max(1, math.ceil(width_v / maximum_band_height))
            band_height = width_v / band_count
            strip_cells: list[LocalCoverCell] = []
            for band in range(band_count):
                cell = LocalCoverCell(
                    low_u=low_u,
                    high_u=high_u,
                    low_v=low_v + band * band_height,
                    high_v=(
                        high_v
                        if band + 1 == band_count
                        else low_v + (band + 1) * band_height
                    ),
                )
                if cell.covering_radius_m > certified_radius_m + 1e-9:
                    valid = False
                    break
                strip_cells.append(cell)
            if not valid:
                break
            cells_by_strip.append(strip_cells)
        if not valid:
            continue

        cells = tuple(cell for strip in cells_by_strip for cell in strip)
        if not cells:
            continue
        route_candidates = (
            _ordered_points(
                cells_by_strip,
                reverse_strips=False,
                origin=origin,
                frame=frame,
                current=current,
            ),
            _ordered_points(
                cells_by_strip,
                reverse_strips=True,
                origin=origin,
                frame=frame,
                current=current,
            ),
        )
        points = min(
            route_candidates,
            key=lambda route: estimate_full_clear_time_s(route, current),
        )
        plan = CertifiedStripPlan(
            points=points,
            cells=cells,
            estimated_time_s=estimate_full_clear_time_s(points, current),
            certified_radius_m=certified_radius_m,
            maximum_cell_radius_m=max(
                cell.covering_radius_m for cell in cells
            ),
            longitudinal_step_m=step,
        )
        if best is None or plan.estimated_time_s < best.estimated_time_s:
            best = plan
    return best


__all__ = [
    "CertifiedStripPlan",
    "LocalCoverCell",
    "build_certified_strip_plan",
    "estimate_full_clear_time_s",
]
