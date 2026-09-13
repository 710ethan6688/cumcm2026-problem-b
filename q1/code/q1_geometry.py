from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Any, Iterable, Sequence


Point = tuple[float, float]


class RegionStatus(str, Enum):
    VALID = "VALID"
    EMPTY = "EMPTY"
    UNBOUNDED = "UNBOUNDED"
    DEGENERATE = "DEGENERATE"
    NUMERICALLY_UNCERTAIN = "NUMERICALLY_UNCERTAIN"


@dataclass(frozen=True)
class HalfPlane:

    q: Point
    d: Point
    source: str = ""


@dataclass
class Q1Result:
    status: RegionStatus
    vertices: tuple[Point, ...] = ()
    diameter: float | None = None
    diameter_pair: tuple[Point, Point] | None = None
    circle_center: Point | None = None
    covered: bool | None = None
    max_violation: float | None = None
    violating_vertex: Point | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "vertices": [list(point) for point in self.vertices],
            "diameter": self.diameter,
            "diameter_pair": (
                [list(self.diameter_pair[0]), list(self.diameter_pair[1])]
                if self.diameter_pair is not None
                else None
            ),
            "circle_center": list(self.circle_center) if self.circle_center else None,
            "covered": self.covered,
            "max_violation": self.max_violation,
            "violating_vertex": (
                list(self.violating_vertex) if self.violating_vertex else None
            ),
            "diagnostics": self.diagnostics,
        }


def _add(a: Point, b: Point) -> Point:
    return (a[0] + b[0], a[1] + b[1])


def _sub(a: Point, b: Point) -> Point:
    return (a[0] - b[0], a[1] - b[1])


def _mul(a: Point, value: float) -> Point:
    return (a[0] * value, a[1] * value)


def _dot(a: Point, b: Point) -> float:
    return a[0] * b[0] + a[1] * b[1]


def _cross(a: Point, b: Point) -> float:
    return a[0] * b[1] - a[1] * b[0]


def _norm_sq(a: Point) -> float:
    return _dot(a, a)


def _distance_sq(a: Point, b: Point) -> float:
    return _norm_sq(_sub(a, b))


def make_halfplane(q: Point, d: Point, source: str = "") -> HalfPlane:
    values = (*q, *d)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("半平面的坐标与方向必须是有限数")
    length = math.hypot(d[0], d[1])
    if length == 0.0:
        raise ValueError("半平面方向不能为零向量")
    return HalfPlane((float(q[0]), float(q[1])), (d[0] / length, d[1] / length), source)


def bearing_halfplanes(
    observations: Sequence[tuple[float, float, float]],
    error_deg: float = 1.0,
) -> list[HalfPlane]:
    """将 ``(x, y, bearing_degrees)`` 观测转换为 2n 个约束。"""

    if not observations:
        raise ValueError("至少需要一条示向观测")
    if not math.isfinite(error_deg) or not 0.0 < error_deg < 90.0:
        raise ValueError("error_deg 必须是位于 (0, 90) 内的有限数")

    epsilon = math.radians(error_deg)
    result: list[HalfPlane] = []
    for index, (x, y, bearing_deg) in enumerate(observations):
        if not all(math.isfinite(value) for value in (x, y, bearing_deg)):
            raise ValueError("观测值必须是有限数")
        theta = math.radians(bearing_deg % 360.0)
        lower = (math.cos(theta - epsilon), math.sin(theta - epsilon))
        upper = (math.cos(theta + epsilon), math.sin(theta + epsilon))
        q = (float(x), float(y))
        result.append(make_halfplane(q, lower, f"observation_{index}:lower"))
        result.append(make_halfplane(q, (-upper[0], -upper[1]), f"observation_{index}:upper"))
    return result


def side(line: HalfPlane, point: Point) -> float:
    return _cross(line.d, _sub(point, line.q))


def contains(line: HalfPlane, point: Point, tolerance: float = 1e-10) -> bool:
    return side(line, point) >= -tolerance


def _line_intersection(
    first: HalfPlane,
    second: HalfPlane,
    parallel_tolerance: float,
) -> Point | None:
    denominator = _cross(first.d, second.d)
    if abs(denominator) <= parallel_tolerance:
        return None
    parameter = _cross(_sub(second.q, first.q), second.d) / denominator
    return _add(first.q, _mul(first.d, parameter))


def _constraint(line: HalfPlane) -> tuple[float, float, float]:
    # side(d, x-q) >= 0 等价于 (d_y, -d_x) 与 x 的点积不大于其与 q 的点积。
    a = line.d[1]
    b = -line.d[0]
    c = a * line.q[0] + b * line.q[1]
    return (a, b, c)


def _find_feasible_point(
    lines: Sequence[HalfPlane], tolerance: float
) -> Point | None:
    """采用精确结构的增量式二维线性可行性检查。"""

    constraints = [_constraint(line) for line in lines]
    point = (0.0, 0.0)
    for index, (a, b, c) in enumerate(constraints):
        if a * point[0] + b * point[1] <= c + tolerance:
            continue

        normal_sq = a * a + b * b
        base = (a * c / normal_sq, b * c / normal_sq)
        direction = (-b / math.sqrt(normal_sq), a / math.sqrt(normal_sq))
        lower = -math.inf
        upper = math.inf
        for previous_a, previous_b, previous_c in constraints[:index]:
            coefficient = previous_a * direction[0] + previous_b * direction[1]
            allowance = previous_c - previous_a * base[0] - previous_b * base[1]
            if abs(coefficient) <= tolerance:
                if allowance < -tolerance:
                    return None
                continue
            bound = allowance / coefficient
            if coefficient > 0.0:
                upper = min(upper, bound)
            else:
                lower = max(lower, bound)
            if lower > upper + tolerance:
                return None

        if lower <= 0.0 <= upper:
            parameter = 0.0
        elif upper < 0.0:
            parameter = upper
        else:
            parameter = lower
        point = _add(base, _mul(direction, parameter))

    if all(contains(line, point, 10.0 * tolerance) for line in lines):
        return point
    return None


def _has_recession_direction(lines: Sequence[HalfPlane], tolerance: float) -> bool:
    """检查二维集合 {d: A d <= 0} 是否包含非零方向。"""

    if not lines:
        return True
    angles = sorted(
        math.atan2(-line.d[0], line.d[1]) % (2.0 * math.pi) for line in lines
    )
    gaps = [angles[index + 1] - angles[index] for index in range(len(angles) - 1)]
    gaps.append(angles[0] + 2.0 * math.pi - angles[-1])
    # 当且仅当所有约束法向量可落在同一闭半圆内时，衰退锥不是平凡锥；
    # 等价地，它们在圆周上的互补间隙至少为 pi。
    return max(gaps) >= math.pi - 10.0 * tolerance


def _same_direction(first: HalfPlane, second: HalfPlane, tolerance: float) -> bool:
    return abs(_cross(first.d, second.d)) <= tolerance and _dot(first.d, second.d) > 0.0


def _more_restrictive(first: HalfPlane, second: HalfPlane) -> HalfPlane:
    # 方向相同时，更靠左的边界对应更严格的约束。
    return second if side(first, second.q) > 0.0 else first


def _sort_and_merge_same_direction(
    lines: Sequence[HalfPlane], tolerance: float
) -> list[HalfPlane]:
    ordered = sorted(lines, key=lambda line: math.atan2(line.d[1], line.d[0]) % (2.0 * math.pi))
    merged: list[HalfPlane] = []
    for line in ordered:
        if merged and _same_direction(merged[-1], line, tolerance):
            merged[-1] = _more_restrictive(merged[-1], line)
        else:
            merged.append(line)

    if len(merged) > 1 and _same_direction(merged[0], merged[-1], tolerance):
        merged[0] = _more_restrictive(merged[0], merged[-1])
        merged.pop()
    return merged


def _convex_hull(points: Iterable[Point], tolerance: float) -> list[Point]:
    ordered = sorted(points)
    unique: list[Point] = []
    for point in ordered:
        if not unique or _distance_sq(point, unique[-1]) > tolerance * tolerance:
            unique.append(point)
    if len(unique) <= 1:
        return unique

    def turn(o: Point, a: Point, b: Point) -> float:
        return _cross(_sub(a, o), _sub(b, o))

    lower: list[Point] = []
    for point in unique:
        while len(lower) >= 2 and turn(lower[-2], lower[-1], point) <= tolerance:
            lower.pop()
        lower.append(point)
    upper: list[Point] = []
    for point in reversed(unique):
        while len(upper) >= 2 and turn(upper[-2], upper[-1], point) <= tolerance:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def polygon_area(vertices: Sequence[Point]) -> float:
    if len(vertices) < 3:
        return 0.0
    doubled = sum(
        _cross(vertices[index], vertices[(index + 1) % len(vertices)])
        for index in range(len(vertices))
    )
    return 0.5 * abs(doubled)


def halfplane_intersection_main(
    lines: Sequence[HalfPlane], tolerance: float = 1e-10
) -> list[Point]:
    """标准的按角度排序双端队列半平面交算法（正式 B 路径）。"""

    parallel_tolerance = max(tolerance * 0.1, 1e-14)
    ordered = _sort_and_merge_same_direction(lines, parallel_tolerance)
    active: deque[HalfPlane] = deque()

    for line in ordered:
        while len(active) >= 2:
            point = _line_intersection(active[-2], active[-1], parallel_tolerance)
            if point is None:
                break
            if contains(line, point, tolerance):
                break
            active.pop()
        while len(active) >= 2:
            point = _line_intersection(active[0], active[1], parallel_tolerance)
            if point is None:
                break
            if contains(line, point, tolerance):
                break
            active.popleft()
        active.append(line)

    while len(active) >= 3:
        point = _line_intersection(active[-2], active[-1], parallel_tolerance)
        if point is not None and contains(active[0], point, tolerance):
            break
        active.pop()
    while len(active) >= 3:
        point = _line_intersection(active[0], active[1], parallel_tolerance)
        if point is not None and contains(active[-1], point, tolerance):
            break
        active.popleft()

    if len(active) < 3:
        return []
    active_list = list(active)
    vertices: list[Point] = []
    for index, line in enumerate(active_list):
        next_line = active_list[(index + 1) % len(active_list)]
        point = _line_intersection(line, next_line, parallel_tolerance)
        if point is None or not all(
            contains(constraint, point, 20.0 * tolerance) for constraint in lines
        ):
            return []
        vertices.append(point)
    return _convex_hull(vertices, 20.0 * tolerance)


def halfplane_intersection_reference(
    lines: Sequence[HalfPlane], tolerance: float = 1e-10
) -> list[Point]:
    """枚举两两边界交点并进行完整筛选（独立 A 路径）。"""

    parallel_tolerance = max(tolerance * 0.1, 1e-14)
    candidates: list[Point] = []
    for first_index, first in enumerate(lines):
        for second in lines[first_index + 1 :]:
            point = _line_intersection(first, second, parallel_tolerance)
            if point is None:
                continue
            if all(contains(line, point, 20.0 * tolerance) for line in lines):
                candidates.append(point)
    return _convex_hull(candidates, 20.0 * tolerance)


def diameter_bruteforce(vertices: Sequence[Point]) -> tuple[float, tuple[Point, Point]]:
    if not vertices:
        raise ValueError("计算直径至少需要一个顶点")
    best_pair = (vertices[0], vertices[0])
    best_sq = 0.0
    for index, first in enumerate(vertices):
        for second in vertices[index + 1 :]:
            distance_sq = _distance_sq(first, second)
            if distance_sq > best_sq:
                best_sq = distance_sq
                best_pair = (first, second)
    return math.sqrt(best_sq), best_pair


def diameter_rotating_calipers(
    vertices: Sequence[Point], tolerance: float = 1e-10
) -> tuple[float, tuple[Point, Point]]:
    """用线性旋转卡壳法求逆时针凸多边形的直径。"""

    count = len(vertices)
    if count == 0:
        raise ValueError("计算直径至少需要一个顶点")
    if count <= 2:
        return diameter_bruteforce(vertices)

    best_sq = 0.0
    best_pair = (vertices[0], vertices[0])

    def update(first_index: int, second_index: int) -> None:
        nonlocal best_sq, best_pair
        distance_sq = _distance_sq(vertices[first_index], vertices[second_index])
        if distance_sq > best_sq:
            best_sq = distance_sq
            best_pair = (vertices[first_index], vertices[second_index])

    opposite = 1
    for index in range(count):
        next_index = (index + 1) % count
        edge = _sub(vertices[next_index], vertices[index])

        def support(candidate: int) -> float:
            return abs(_cross(edge, _sub(vertices[candidate], vertices[index])))

        while support((opposite + 1) % count) > support(opposite) + tolerance:
            opposite = (opposite + 1) % count
        update(index, opposite)
        update(next_index, opposite)
        next_opposite = (opposite + 1) % count
        if abs(support(next_opposite) - support(opposite)) <= tolerance:
            update(index, next_opposite)
            update(next_index, next_opposite)

    return math.sqrt(best_sq), best_pair


def coverage_by_dot_product(
    vertices: Sequence[Point],
    diameter_pair: tuple[Point, Point],
    tolerance: float = 1e-10,
) -> tuple[bool, float, Point | None]:
    first, second = diameter_pair
    diameter_sq = _distance_sq(first, second)
    threshold = tolerance * max(1.0, diameter_sq)
    values = [(_dot(_sub(vertex, first), _sub(vertex, second)), vertex) for vertex in vertices]
    maximum, witness = max(values, default=(0.0, None), key=lambda item: item[0])
    return maximum <= threshold, max(0.0, maximum), witness if maximum > threshold else None


def coverage_by_center_distance(
    vertices: Sequence[Point],
    diameter_pair: tuple[Point, Point],
    tolerance: float = 1e-10,
) -> bool:
    first, second = diameter_pair
    center = _mul(_add(first, second), 0.5)
    radius_sq = 0.25 * _distance_sq(first, second)
    threshold = tolerance * max(1.0, radius_sq)
    return all(_distance_sq(vertex, center) <= radius_sq + threshold for vertex in vertices)


def _vertex_sets_agree(first: Sequence[Point], second: Sequence[Point], tolerance: float) -> bool:
    if len(first) != len(second):
        return False
    limit_sq = (100.0 * tolerance) ** 2
    return all(min(_distance_sq(point, other) for other in second) <= limit_sq for point in first)


def _normalization(lines: Sequence[HalfPlane]) -> tuple[Point, float]:
    if not lines:
        return (0.0, 0.0), 1.0
    center = (
        sum(line.q[0] for line in lines) / len(lines),
        sum(line.q[1] for line in lines) / len(lines),
    )
    scale = max((math.hypot(*_sub(line.q, center)) for line in lines), default=1.0)
    return center, max(scale, 1.0)


def solve_halfplanes(
    halfplanes: Sequence[HalfPlane],
    *,
    tolerance: float = 1e-10,
    verify: bool = True,
) -> Q1Result:
    if not math.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("tolerance 必须是正有限数")
    lines = [make_halfplane(line.q, line.d, line.source) for line in halfplanes]
    if not lines:
        return Q1Result(RegionStatus.UNBOUNDED, diagnostics={"constraint_count": 0})

    center, scale = _normalization(lines)
    normalized = [
        make_halfplane(_mul(_sub(line.q, center), 1.0 / scale), line.d, line.source)
        for line in lines
    ]
    diagnostics: dict[str, Any] = {
        "constraint_count": len(lines),
        "normalization_center": list(center),
        "normalization_scale": scale,
        "tolerance": tolerance,
        "formal_vertex_algorithm": "angle-sorted deque half-plane intersection",
        "reference_vertex_algorithm": "pairwise boundary intersections with full screening",
    }
    main_vertices = halfplane_intersection_main(normalized, tolerance)
    diagnostics["main_vertex_count"] = len(main_vertices)
    diagnostics["normalized_area"] = polygon_area(main_vertices)
    main_is_2d = len(main_vertices) >= 3 and polygon_area(main_vertices) > 100.0 * tolerance
    has_recession = _has_recession_direction(normalized, tolerance)

    # 正常有界输入始终走 O(n log n) 的正式路径；只有结果异常或未决时，
    # 才调用速度较慢的防御性分类器。
    if not main_is_2d or has_recession:
        feasible_point = _find_feasible_point(normalized, tolerance)
        if feasible_point is None:
            return Q1Result(RegionStatus.EMPTY, diagnostics=diagnostics)
        if has_recession:
            return Q1Result(RegionStatus.UNBOUNDED, diagnostics=diagnostics)
        reference_vertices = halfplane_intersection_reference(normalized, tolerance)
        diagnostics["reference_vertex_count"] = len(reference_vertices)
        diagnostics["reference_normalized_area"] = polygon_area(reference_vertices)
        if len(reference_vertices) < 3 or polygon_area(reference_vertices) <= 100.0 * tolerance:
            return Q1Result(RegionStatus.DEGENERATE, diagnostics=diagnostics)
        return Q1Result(RegionStatus.NUMERICALLY_UNCERTAIN, diagnostics=diagnostics)

    reference_vertices: list[Point] | None = None
    if verify:
        reference_vertices = halfplane_intersection_reference(normalized, tolerance)
        vertex_agreement = _vertex_sets_agree(main_vertices, reference_vertices, tolerance)
        diagnostics["main_reference_vertex_agreement"] = vertex_agreement
        diagnostics["reference_vertex_count"] = len(reference_vertices)
        diagnostics["reference_normalized_area"] = polygon_area(reference_vertices)
        if not vertex_agreement:
            return Q1Result(RegionStatus.NUMERICALLY_UNCERTAIN, diagnostics=diagnostics)
    else:
        diagnostics["reference_checks_run"] = False

    diameter, pair = diameter_rotating_calipers(main_vertices, tolerance)
    if verify:
        assert reference_vertices is not None
        reference_diameter, _ = diameter_bruteforce(reference_vertices)
        diameter_agreement = math.isclose(
            diameter,
            reference_diameter,
            rel_tol=100.0 * tolerance,
            abs_tol=100.0 * tolerance,
        )
        diagnostics["calipers_bruteforce_diameter_agreement"] = diameter_agreement
        diagnostics["normalized_reference_diameter"] = reference_diameter
        if not diameter_agreement:
            return Q1Result(RegionStatus.NUMERICALLY_UNCERTAIN, diagnostics=diagnostics)

    covered, violation, violating_vertex = coverage_by_dot_product(
        main_vertices, pair, tolerance
    )
    if verify:
        reference_covered = coverage_by_center_distance(main_vertices, pair, tolerance)
        diagnostics["coverage_formula_agreement"] = covered == reference_covered
        if covered != reference_covered:
            return Q1Result(RegionStatus.NUMERICALLY_UNCERTAIN, diagnostics=diagnostics)

    def restore(point: Point) -> Point:
        return _add(center, _mul(point, scale))

    restored_vertices = tuple(restore(point) for point in main_vertices)
    restored_pair = (restore(pair[0]), restore(pair[1]))
    restored_center = _mul(_add(restored_pair[0], restored_pair[1]), 0.5)
    restored_witness = restore(violating_vertex) if violating_vertex is not None else None
    return Q1Result(
        status=RegionStatus.VALID,
        vertices=restored_vertices,
        diameter=diameter * scale,
        diameter_pair=restored_pair,
        circle_center=restored_center,
        covered=covered,
        max_violation=violation * scale * scale,
        violating_vertex=restored_witness,
        diagnostics=diagnostics,
    )


def solve_observations(
    observations: Sequence[tuple[float, float, float]],
    *,
    error_deg: float = 1.0,
    tolerance: float = 1e-10,
    verify: bool = True,
) -> Q1Result:
    return solve_halfplanes(
        bearing_halfplanes(observations, error_deg),
        tolerance=tolerance,
        verify=verify,
    )


__all__ = [
    "HalfPlane",
    "Point",
    "Q1Result",
    "RegionStatus",
    "bearing_halfplanes",
    "contains",
    "coverage_by_center_distance",
    "coverage_by_dot_product",
    "diameter_bruteforce",
    "diameter_rotating_calipers",
    "halfplane_intersection_main",
    "halfplane_intersection_reference",
    "make_halfplane",
    "polygon_area",
    "side",
    "solve_halfplanes",
    "solve_observations",
]
