"""Q2 快速选点器：保守接收约束与极小化最坏定位误差。"""
from __future__ import annotations

from dataclasses import dataclass, replace
import math
from time import perf_counter
from typing import Sequence

from q2_geometry import Point, bearing_deg, distance, normalize_angle_deg
from q2_state import FirstObservation, Q2Config, StateDomain, build_state_domain
from q1_geometry import (
    HalfPlane,
    RegionStatus,
    bearing_halfplanes,
    diameter_rotating_calipers,
    make_halfplane,
    solve_halfplanes,
)


@dataclass(frozen=True)
class FastOptions:
    circle_sides: int = 48
    state_angle_cells: int = 33
    state_radial_cells: int = 24
    coarse_source_count: int = 24
    final_source_count: int = 64
    coarse_error_nodes: int = 3
    final_error_nodes: int = 7
    seed_count: int = 3
    local_rounds: int = 4
    local_initial_step_m: float | None = None
    recommendation_count: int = 3
    tolerance: float = 1e-9


@dataclass(frozen=True)
class EnclosingCircle:
    center: Point
    radius: float


@dataclass(frozen=True)
class CandidateScore:
    point: Point
    stage: str
    movement_m: float
    conservative_safety_margin_m: float
    worst_posterior_diameter_m: float
    worst_source: Point | None
    worst_error_deg: float | None
    worst_observed_bearing_deg: float | None
    worst_posterior_vertex_count: int
    evaluated_direction_cases: int
    evaluated_near_cases: int

    def to_dict(self) -> dict[str, object]:
        return {
            "point_m": list(self.point),
            "stage": self.stage,
            "movement_m": self.movement_m,
            "conservative_safety_margin_m": self.conservative_safety_margin_m,
            "worst_posterior_diameter_m": self.worst_posterior_diameter_m,
            "worst_source_m": list(self.worst_source) if self.worst_source else None,
            "worst_error_deg": self.worst_error_deg,
            "worst_observed_bearing_deg": self.worst_observed_bearing_deg,
            "worst_posterior_vertex_count": self.worst_posterior_vertex_count,
            "evaluated_direction_cases": self.evaluated_direction_cases,
            "evaluated_near_cases": self.evaluated_near_cases,
        }


def _disk_outer_halfplanes(
    center: Point, radius: float, sides: int, source: str
) -> list[HalfPlane]:
    if sides < 8:
        raise ValueError("circle_sides 必须至少为 8")
    result: list[HalfPlane] = []
    for index in range(sides):
        angle = 2.0 * math.pi * index / sides
        ux, uy = math.cos(angle), math.sin(angle)
        q = (center[0] + radius * ux, center[1] + radius * uy)
        result.append(make_halfplane(q, (-uy, ux), f"{source}_{index}"))
    return result


def build_position_outer_polygon(
    first: FirstObservation, config: Q2Config, circle_sides: int = 48
) -> list[Point]:
    """构造与第一次观测相容的全部源位置的凸外包。"""
    constraints = bearing_halfplanes(
        [(first.point[0], first.point[1], first.bearing_deg)],
        error_deg=config.error_deg,
    )
    constraints.extend(
        _disk_outer_halfplanes(config.center, config.target_radius, circle_sides, "target")
    )
    constraints.extend(
        _disk_outer_halfplanes(first.point, config.receive_max, circle_sides, "range")
    )
    answer = solve_halfplanes(constraints, tolerance=1e-10, verify=False)
    if answer.status is not RegionStatus.VALID or len(answer.vertices) < 3:
        raise ValueError("第一次观测没有对应的正常可行源区域")
    return [(float(x), float(y)) for x, y in answer.vertices]


def conservative_safety_margin(
    point: Point, outer_polygon: Sequence[Point], receive_min: float
) -> float:
    return receive_min - max(distance(point, vertex) for vertex in outer_polygon)


def _pair_circle(first: Point, second: Point) -> EnclosingCircle:
    center = ((first[0] + second[0]) / 2.0, (first[1] + second[1]) / 2.0)
    return EnclosingCircle(center, distance(first, second) / 2.0)


def _triple_circle(a: Point, b: Point, c: Point) -> EnclosingCircle | None:
    denominator = 2.0 * (
        a[0] * (b[1] - c[1])
        + b[0] * (c[1] - a[1])
        + c[0] * (a[1] - b[1])
    )
    if abs(denominator) <= 1e-12:
        return None
    aa = a[0] * a[0] + a[1] * a[1]
    bb = b[0] * b[0] + b[1] * b[1]
    cc = c[0] * c[0] + c[1] * c[1]
    center = (
        (aa * (b[1] - c[1]) + bb * (c[1] - a[1]) + cc * (a[1] - b[1]))
        / denominator,
        (aa * (c[0] - b[0]) + bb * (a[0] - c[0]) + cc * (b[0] - a[0]))
        / denominator,
    )
    return EnclosingCircle(center, distance(center, a))


def minimum_enclosing_circle(points: Sequence[Point]) -> EnclosingCircle:
    if not points:
        raise ValueError("计算最小包围圆至少需要一个点")
    candidates = [EnclosingCircle(point, 0.0) for point in points]
    for i, first in enumerate(points):
        for second in points[i + 1 :]:
            candidates.append(_pair_circle(first, second))
    for i, first in enumerate(points):
        for j in range(i + 1, len(points)):
            for k in range(j + 1, len(points)):
                circle = _triple_circle(first, points[j], points[k])
                if circle is not None:
                    candidates.append(circle)
    feasible = [
        circle
        for circle in candidates
        if all(distance(circle.center, point) <= circle.radius + 1e-7 for point in points)
    ]
    if not feasible:
        raise RuntimeError("最小包围圆构造失败")
    return min(feasible, key=lambda item: item.radius)


def _ray_safe_extent(
    origin: Point, direction: Point, polygon: Sequence[Point], radius: float
) -> float:
    upper = math.inf
    for vertex in polygon:
        wx, wy = origin[0] - vertex[0], origin[1] - vertex[1]
        projection = wx * direction[0] + wy * direction[1]
        discriminant = projection * projection - (wx * wx + wy * wy - radius * radius)
        if discriminant < -1e-7:
            return 0.0
        upper = min(upper, -projection + math.sqrt(max(0.0, discriminant)))
    return max(0.0, upper)


def _deduplicate(points: Sequence[Point], tolerance: float = 1e-6) -> list[Point]:
    result: list[Point] = []
    for point in points:
        if all(distance(point, other) > tolerance for other in result):
            result.append(point)
    return result


def generate_sparse_candidates(
    first: FirstObservation,
    config: Q2Config,
    polygon: Sequence[Point],
    *,
    tolerance: float = 1e-9,
) -> tuple[list[Point], EnclosingCircle]:
    """沿十二个几何对齐方向生成中心点及两层径向候选点。"""
    circle = minimum_enclosing_circle(polygon)
    if circle.radius > config.receive_min + tolerance:
        return [], circle
    axis = math.radians(normalize_angle_deg(first.bearing_deg))
    directions = [
        (math.cos(axis + index * math.pi / 6.0), math.sin(axis + index * math.pi / 6.0))
        for index in range(12)
    ]
    raw = [circle.center]
    for direction in directions:
        extent = _ray_safe_extent(circle.center, direction, polygon, config.receive_min)
        for fraction in (0.55, 0.9):
            raw.append(
                (
                    circle.center[0] + fraction * extent * direction[0],
                    circle.center[1] + fraction * extent * direction[1],
                )
            )
    candidates = [
        point
        for point in _deduplicate(raw)
        if distance(point, first.point) > tolerance
        and conservative_safety_margin(point, polygon, config.receive_min) >= -1e-7
    ]
    return candidates, circle


def _representative_sources(domain: StateDomain, count: int) -> list[Point]:
    pool = _deduplicate(
        list(domain.support_points) + [cell.point for cell in domain.samples], 1e-8
    )
    if len(pool) <= count:
        return pool
    center = (
        sum(point[0] for point in pool) / len(pool),
        sum(point[1] for point in pool) / len(pool),
    )
    selected = [max(pool, key=lambda point: distance(point, center))]
    while len(selected) < count:
        selected.append(
            max(pool, key=lambda point: min(distance(point, chosen) for chosen in selected))
        )
    return _deduplicate(selected, 1e-8)[:count]


def _error_grid(error_deg: float, nodes: int) -> list[float]:
    if nodes <= 1 or error_deg == 0.0:
        return [0.0]
    return [-error_deg + 2.0 * error_deg * index / (nodes - 1) for index in range(nodes)]


def _side(line: HalfPlane, point: Point) -> float:
    return line.d[0] * (point[1] - line.q[1]) - line.d[1] * (point[0] - line.q[0])


def _clip_halfplane(
    polygon: Sequence[Point], line: HalfPlane, tolerance: float
) -> list[Point]:
    if not polygon:
        return []
    result: list[Point] = []
    previous = polygon[-1]
    previous_side = _side(line, previous)
    for current in polygon:
        current_side = _side(line, current)
        previous_in = previous_side >= -tolerance
        current_in = current_side >= -tolerance
        if previous_in != current_in:
            denominator = previous_side - current_side
            fraction = 0.5 if abs(denominator) <= tolerance else previous_side / denominator
            result.append(
                (
                    previous[0] + fraction * (current[0] - previous[0]),
                    previous[1] + fraction * (current[1] - previous[1]),
                )
            )
        if current_in:
            result.append(current)
        previous, previous_side = current, current_side
    return _deduplicate(result, 1e-8)


def posterior_polygon(
    prior_polygon: Sequence[Point],
    candidate: Point,
    observed_bearing_deg: float,
    error_deg: float,
    tolerance: float = 1e-9,
) -> list[Point]:
    result = list(prior_polygon)
    lines = bearing_halfplanes(
        [(candidate[0], candidate[1], observed_bearing_deg)], error_deg=error_deg
    )
    for line in lines:
        result = _clip_halfplane(result, line, tolerance)
    return result


def evaluate_candidate(
    candidate: Point,
    stage: str,
    first: FirstObservation,
    config: Q2Config,
    polygon: Sequence[Point],
    sources: Sequence[Point],
    errors: Sequence[float],
) -> CandidateScore:
    margin = conservative_safety_margin(candidate, polygon, config.receive_min)
    worst = -1.0
    witness_source: Point | None = None
    witness_error: float | None = None
    witness_bearing: float | None = None
    witness_vertices = 0
    direction_cases = 0
    near_cases = 0
    for source in sources:
        if distance(candidate, source) <= config.near_radius:
            near_cases += 1
            worst = max(worst, 0.0)
            continue
        true_bearing = bearing_deg(candidate, source)
        for error in errors:
            direction_cases += 1
            observed = normalize_angle_deg(true_bearing + error)
            posterior = posterior_polygon(
                polygon, candidate, observed, config.error_deg
            )
            if len(posterior) <= 1:
                diameter = 0.0
            else:
                diameter = diameter_rotating_calipers(posterior)[0]
            if diameter > worst:
                worst = diameter
                witness_source = source
                witness_error = error
                witness_bearing = observed
                witness_vertices = len(posterior)
    if worst < 0.0:
        worst = math.inf
    return CandidateScore(
        candidate,
        stage,
        distance(first.point, candidate),
        margin,
        worst,
        witness_source,
        witness_error,
        witness_bearing,
        witness_vertices,
        direction_cases,
        near_cases,
    )


def _score_key(score: CandidateScore) -> tuple[float, float, float]:
    return (
        score.worst_posterior_diameter_m,
        score.movement_m,
        -score.conservative_safety_margin_m,
    )


def _local_refine(
    seed: CandidateScore,
    first: FirstObservation,
    config: Q2Config,
    polygon: Sequence[Point],
    sources: Sequence[Point],
    errors: Sequence[float],
    step: float,
    rounds: int,
) -> tuple[CandidateScore, int]:
    best = seed
    evaluations = 0
    directions = [
        (math.cos(index * math.pi / 4.0), math.sin(index * math.pi / 4.0))
        for index in range(8)
    ]
    for _ in range(rounds):
        neighbors = [
            (best.point[0] + step * dx, best.point[1] + step * dy)
            for dx, dy in directions
        ]
        for point in neighbors:
            if conservative_safety_margin(point, polygon, config.receive_min) < -1e-7:
                continue
            score = evaluate_candidate(
                point, "local_refinement", first, config, polygon, sources, errors
            )
            evaluations += 1
            if _score_key(score) < _score_key(best):
                best = score
        step *= 0.5
    return best, evaluations


def solve_fast_q2(
    first: FirstObservation,
    config: Q2Config | None = None,
    options: FastOptions | None = None,
    safety_buffer_m: float = 0.0,
) -> dict[str, object]:
    """返回保守安全候选点及快速极小极大推荐结果。"""
    started = perf_counter()
    config = config or Q2Config()
    options = options or FastOptions()
    first.validate()
    config.validate()
    if not math.isfinite(safety_buffer_m) or safety_buffer_m < 0.0:
        raise ValueError("safety_buffer_m 必须是非负有限数")
    effective_receive_radius = config.receive_min - safety_buffer_m
    if effective_receive_radius <= config.near_radius:
        raise ValueError("设置安全缓冲后已没有可用的接收半径")
    safety_config = replace(config, receive_min=effective_receive_radius)
    safety_config.validate()
    polygon = build_position_outer_polygon(first, config, options.circle_sides)
    domain = build_state_domain(
        first,
        config,
        angle_cells=options.state_angle_cells,
        radial_cells=options.state_radial_cells,
        tolerance=options.tolerance,
    )
    candidates, circle = generate_sparse_candidates(
        first, safety_config, polygon, tolerance=options.tolerance
    )
    base: dict[str, object] = {
        "algorithm": "CONSERVATIVE_SPARSE_MINIMAX",
        "evidence_level": {
            "reception_safety": "conservative outer-polygon certificate",
            "localization_objective": "representative-state numerical minimax",
            "global_optimality": "not claimed",
        },
        "first_observation": {
            "point_m": list(first.point),
            "bearing_deg": normalize_angle_deg(first.bearing_deg),
        },
        "safe_region": {
            "outer_polygon_vertices_m": [list(point) for point in polygon],
            "outer_polygon_vertex_count": len(polygon),
            "minimum_enclosing_circle_center_m": list(circle.center),
            "minimum_enclosing_circle_radius_m": circle.radius,
            "minimum_receive_radius_m": config.receive_min,
            "safety_buffer_m": safety_buffer_m,
            "effective_safe_radius_m": effective_receive_radius,
            "nonempty_under_outer_approximation": bool(candidates),
        },
        "state_domain": {
            "status": domain.status.value,
            "source_sample_count": len(domain.samples),
            "support_point_count": len(domain.support_points),
            "approximate_area_m2": domain.approximate_area_m2,
        },
    }
    if not candidates:
        base.update(
            {
                "result_status": "NO_CONSERVATIVELY_SAFE_CANDIDATE",
                "recommendations": [],
                "elapsed_seconds": perf_counter() - started,
            }
        )
        return base

    coarse_sources = _representative_sources(domain, options.coarse_source_count)
    coarse_errors = _error_grid(config.error_deg, options.coarse_error_nodes)
    coarse_scores = [
        evaluate_candidate(
            point, "sparse_search", first, safety_config, polygon, coarse_sources, coarse_errors
        )
        for point in candidates
    ]
    coarse_scores.sort(key=_score_key)
    slack = max(0.0, effective_receive_radius - circle.radius)
    initial_step = options.local_initial_step_m or min(200.0, max(20.0, 0.45 * slack))
    refined: list[CandidateScore] = []
    local_evaluations = 0
    for seed in coarse_scores[: options.seed_count]:
        result, used = _local_refine(
            seed,
            first,
            safety_config,
            polygon,
            coarse_sources,
            coarse_errors,
            initial_step,
            options.local_rounds,
        )
        refined.append(result)
        local_evaluations += used

    finalist_points = _deduplicate(
        [score.point for score in coarse_scores[: max(6, options.seed_count)]]
        + [score.point for score in refined]
    )
    final_sources = _representative_sources(domain, options.final_source_count)
    final_errors = _error_grid(config.error_deg, options.final_error_nodes)
    final_scores = [
        evaluate_candidate(
            point, "final_recheck", first, safety_config, polygon, final_sources, final_errors
        )
        for point in finalist_points
    ]
    final_scores.sort(key=_score_key)
    recommendations = final_scores[: options.recommendation_count]
    base.update(
        {
            "result_status": "FAST_NUMERICAL_SOLUTION",
            "search": {
                "sparse_candidate_count": len(candidates),
                "coarse_source_count": len(coarse_sources),
                "coarse_error_nodes": len(coarse_errors),
                "local_seed_count": min(options.seed_count, len(coarse_scores)),
                "local_rounds": options.local_rounds,
                "local_initial_step_m": initial_step,
                "local_candidate_evaluations": local_evaluations,
                "finalist_count": len(finalist_points),
                "final_source_count": len(final_sources),
                "final_error_nodes": len(final_errors),
            },
            "best_sparse_candidate": coarse_scores[0].to_dict(),
            "recommendations": [score.to_dict() for score in recommendations],
            "elapsed_seconds": perf_counter() - started,
        }
    )
    return base


__all__ = [
    "CandidateScore",
    "EnclosingCircle",
    "FastOptions",
    "build_position_outer_polygon",
    "conservative_safety_margin",
    "evaluate_candidate",
    "generate_sparse_candidates",
    "minimum_enclosing_circle",
    "posterior_polygon",
    "solve_fast_q2",
]
