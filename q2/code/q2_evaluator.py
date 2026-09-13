"""Q2 低分辨率评价器与离散 Pareto 分析。

本模块有意只产生点估计；它是 METHOD.md 所述的诊断原型，
并非后续经过区间认证的求解器。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Sequence

from q2_curve import StepCurve, curve_dominates, empirical_step_curve, lower_envelope
from q2_geometry import AngleQualityTable, Branch, Point, bearing_deg, classify_branch, distance
from q2_measures import branch_areas
from q2_state import FirstObservation, Q2Config, SourceCell, StateDomain


@dataclass(frozen=True)
class RadiusEvaluation:
    receive_radius_m: float
    active_area_m2: float
    near_share: float
    direction_share: float
    no_signal_share: float
    effective_coverage: float
    curve: tuple[float, ...] | None
    step_curve: StepCurve | None
    finite_direction_share: float | None

    def to_dict(self, thresholds_m: Sequence[float]) -> dict[str, object]:
        result = asdict(self)
        result.pop("curve")
        result["curve"] = (
            None
            if self.curve is None
            else {str(float(t)): value for t, value in zip(thresholds_m, self.curve)}
        )
        result.pop("step_curve")
        result["step_curve"] = None if self.step_curve is None else self.step_curve.to_dict()
        return result


@dataclass(frozen=True)
class CandidateEvaluation:
    point: Point
    movement_m: float
    gamma_point_estimate_m: float
    sampled_safe: bool
    evaluable: bool
    sampled_near_only: bool
    robust_effective_coverage: float
    robust_near_share: float
    robust_curve: tuple[float, ...] | None
    robust_step_curve: StepCurve | None
    robust_platform: float | None
    sampled_tail_diameter_m: float | None
    radius_evaluations: tuple[RadiusEvaluation, ...]
    angle_table_status_counts: dict[str, int]

    def to_dict(self, thresholds_m: Sequence[float], *, include_radii: bool = False) -> dict[str, object]:
        result: dict[str, object] = {
            "point": list(self.point),
            "movement_m": self.movement_m,
            "gamma_point_estimate_m": self.gamma_point_estimate_m,
            "sampled_safe": self.sampled_safe,
            "safety_evidence": "PROTOTYPE_POINT_ESTIMATE_NOT_CERTIFIED",
            "evaluable": self.evaluable,
            "sampled_near_only": self.sampled_near_only,
            "robust_effective_coverage": self.robust_effective_coverage,
            "robust_near_share": self.robust_near_share,
            "robust_curve": (
                None
                if self.robust_curve is None
                else {str(float(t)): value for t, value in zip(thresholds_m, self.robust_curve)}
            ),
            "robust_step_curve": (
                None if self.robust_step_curve is None else self.robust_step_curve.to_dict()
            ),
            "robust_platform": self.robust_platform,
            "sampled_tail_diameter_m": self.sampled_tail_diameter_m,
            "angle_table_status_counts": self.angle_table_status_counts,
        }
        if include_radii:
            result["radius_evaluations"] = [
                item.to_dict(thresholds_m) for item in self.radius_evaluations
            ]
        return result


@dataclass(frozen=True)
class _PreparedSource:
    cell: SourceCell
    distance_to_candidate: float
    worst_angle_diameter_m: float


def evaluate_candidate(
    candidate: Point,
    first: FirstObservation,
    config: Q2Config,
    domain: StateDomain,
    radii_m: Sequence[float],
    thresholds_m: Sequence[float],
    *,
    angle_step_deg: float = 2.0,
    tolerance: float = 1e-9,
) -> CandidateEvaluation:
    """使用离散的源位置、接收半径和角度状态评价一个候选点。"""

    if not domain.samples:
        raise ValueError("需要一个正面积状态域")
    if not radii_m:
        raise ValueError("至少需要一个与面积状态相容的接收半径")
    if not thresholds_m or any(not math.isfinite(t) or t < 0.0 for t in thresholds_m):
        raise ValueError("阈值必须构成非空的非负序列")
    if tuple(thresholds_m) != tuple(sorted(thresholds_m)):
        raise ValueError("阈值必须按升序排列")

    table = AngleQualityTable.build(
        first.point,
        first.bearing_deg,
        candidate,
        error_deg=config.error_deg,
        requested_step_deg=angle_step_deg,
    )
    prepared: list[_PreparedSource] = []
    for cell in domain.samples:
        separation = distance(candidate, cell.point)
        if separation <= config.near_radius + tolerance:
            worst = 0.0
        else:
            true_bearing = bearing_deg(candidate, cell.point)
            worst = table.worst_for_true_bearing(true_bearing, config.error_deg)
        prepared.append(_PreparedSource(cell, separation, worst))

    radius_results: list[RadiusEvaluation] = []
    empirical_curves: list[StepCurve] = []
    for receive_radius in radii_m:
        active = [item for item in prepared if item.cell.distance_from_first <= receive_radius + tolerance]
        areas = branch_areas(candidate, first, config, receive_radius)
        if areas.active_area_m2 <= 0.0:
            continue
        direction_states = [
            item for item in active
            if classify_branch(
                item.cell.point, candidate, receive_radius, config.near_radius,
                tolerance=tolerance,
            ) is Branch.DIRECTION
        ]
        step_curve = empirical_step_curve(
            [item.worst_angle_diameter_m for item in direction_states],
            [item.cell.weight_m2 for item in direction_states],
        )
        curve = (
            None
            if step_curve is None
            else tuple(step_curve.at(value) for value in thresholds_m)
        )
        finite_share = None if step_curve is None else step_curve.platform
        if step_curve is not None:
            empirical_curves.append(step_curve)
        radius_results.append(
            RadiusEvaluation(
                receive_radius,
                areas.active_area_m2,
                areas.near_area_m2 / areas.active_area_m2,
                areas.direction_area_m2 / areas.active_area_m2,
                areas.no_signal_area_m2 / areas.active_area_m2,
                areas.effective_area_m2 / areas.active_area_m2,
                curve,
                step_curve,
                finite_share,
            )
        )

    if not radius_results:
        raise ValueError("接收半径栅格中没有离散到正面积状态")
    robust_step_curve = lower_envelope(empirical_curves)
    robust_curve = (
        None
        if robust_step_curve is None
        else tuple(robust_step_curve.at(value) for value in thresholds_m)
    )
    platform = None if robust_step_curve is None else robust_step_curve.platform
    tail: float | None = None
    if platform is not None and platform <= tolerance:
        tail = 0.0
    elif robust_step_curve is not None:
        tail = next(
            (
                threshold
                for threshold, value in zip(
                    robust_step_curve.breakpoints_m, robust_step_curve.attainment
                )
                if value >= platform - 1e-12
            ),
            None,
        )

    gamma_points = [cell.point for cell in domain.samples]
    gamma_points.extend(domain.support_points)
    gamma = max(
        distance(source, candidate)
        - max(config.receive_min, distance(source, first.point))
        for source in gamma_points
    )
    has_direction = robust_step_curve is not None
    all_near = all(item.near_share >= 1.0 - tolerance for item in radius_results)
    return CandidateEvaluation(
        candidate,
        distance(first.point, candidate),
        gamma,
        gamma <= tolerance,
        has_direction,
        all_near,
        min(item.effective_coverage for item in radius_results),
        min(item.near_share for item in radius_results),
        robust_curve,
        robust_step_curve,
        platform,
        tail,
        tuple(radius_results),
        table.status_counts(),
    )


def dominates(
    first: CandidateEvaluation,
    second: CandidateEvaluation,
    *,
    safety_front: bool = False,
    tolerance: float = 1e-10,
) -> bool:
    """按 C、G、H 判断点估计支配关系；安全前沿内仅使用 C 和 H。"""

    if first.robust_step_curve is None or second.robust_step_curve is None:
        return False
    curve_weakly_better, curve_strictly_better = curve_dominates(
        first.robust_step_curve, second.robust_step_curve, tolerance=tolerance
    )
    if not curve_weakly_better:
        return False
    first_values: list[float] = []
    second_values: list[float] = []
    if not safety_front:
        first_values.append(first.robust_effective_coverage)
        second_values.append(second.robust_effective_coverage)
    first_values.append(first.robust_near_share)
    second_values.append(second.robust_near_share)
    weakly_better = all(a >= b - tolerance for a, b in zip(first_values, second_values))
    strictly_better = curve_strictly_better or any(
        a > b + tolerance for a, b in zip(first_values, second_values)
    )
    return weakly_better and strictly_better


def nondominated(
    candidates: Sequence[CandidateEvaluation],
    *,
    safety_front: bool = False,
) -> tuple[CandidateEvaluation, ...]:
    eligible = [candidate for candidate in candidates if candidate.evaluable]
    return tuple(
        candidate
        for candidate in eligible
        if not any(
            other is not candidate and dominates(other, candidate, safety_front=safety_front)
            for other in eligible
        )
    )


def representative_indices(
    candidates: Sequence[CandidateEvaluation],
) -> dict[str, int | None]:
    if not candidates:
        return {"coverage": None, "near": None, "tail": None}
    coverage = max(
        range(len(candidates)),
        key=lambda i: (candidates[i].robust_effective_coverage,
                       candidates[i].robust_near_share, -candidates[i].movement_m),
    )
    near = max(
        range(len(candidates)),
        key=lambda i: (candidates[i].robust_near_share,
                       candidates[i].robust_effective_coverage, -candidates[i].movement_m),
    )
    tail = max(
        range(len(candidates)),
        key=lambda i: (
            candidates[i].robust_platform if candidates[i].robust_platform is not None else -1.0,
            -(candidates[i].sampled_tail_diameter_m
              if candidates[i].sampled_tail_diameter_m is not None else math.inf),
            candidates[i].robust_effective_coverage,
            -candidates[i].movement_m,
        ),
    )
    return {"coverage": coverage, "near": near, "tail": tail}


__all__ = [
    "CandidateEvaluation",
    "RadiusEvaluation",
    "dominates",
    "evaluate_candidate",
    "nondominated",
    "representative_indices",
]
