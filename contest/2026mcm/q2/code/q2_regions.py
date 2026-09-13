"""Q2 栅格区域构造与多分辨率前沿诊断。

输出是有限方形单元的并集，而不是零面积散点云。
在缺少候选空间性能界时，它仍只是数值前沿带，
因此不称为经过认证的连续 Pareto 区域。
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping, Sequence

from q2_geometry import Point
from q2_curve import StepCurve
from q2_state import FirstObservation, Q2Config
from run_q2_prototype import DEFAULT_THRESHOLDS_M, run_prototype


GridIndex = tuple[int, int]


@dataclass(frozen=True)
class ResolutionLevel:
    candidate_step_m: float
    angle_cells: int
    radial_cells: int
    radius_count: int
    angle_step_deg: float

    def validate(self) -> None:
        if not math.isfinite(self.candidate_step_m) or self.candidate_step_m <= 0.0:
            raise ValueError("候选点步长必须是正有限数")
        if min(self.angle_cells, self.radial_cells) <= 0 or self.radius_count < 2:
            raise ValueError("状态或接收半径分辨率无效")
        if not math.isfinite(self.angle_step_deg) or self.angle_step_deg <= 0.0:
            raise ValueError("角度步长必须是正有限数")

    def to_dict(self) -> dict[str, float | int]:
        return {
            "candidate_step_m": self.candidate_step_m,
            "angle_cells": self.angle_cells,
            "radial_cells": self.radial_cells,
            "radius_count": self.radius_count,
            "angle_step_deg": self.angle_step_deg,
        }


def _grid_index(point: Point, step_m: float) -> GridIndex:
    scaled_x = point[0] / step_m
    scaled_y = point[1] / step_m
    index = (round(scaled_x), round(scaled_y))
    if not (
        math.isclose(scaled_x, index[0], abs_tol=1e-7)
        and math.isclose(scaled_y, index[1], abs_tol=1e-7)
    ):
        raise ValueError("候选点未与声明的栅格对齐")
    return index


def _point(index: GridIndex, step_m: float) -> Point:
    return (index[0] * step_m, index[1] * step_m)


def expanded_front_cells(
    front_points: Sequence[Point],
    allowed_points: Sequence[Point],
    step_m: float,
    *,
    buffer_cells: int = 1,
) -> set[GridIndex]:
    """按栅格单元缓冲扩展前沿中心，并裁剪至允许的中心集合。"""

    if buffer_cells < 0:
        raise ValueError("buffer_cells 必须非负")
    allowed = {_grid_index(point, step_m) for point in allowed_points}
    retained: set[GridIndex] = set()
    for point in front_points:
        center = _grid_index(point, step_m)
        for dx in range(-buffer_cells, buffer_cells + 1):
            for dy in range(-buffer_cells, buffer_cells + 1):
                neighbor = (center[0] + dx, center[1] + dy)
                if neighbor in allowed:
                    retained.add(neighbor)
    return retained


def _components(cells: set[GridIndex]) -> list[set[GridIndex]]:
    remaining = set(cells)
    groups: list[set[GridIndex]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        group = {seed}
        stack = [seed]
        while stack:
            x, y = stack.pop()
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    group.add(neighbor)
                    stack.append(neighbor)
        groups.append(group)
    return groups


def _boundary_segments(cells: set[GridIndex], step_m: float) -> list[list[list[float]]]:
    """返回方形单元并集中未被抵消的边。"""

    edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    for x, y in cells:
        lower_left = (2 * x - 1, 2 * y - 1)
        lower_right = (2 * x + 1, 2 * y - 1)
        upper_right = (2 * x + 1, 2 * y + 1)
        upper_left = (2 * x - 1, 2 * y + 1)
        for first, second in (
            (lower_left, lower_right),
            (lower_right, upper_right),
            (upper_right, upper_left),
            (upper_left, lower_left),
        ):
            reverse = (second, first)
            if reverse in edges:
                edges.remove(reverse)
            else:
                edges.add((first, second))
    scale = 0.5 * step_m
    return [
        [[first[0] * scale, first[1] * scale],
         [second[0] * scale, second[1] * scale]]
        for first, second in sorted(edges)
    ]


def raster_region(
    cells: Iterable[GridIndex],
    step_m: float,
    *,
    buffer_cells: int,
    label: str,
) -> dict[str, object]:
    """序列化等大方形栅格单元组成的非零面积并集。"""

    cell_set = set(cells)
    components = []
    for group in _components(cell_set):
        centers = [_point(index, step_m) for index in sorted(group)]
        xs = [value[0] for value in centers]
        ys = [value[1] for value in centers]
        half = 0.5 * step_m
        components.append({
            "cell_count": len(group),
            "area_m2": len(group) * step_m * step_m,
            "bounds_m": [min(xs) - half, min(ys) - half,
                         max(xs) + half, max(ys) + half],
            "cell_centers": [list(value) for value in centers],
            "boundary_segments": _boundary_segments(group, step_m),
        })
    all_centers = [_point(index, step_m) for index in sorted(cell_set)]
    if all_centers:
        half = 0.5 * step_m
        bounds: list[float] | None = [
            min(value[0] for value in all_centers) - half,
            min(value[1] for value in all_centers) - half,
            max(value[0] for value in all_centers) + half,
            max(value[1] for value in all_centers) + half,
        ]
    else:
        bounds = None
    return {
        "label": label,
        "geometry_type": "UNION_OF_AXIS_ALIGNED_SQUARE_CELLS",
        "candidate_step_m": step_m,
        "cell_half_width_m": 0.5 * step_m,
        "front_buffer_cells": buffer_cells,
        "retained_cell_count": len(cell_set),
        "component_count": len(components),
        "area_m2": len(cell_set) * step_m * step_m,
        "bounds_m": bounds,
        "components": components,
        "evidence": "NUMERICAL_FRONT_BAND_NOT_CELLWISE_CERTIFIED",
    }


def hausdorff_distance(first: Sequence[Point], second: Sequence[Point]) -> float | None:
    if not first or not second:
        return None

    def directed(left: Sequence[Point], right: Sequence[Point]) -> float:
        return max(
            min(math.hypot(a[0] - b[0], a[1] - b[1]) for b in right)
            for a in left
        )

    return max(directed(first, second), directed(second, first))


def _points(records: Sequence[Mapping[str, object]]) -> list[Point]:
    return [tuple(record["point"]) for record in records]  # type: ignore[arg-type,return-value]


def _level_summary(level: ResolutionLevel, result: Mapping[str, object]) -> dict[str, object]:
    return {
        "resolution": level.to_dict(),
        "result_status": result["result_status"],
        "counts": result["counts"],
        "elapsed_seconds": result["elapsed_seconds"],
        "global_front_points": [record["point"] for record in result["global_front"]],
        "certified_safe_internal_front_points": [
            record["point"] for record in result["certified_safe_internal_front"]
        ],
        "global_front_certified_safe_points": [
            record["point"] for record in result["global_front_certified_safe_intersection"]
        ],
    }


def _curve_from_record(record: Mapping[str, object]) -> StepCurve | None:
    value = record.get("robust_step_curve")
    if value is None:
        return None
    return StepCurve(
        tuple(value["breakpoints_m"]), tuple(value["attainment"]), value["platform"]
    )


def _common_point_changes(
    coarse: Mapping[str, object], fine: Mapping[str, object]
) -> dict[str, object]:
    coarse_map = {tuple(row["point"]): row for row in coarse["all_candidates"]}
    fine_map = {tuple(row["point"]): row for row in fine["all_candidates"]}
    common = sorted(set(coarse_map) & set(fine_map))
    max_g = max_h = max_curve = 0.0
    safety_changes = 0
    curve_pairs = 0
    for point in common:
        left, right = coarse_map[point], fine_map[point]
        max_g = max(max_g, abs(left["robust_effective_coverage"] - right["robust_effective_coverage"]))
        max_h = max(max_h, abs(left["robust_near_share"] - right["robust_near_share"]))
        if left["gamma_certificate"]["status"] != right["gamma_certificate"]["status"]:
            safety_changes += 1
        first, second = _curve_from_record(left), _curve_from_record(right)
        if first is not None and second is not None:
            curve_pairs += 1
            points = set(first.breakpoints_m) | set(second.breakpoints_m)
            max_curve = max(max_curve, abs(first.platform - second.platform))
            for threshold in points:
                max_curve = max(max_curve, abs(first.at(threshold) - second.at(threshold)))
    return {
        "common_candidate_count": len(common),
        "max_abs_G_change": max_g,
        "max_abs_H_change": max_h,
        "max_curve_vertical_change": max_curve,
        "compared_curve_count": curve_pairs,
        "gamma_status_change_count": safety_changes,
    }


def solve_numerical_regions(
    first: FirstObservation,
    config: Q2Config,
    levels: Sequence[ResolutionLevel],
    *,
    thresholds_m: Sequence[float] = DEFAULT_THRESHOLDS_M,
    max_candidates: int = 1600,
    front_buffer_cells: int = 1,
) -> dict[str, object]:
    """评价完整嵌套栅格，并返回最细层级的前沿带区域。"""

    if len(levels) < 2:
        raise ValueError("至少需要两个分辨率层级")
    for level in levels:
        level.validate()
    if any(
        finer.candidate_step_m >= coarser.candidate_step_m
        for coarser, finer in zip(levels, levels[1:])
    ):
        raise ValueError("候选点步长必须严格递减")
    for coarser, finer in zip(levels, levels[1:]):
        ratio = coarser.candidate_step_m / finer.candidate_step_m
        if not math.isclose(ratio, round(ratio), rel_tol=0.0, abs_tol=1e-9):
            raise ValueError("相邻候选点步长之间必须具有整数嵌套比例")

    results = [
        run_prototype(
            first,
            config,
            angle_cells=level.angle_cells,
            radial_cells=level.radial_cells,
            radius_count=level.radius_count,
            candidate_step_m=level.candidate_step_m,
            angle_step_deg=level.angle_step_deg,
            thresholds_m=thresholds_m,
            max_candidates=max_candidates,
            include_radius_details=False,
        )
        for level in levels
    ]
    if any(result["result_status"] != "PROTOTYPE_DIAGNOSTIC_ONLY" for result in results):
        return {
            "result_status": "REGION_UNDEFINED_FOR_NONREGULAR_INPUT",
            "levels": [_level_summary(level, result) for level, result in zip(levels, results)],
            "regions": {},
        }

    finest_level = levels[-1]
    finest = results[-1]
    all_records = finest["all_candidates"]
    evaluable_points = _points([record for record in all_records if record["evaluable"]])
    certified_safe_points = _points([
        record for record in all_records
        if record["evaluable"]
        and record["gamma_certificate"]["status"] == "CERTIFIED_SAFE"
    ])
    global_front_points = _points(finest["global_front"])
    safe_front_points = _points(finest["certified_safe_internal_front"])

    global_cells = expanded_front_cells(
        global_front_points,
        evaluable_points,
        finest_level.candidate_step_m,
        buffer_cells=front_buffer_cells,
    )
    safe_cells = expanded_front_cells(
        safe_front_points,
        certified_safe_points,
        finest_level.candidate_step_m,
        buffer_cells=front_buffer_cells,
    )
    intersection_cells = global_cells & safe_cells

    convergence = []
    for index in range(1, len(levels)):
        coarse = results[index - 1]
        fine = results[index]
        global_distance = hausdorff_distance(
            _points(coarse["global_front"]), _points(fine["global_front"])
        )
        safe_distance = hausdorff_distance(
            _points(coarse["certified_safe_internal_front"]),
            _points(fine["certified_safe_internal_front"]),
        )
        convergence.append({
            "from_step_m": levels[index - 1].candidate_step_m,
            "to_step_m": levels[index].candidate_step_m,
            "global_front_hausdorff_m": global_distance,
            "safe_front_hausdorff_m": safe_distance,
            "global_hausdorff_in_fine_cells": (
                None if global_distance is None
                else global_distance / levels[index].candidate_step_m
            ),
            "safe_hausdorff_in_fine_cells": (
                None if safe_distance is None
                else safe_distance / levels[index].candidate_step_m
            ),
            **_common_point_changes(coarse, fine),
        })

    recent = convergence[-2:]
    converged = len(recent) == 2 and all(
        row["global_hausdorff_in_fine_cells"] is not None
        and row["safe_hausdorff_in_fine_cells"] is not None
        and row["global_hausdorff_in_fine_cells"] <= 1.0
        and row["safe_hausdorff_in_fine_cells"] <= 1.0
        and row["max_abs_G_change"] <= 0.01
        and row["max_abs_H_change"] <= 0.01
        and row["max_curve_vertical_change"] <= 0.02
        and row["gamma_status_change_count"] == 0
        for row in recent
    )

    return {
        "result_status": "MULTIRESOLUTION_NUMERICAL_FRONT_BANDS",
        "evidence_level": {
            "candidate_space": "COMPLETE_GRID_AT_EACH_REPORTED_LEVEL",
            "regions": "FINEST_FRONT_CELLS_PLUS_ONE_CONFIGURABLE_CELL_BUFFER",
            "continuous_cell_dominance": "NOT_CERTIFIED",
            "formal_use": "REQUIRES_FURTHER_CONVERGENCE_AND_ENVELOPE_VALIDATION",
        },
        "levels": [_level_summary(level, result) for level, result in zip(levels, results)],
        "convergence": convergence,
        "convergence_assessment": {
            "converged": converged,
            "requires_two_successive_transitions": True,
            "criteria": {
                "front_hausdorff_fine_cells": 1.0,
                "max_abs_G_or_H_change": 0.01,
                "max_curve_vertical_change": 0.02,
                "gamma_status_changes": 0,
            },
            "scope": "nested candidate/source/radius/angle discretizations; continuous-R and interval curve certification remain separate",
        },
        "regions": {
            "global_front_band": raster_region(
                global_cells, finest_level.candidate_step_m,
                buffer_cells=front_buffer_cells, label="GLOBAL_FRONT_BAND",
            ),
            "certified_safe_internal_front_band": raster_region(
                safe_cells, finest_level.candidate_step_m,
                buffer_cells=front_buffer_cells, label="CERTIFIED_SAFE_INTERNAL_FRONT_BAND",
            ),
            "global_safe_band_intersection": raster_region(
                intersection_cells, finest_level.candidate_step_m,
                buffer_cells=front_buffer_cells, label="GLOBAL_SAFE_BAND_INTERSECTION",
            ),
        },
        "finest_front_records": {
            "global": finest["global_front"],
            "certified_safe_internal": finest["certified_safe_internal_front"],
            "global_certified_safe_intersection": finest[
                "global_front_certified_safe_intersection"
            ],
        },
        "interpretation": (
            "Each reported region is a nonzero-area union of evaluated square cells. "
            "The buffer represents candidate-grid resolution uncertainty; it does not "
            "prove that every point in a retained cell is Pareto-nondominated."
        ),
    }


__all__ = [
    "ResolutionLevel",
    "expanded_front_cells",
    "hausdorff_distance",
    "raster_region",
    "solve_numerical_regions",
]
