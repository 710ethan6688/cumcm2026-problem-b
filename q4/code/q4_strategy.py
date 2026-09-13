"""Guaranteed Q4 search built on the reusable Q3 localization and clear core."""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SHARED_CODE = _PROJECT_ROOT / "code"
_Q2_CODE = _PROJECT_ROOT / "q2" / "code"
_Q3_CODE = _PROJECT_ROOT / "q3" / "code"
for _code_dir in (_SHARED_CODE, _Q2_CODE, _Q3_CODE):
    if str(_code_dir) not in sys.path:
        sys.path.insert(0, str(_code_dir))

from q2_fast import (  # noqa: E402
    CandidateScore,
    conservative_safety_margin,
    evaluate_candidate,
    generate_sparse_candidates,
    minimum_enclosing_circle,
)
from q2_state import FirstObservation  # noqa: E402
from q4_clear_terminal import (  # noqa: E402
    CertifiedStripPlan,
    build_certified_strip_plan,
    estimate_full_clear_time_s,
)
from q3_strategy import (  # noqa: E402
    ChannelTrack,
    ChannelStatus,
    GuaranteedRollingQ3Strategy,
    Q3StrategyOptions,
    _channel_order,
    _distance,
    _error_grid,
    _point,
    _position,
    _representative_polygon_points,
    _score_key,
)
from radio_sim.domain.models import (  # noqa: E402
    ClearStatus,
    MeasureResult,
    MeasureStatus,
    StrategyResult,
)
from radio_sim.environment.base import Environment  # noqa: E402

Point = tuple[float, float]

DIRECTIONAL_INNER_RADIUS_M = 950.0
DIRECTIONAL_OUTER_RADIUS_M = 1870.0
DIRECTIONAL_RING_COUNT = 12


@dataclass(frozen=True)
class Q4StrategyOptions(Q3StrategyOptions):
    """Q4 options; inherited fields keep Q3/Q4 localization comparable."""

    max_active_measurements: int = 2
    mirrored_reacquisition: bool = True
    prioritized_clear_grid: bool = True
    task_insertion_scheduler: bool = False
    joint_direction_ranking: bool = False
    adaptive_tail_probe: bool = True
    adaptive_tail_min_visibility: float = 0.30
    direction_aware_grid_ordering: bool = False
    direction_heading_samples: int = 36
    analytic_clear_terminal: bool = False
    tail_terminal_linkage: bool = False

    def validate(self) -> None:
        super().validate()
        if self.direction_heading_samples < 8:
            raise ValueError("direction_heading_samples must be at least eight")
        if not 0.0 <= self.adaptive_tail_min_visibility <= 1.0:
            raise ValueError(
                "adaptive_tail_min_visibility must be in [0, 1]"
            )
        if self.tail_terminal_linkage and not self.analytic_clear_terminal:
            raise ValueError(
                "tail_terminal_linkage requires analytic_clear_terminal"
            )


def _polar_point(radius_m: float, angle_deg: float) -> Point:
    angle = math.radians(angle_deg)
    return (radius_m * math.cos(angle), radius_m * math.sin(angle))


def _reflect_across_bearing_axis(
    point: Point,
    origin: Point,
    bearing_deg: float,
) -> Point:
    """Reflect a probe across the latest successful bearing line."""
    angle = math.radians(bearing_deg)
    ux, uy = math.cos(angle), math.sin(angle)
    dx, dy = point[0] - origin[0], point[1] - origin[1]
    projection = dx * ux + dy * uy
    axial_x, axial_y = projection * ux, projection * uy
    return (
        origin[0] + 2.0 * axial_x - dx,
        origin[1] + 2.0 * axial_y - dy,
    )


def build_directionally_complete_search_points() -> tuple[Point, ...]:
    """Return center, twelve inner points, and twelve offset outer points."""
    inner = tuple(
        _polar_point(DIRECTIONAL_INNER_RADIUS_M, 30.0 * index)
        for index in range(DIRECTIONAL_RING_COUNT)
    )
    outer = tuple(
        _polar_point(DIRECTIONAL_OUTER_RADIUS_M, 30.0 * index + 15.0)
        for index in range(DIRECTIONAL_RING_COUNT)
    )
    return ((0.0, 0.0), *inner, *outer)


DIRECTIONAL_SEARCH_POINTS = build_directionally_complete_search_points()

# A shortest open tour found for the fixed 25-point certificate. The
# certificate itself is unchanged; this order only removes avoidable travel.
DIRECTIONAL_SEARCH_ROUTE_INDICES: tuple[int, ...] = (
    0, 9, 8, 7, 6, 5, 4, 3, 2, 1, 12, 11, 10,
    22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 24, 23,
)


def directional_search_route_length_m() -> float:
    """Return the origin-started length of the fixed certificate tour."""
    points = [
        DIRECTIONAL_SEARCH_POINTS[index]
        for index in DIRECTIONAL_SEARCH_ROUTE_INDICES
    ]
    return sum(
        _distance(first, second)
        for first, second in zip(((0.0, 0.0), *points[:-1]), points)
    )


def _source_before_search(
    current: Point,
    next_search: Point,
    source_centers: dict[int, Point],
) -> int | None:
    """Return a source only when source-then-search shortens both tasks."""
    if not source_centers:
        return None
    source_channel, source_first_cost = min(
        (
            channel,
            _distance(current, center) + _distance(center, next_search),
        )
        for channel, center in source_centers.items()
    )
    search_first_cost = _distance(current, next_search) + min(
        _distance(next_search, center) for center in source_centers.values()
    )
    if source_first_cost + 1e-9 < search_first_cost:
        return source_channel
    return None


def _directional_visibility_fraction(
    candidate: Point,
    sources: list[Point],
    visible_points: list[Point],
    blind_points: list[Point],
    heading_count: int,
    near_radius_m: float = 5.0,
) -> float | None:
    """Score visibility over feasible sampled position-heading states.

    This is a state-space fraction, not a probability. Blind points are only
    supplied after distance-safe probes, so their no-signal result identifies
    the directional half-plane rather than a range failure.
    """
    feasible = 0
    visible = 0
    for source in sources:
        for index in range(heading_count):
            angle = 2.0 * math.pi * index / heading_count
            ux, uy = math.cos(angle), math.sin(angle)

            def in_emission_halfplane(point: Point) -> bool:
                return (
                    ux * (point[0] - source[0])
                    + uy * (point[1] - source[1])
                    >= -1e-9
                )

            if any(not in_emission_halfplane(point) for point in visible_points):
                continue
            if any(in_emission_halfplane(point) for point in blind_points):
                continue
            feasible += 1
            if (
                _distance(candidate, source) <= near_radius_m
                or in_emission_halfplane(candidate)
            ):
                visible += 1
    if feasible == 0:
        return None
    return visible / feasible


def _compatible_heading_count(
    source: Point,
    visible_points: list[Point],
    blind_points: list[Point],
    heading_count: int,
) -> int:
    """Count sampled headings consistent with visible and blind probes."""
    compatible = 0
    for index in range(heading_count):
        angle = 2.0 * math.pi * index / heading_count
        ux, uy = math.cos(angle), math.sin(angle)

        def visible(point: Point) -> bool:
            return (
                ux * (point[0] - source[0])
                + uy * (point[1] - source[1])
                >= -1e-9
            )

        if all(visible(point) for point in visible_points) and all(
            not visible(point) for point in blind_points
        ):
            compatible += 1
    return compatible


def directional_search_triangles() -> tuple[tuple[Point, Point, Point], ...]:
    """Return the 36 triangles used by the finite discovery certificate."""
    center = DIRECTIONAL_SEARCH_POINTS[0]
    inner = DIRECTIONAL_SEARCH_POINTS[1:13]
    outer = DIRECTIONAL_SEARCH_POINTS[13:25]
    triangles: list[tuple[Point, Point, Point]] = []
    for index in range(DIRECTIONAL_RING_COUNT):
        next_index = (index + 1) % DIRECTIONAL_RING_COUNT
        previous_index = (index - 1) % DIRECTIONAL_RING_COUNT
        triangles.append((center, inner[index], inner[next_index]))
        triangles.append((inner[index], outer[previous_index], outer[index]))
        triangles.append((inner[index], inner[next_index], outer[index]))
    return tuple(triangles)


def directional_search_certificate() -> dict[str, float | int | bool]:
    """Compute the geometric quantities behind the Q4 discovery proof."""
    triangles = directional_search_triangles()
    maximum_edge = max(
        _distance(first, second)
        for triangle in triangles
        for first, second in (
            (triangle[0], triangle[1]),
            (triangle[1], triangle[2]),
            (triangle[2], triangle[0]),
        )
    )
    outer_inradius = DIRECTIONAL_OUTER_RADIUS_M * math.cos(math.pi / 12.0)
    return {
        "search_point_count": len(DIRECTIONAL_SEARCH_POINTS),
        "triangle_count": len(triangles),
        "maximum_triangle_edge_m": maximum_edge,
        "outer_polygon_inradius_m": outer_inradius,
        "strict_receive_margin_m": 1000.0 - maximum_edge,
        "covers_target_disk": outer_inradius >= 1800.0,
        "all_triangle_edges_below_receive_min": maximum_edge < 1000.0,
    }


class GuaranteedDirectionalQ4Strategy(GuaranteedRollingQ3Strategy):
    """Q4 baseline with complete directional discovery and finite clearing."""

    def __init__(self, options: Q4StrategyOptions | None = None) -> None:
        super().__init__(options or Q4StrategyOptions())
        self._search_completed_by_channel = {
            channel: set() for channel in range(1, 21)
        }
        self._mirrored_reacquisition_attempts = 0
        self._mirrored_reacquisition_hits = 0
        self._source_first_insertions = 0
        self._search_first_decisions = 0
        self._joint_direction_rankings = 0
        self._adaptive_tail_probe_attempts = 0
        self._adaptive_tail_probe_hits = 0
        self._direction_aware_grid_uses = 0
        self._analytic_plan_generated = 0
        self._analytic_plan_certified = 0
        self._analytic_plan_selected = 0
        self._analytic_plan_fallbacks = 0
        self._analytic_estimated_saving_s = 0.0
        self._tail_terminal_linkage_evaluations = 0
        self._tail_terminal_analytic_choices = 0
        self._tail_terminal_estimated_cost_reduction_s = 0.0
        self._last_candidate_score_by_channel: dict[int, CandidateScore] = {}
        self._visible_points_by_channel: dict[int, list[Point]] = {
            channel: [] for channel in range(1, 21)
        }
        self._blind_points_by_channel: dict[int, list[Point]] = {
            channel: [] for channel in range(1, 21)
        }

    def run(self, env: Environment) -> StrategyResult:
        """Run the shared lifecycle and append Q4 recovery diagnostics."""
        result = super().run(env)
        note = (
            f"{result.note};"
            f"mirrored_reacquisition_attempts={self._mirrored_reacquisition_attempts};"
            f"mirrored_reacquisition_hits={self._mirrored_reacquisition_hits};"
            f"source_first_insertions={self._source_first_insertions};"
            f"search_first_decisions={self._search_first_decisions};"
            f"joint_direction_rankings={self._joint_direction_rankings};"
            f"adaptive_tail_probe_attempts={self._adaptive_tail_probe_attempts};"
            f"adaptive_tail_probe_hits={self._adaptive_tail_probe_hits};"
            f"direction_aware_grid_uses={self._direction_aware_grid_uses};"
            f"analytic_plan_generated={self._analytic_plan_generated};"
            f"analytic_plan_certified={self._analytic_plan_certified};"
            f"analytic_plan_selected={self._analytic_plan_selected};"
            f"analytic_plan_fallbacks={self._analytic_plan_fallbacks};"
            f"analytic_estimated_saving_s={self._analytic_estimated_saving_s:.6f};"
            f"tail_terminal_linkage_evaluations="
            f"{self._tail_terminal_linkage_evaluations};"
            f"tail_terminal_analytic_choices="
            f"{self._tail_terminal_analytic_choices};"
            f"tail_terminal_estimated_cost_reduction_s="
            f"{self._tail_terminal_estimated_cost_reduction_s:.6f}"
        )
        return StrategyResult(
            strategy_name=result.strategy_name,
            completed=result.completed,
            note=note,
        )

    @property
    def analytic_terminal_diagnostics(self) -> dict[str, bool | int | float]:
        return {
            "analytic_clear_terminal_enabled": (
                self.options.analytic_clear_terminal
            ),
            "tail_terminal_linkage_enabled": self.options.tail_terminal_linkage,
            "analytic_plan_generated": self._analytic_plan_generated,
            "analytic_plan_certified": self._analytic_plan_certified,
            "analytic_plan_selected": self._analytic_plan_selected,
            "analytic_plan_fallbacks": self._analytic_plan_fallbacks,
            "analytic_estimated_saving_s": self._analytic_estimated_saving_s,
            "tail_terminal_linkage_evaluations": (
                self._tail_terminal_linkage_evaluations
            ),
            "tail_terminal_analytic_choices": (
                self._tail_terminal_analytic_choices
            ),
            "tail_terminal_estimated_cost_reduction_s": (
                self._tail_terminal_estimated_cost_reduction_s
            ),
        }

    @staticmethod
    def _append_distinct(points: list[Point], point: Point) -> None:
        if all(_distance(point, prior) > 1e-7 for prior in points):
            points.append(point)

    def _record_blind_probe(self, channel: int, point: Point) -> None:
        self._append_distinct(self._blind_points_by_channel[channel], point)

    def _handle_measurement(
        self,
        env: Environment,
        track: ChannelTrack,
        point: Point,
        result: MeasureResult,
    ) -> None:
        if result.status is not MeasureStatus.NO_SIGNAL:
            self._append_distinct(
                self._visible_points_by_channel[track.channel],
                point,
            )
        super()._handle_measurement(env, track, point, result)

    def _certify_completed_unknown_channels(self) -> None:
        required = len(DIRECTIONAL_SEARCH_POINTS)
        for channel, track in self._tracks.items():
            if (
                track.status is ChannelStatus.UNKNOWN
                and len(self._search_completed_by_channel[channel]) == required
            ):
                track.status = ChannelStatus.ABSENT_CERTIFIED

    def _rolling_search_and_clear(self, env: Environment) -> None:
        """Interleave the certificate tour with beneficial source insertions."""
        if self.options.task_insertion_scheduler:
            unvisited = list(DIRECTIONAL_SEARCH_ROUTE_INDICES)
        else:
            unvisited = list(range(len(DIRECTIONAL_SEARCH_POINTS)))

        while unvisited or any(
            track.status is ChannelStatus.ALIVE for track in self._tracks.values()
        ):
            if self._confirmed_count() >= 16:
                unvisited.clear()
                self._mark_unknown_absent()

            current = _point(env.current_position)
            source_centers = {
                channel: minimum_enclosing_circle(track.polygon).center
                for channel, track in self._tracks.items()
                if track.status is ChannelStatus.ALIVE
            }
            task_type: str | None = None
            identifier: int | None = None

            if self.options.task_insertion_scheduler:
                if unvisited:
                    next_search_index = min(
                        unvisited,
                        key=lambda index: _distance(
                            current,
                            DIRECTIONAL_SEARCH_POINTS[index],
                        ),
                    )
                    next_search = DIRECTIONAL_SEARCH_POINTS[next_search_index]
                    source_channel = _source_before_search(
                        current,
                        next_search,
                        source_centers,
                    )
                    if source_channel is not None:
                        task_type, identifier = "source", source_channel
                        self._source_first_insertions += 1
                    else:
                        task_type, identifier = "search", next_search_index
                        if source_centers:
                            self._search_first_decisions += 1
                elif source_centers:
                    identifier = min(
                        source_centers,
                        key=lambda channel: _distance(
                            current, source_centers[channel]
                        ),
                    )
                    task_type = "source"
            else:
                tasks: list[tuple[float, int, str, int]] = []
                for index in unvisited:
                    tasks.append(
                        (
                            _distance(current, DIRECTIONAL_SEARCH_POINTS[index]),
                            1,
                            "search",
                            index,
                        )
                    )
                for channel, center in source_centers.items():
                    tasks.append(
                        (_distance(current, center), 0, "source", channel)
                    )
                if tasks:
                    _, _, task_type, identifier = min(tasks)

            if task_type is None or identifier is None:
                break
            if task_type == "source":
                self._localize_and_clear(env, self._tracks[identifier])
                continue

            unvisited.remove(identifier)
            search_point = DIRECTIONAL_SEARCH_POINTS[identifier]
            unknown_channels = [
                channel
                for channel, track in self._tracks.items()
                if track.status is ChannelStatus.UNKNOWN
            ]
            for channel in _channel_order(unknown_channels, env.current_channel):
                result = env.measure(_position(search_point), channel)
                self._search_completed_by_channel[channel].add(identifier)
                self._handle_measurement(
                    env,
                    self._tracks[channel],
                    search_point,
                    result,
                )
                self._certify_completed_unknown_channels()
                if self._confirmed_count() >= 16:
                    break
            self._search_points_visited += 1

        self._certify_completed_unknown_channels()

    def _choose_untried_q2_candidate(
        self,
        env: Environment,
        track: ChannelTrack,
        avoided: list[Point],
        *,
        force_joint_direction: bool = False,
    ) -> Point | None:
        """Choose a safe probe using Q2 geometry and Q4 direction history."""
        if track.last_point is None or track.last_bearing_deg is None:
            return None
        current = _point(env.current_position)
        reference = FirstObservation(track.last_point, track.last_bearing_deg)
        candidates, circle = generate_sparse_candidates(
            reference,
            self._q2_config,
            track.polygon,
        )
        candidates = [
            point
            for point in candidates
            if all(_distance(point, prior) > 10.0 for prior in avoided)
        ]

        blind_points = self._blind_points_by_channel[track.channel]
        joint_requested = (
            self.options.joint_direction_ranking or force_joint_direction
        )
        if joint_requested and blind_points:
            reflected: list[Point] = []
            for point in candidates:
                mirror = _reflect_across_bearing_axis(
                    point,
                    track.last_point,
                    track.last_bearing_deg,
                )
                if any(_distance(mirror, prior) <= 10.0 for prior in avoided):
                    continue
                if any(
                    _distance(mirror, prior) <= 1e-7
                    for prior in (*candidates, *reflected)
                ):
                    continue
                if (
                    conservative_safety_margin(
                        mirror,
                        track.polygon,
                        self._q2_config.receive_min,
                    )
                    < -1e-7
                ):
                    continue
                reflected.append(mirror)
            candidates.extend(reflected)
        if not candidates:
            return None

        sources = _representative_polygon_points(
            track.polygon, self.options.q2_source_samples
        )
        errors = _error_grid(
            self.options.bearing_error_deg, self.options.q2_error_nodes
        )
        visible_points = self._visible_points_by_channel[track.channel]
        joint_enabled = (
            joint_requested
            and len(blind_points) >= 2
            and _directional_visibility_fraction(
                circle.center,
                sources,
                visible_points,
                blind_points,
                self.options.direction_heading_samples,
                self._q2_config.near_radius,
            )
            is not None
        )
        if joint_enabled:
            self._joint_direction_rankings += 1

        def ranking_key(score: CandidateScore) -> tuple[float, ...]:
            base = _score_key(score, current, circle.center)
            if not joint_enabled:
                return base
            fraction = _directional_visibility_fraction(
                score.point,
                sources,
                visible_points,
                blind_points,
                self.options.direction_heading_samples,
                self._q2_config.near_radius,
            )
            assert fraction is not None
            return (-fraction, *base)

        scores = [
            evaluate_candidate(
                candidate,
                "q4_sparse",
                reference,
                self._q2_config,
                track.polygon,
                sources,
                errors,
            )
            for candidate in candidates
        ]
        scores.sort(key=ranking_key)

        slack = max(0.0, self._q2_config.receive_min - circle.radius)
        step = min(150.0, max(12.0, 0.4 * slack))
        directions = [
            (math.cos(index * math.pi / 4.0), math.sin(index * math.pi / 4.0))
            for index in range(8)
        ]
        refined: list[CandidateScore] = []
        for seed in scores[: self.options.q2_seed_count]:
            best = seed
            local_step = step
            for _ in range(self.options.q2_local_rounds):
                for dx, dy in directions:
                    point = (
                        best.point[0] + local_step * dx,
                        best.point[1] + local_step * dy,
                    )
                    if any(_distance(point, prior) <= 10.0 for prior in avoided):
                        continue
                    if (
                        conservative_safety_margin(
                            point, track.polygon, self._q2_config.receive_min
                        )
                        < -1e-7
                    ):
                        continue
                    score = evaluate_candidate(
                        point,
                        "q4_local",
                        reference,
                        self._q2_config,
                        track.polygon,
                        sources,
                        errors,
                    )
                    if ranking_key(score) < ranking_key(best):
                        best = score
                local_step *= 0.5
            refined.append(best)

        refined.extend(scores[:3])
        best = min(refined, key=ranking_key)
        self._last_candidate_score_by_channel[track.channel] = best
        return best.point

    def _mirrored_reacquisition_candidate(
        self,
        track: ChannelTrack,
        failed_candidate: Point,
        avoided: list[Point],
    ) -> Point | None:
        """Try the opposite side of the last visible bearing after a blind miss."""
        if track.last_point is None or track.last_bearing_deg is None:
            return None
        candidate = _reflect_across_bearing_axis(
            failed_candidate,
            track.last_point,
            track.last_bearing_deg,
        )
        if any(_distance(candidate, prior) <= 10.0 for prior in avoided):
            return None
        if (
            conservative_safety_margin(
                candidate,
                track.polygon,
                self._q2_config.receive_min,
            )
            < -1e-7
        ):
            return None
        return candidate

    def _localize_and_clear(self, env: Environment, track: ChannelTrack) -> None:
        """Retry a mirrored probe before falling back to a clearing grid."""
        avoided: list[Point] = []
        attempts = 0
        while attempts < self.options.max_active_measurements:
            circle = minimum_enclosing_circle(track.polygon)
            if circle.radius <= self.options.guaranteed_clear_radius_m:
                if self._try_guaranteed_clear(env, track, circle.center):
                    return
                break

            candidate = self._choose_untried_q2_candidate(env, track, avoided)
            if candidate is None:
                break
            result = env.measure(_position(candidate), track.channel)
            track.active_measurements += 1
            attempts += 1
            if result.status is MeasureStatus.NO_SIGNAL:
                track.no_signal_during_localization += 1
                avoided.append(candidate)
                self._record_blind_probe(track.channel, candidate)
                recovery = (
                    self._mirrored_reacquisition_candidate(
                        track,
                        candidate,
                        avoided,
                    )
                    if self.options.mirrored_reacquisition
                    else None
                )
                if recovery is not None and attempts < self.options.max_active_measurements:
                    self._mirrored_reacquisition_attempts += 1
                    recovery_result = env.measure(
                        _position(recovery),
                        track.channel,
                    )
                    track.active_measurements += 1
                    attempts += 1
                    if recovery_result.status is MeasureStatus.NO_SIGNAL:
                        track.no_signal_during_localization += 1
                        avoided.append(recovery)
                        self._record_blind_probe(track.channel, recovery)
                    else:
                        self._mirrored_reacquisition_hits += 1
                        self._handle_measurement(
                            env,
                            track,
                            recovery,
                            recovery_result,
                        )
                        avoided.clear()
                        if track.status is ChannelStatus.CLEARED:
                            return
                continue

            self._handle_measurement(env, track, candidate, result)
            avoided.clear()
            if track.status is ChannelStatus.CLEARED:
                return

        if track.status is ChannelStatus.CLEARED:
            return
        if self.options.adaptive_tail_probe:
            self._try_adaptive_tail_probe(env, track, avoided)
            if track.status is ChannelStatus.CLEARED:
                return
        circle = minimum_enclosing_circle(track.polygon)
        if circle.radius <= self.options.clear_radius_m:
            if self._try_guaranteed_clear(env, track, circle.center):
                return
        self._clear_by_grid(env, track)

    def _build_clear_grid_rows(
        self,
        track: ChannelTrack,
    ) -> tuple[dict[int, list[Point]], dict[int, float], float]:
        """Build the same guaranteed intersecting-cell cover used by V1."""
        origin = track.first_point or track.polygon[0]
        bearing = math.radians(track.first_bearing_deg or 0.0)
        ux, uy = math.cos(bearing), math.sin(bearing)
        vx, vy = -uy, ux
        local = [
            (
                (point[0] - origin[0]) * ux + (point[1] - origin[1]) * uy,
                (point[0] - origin[0]) * vx + (point[1] - origin[1]) * vy,
            )
            for point in track.polygon
        ]
        min_u = min(point[0] for point in local)
        max_u = max(point[0] for point in local)
        min_v = min(point[1] for point in local)
        max_v = max(point[1] for point in local)
        step = self.options.clear_cell_side_m
        columns = max(1, math.ceil((max_u - min_u) / step))
        rows = max(1, math.ceil((max_v - min_v) / step))
        circle_center = minimum_enclosing_circle(track.polygon).center
        center_v = (
            (circle_center[0] - origin[0]) * vx
            + (circle_center[1] - origin[1]) * vy
        )

        row_points: dict[int, list[Point]] = {}
        row_v: dict[int, float] = {}
        for row in range(rows):
            low_v = min_v + row * step
            high_v = low_v + step
            strip_u: list[float] = []
            for point in local:
                if low_v - 1e-9 <= point[1] <= high_v + 1e-9:
                    strip_u.append(point[0])
            for index, first in enumerate(local):
                second = local[(index + 1) % len(local)]
                dv = second[1] - first[1]
                if abs(dv) <= 1e-12:
                    continue
                for boundary_v in (low_v, high_v):
                    fraction = (boundary_v - first[1]) / dv
                    if -1e-12 <= fraction <= 1.0 + 1e-12:
                        strip_u.append(
                            first[0] + fraction * (second[0] - first[0])
                        )
            if not strip_u:
                continue
            first_column = max(
                0,
                min(columns - 1, math.floor((min(strip_u) - min_u) / step)),
            )
            last_column = max(
                0,
                min(columns - 1, math.floor((max(strip_u) - min_u) / step)),
            )
            points: list[Point] = []
            for column in range(first_column, last_column + 1):
                u = min_u + (column + 0.5) * step
                v = min_v + (row + 0.5) * step
                points.append(
                    (
                        origin[0] + u * ux + v * vx,
                        origin[1] + u * uy + v * vy,
                    )
                )
            row_points[row] = points
            row_v[row] = min_v + (row + 0.5) * step
        return row_points, row_v, center_v

    def _clear_grid_plan(
        self,
        track: ChannelTrack,
        current: Point,
        *,
        direction_aware: bool,
    ) -> tuple[list[Point], bool]:
        """Order every guaranteed grid cell, optionally using direction history."""
        row_points, row_v, center_v = self._build_clear_grid_rows(track)
        point_weights: dict[Point, int] = {}
        blind_points = self._blind_points_by_channel[track.channel]
        visible_points = self._visible_points_by_channel[track.channel]
        if direction_aware and blind_points:
            point_weights = {
                point: _compatible_heading_count(
                    point,
                    visible_points,
                    blind_points,
                    self.options.direction_heading_samples,
                )
                for points in row_points.values()
                for point in points
            }
        used_direction = bool(point_weights) and max(point_weights.values()) > 0
        if used_direction:
            row_order = sorted(
                row_points,
                key=lambda row: (
                    -max(point_weights[point] for point in row_points[row]),
                    -sum(point_weights[point] for point in row_points[row]),
                    abs(row_v[row] - center_v),
                ),
            )
        else:
            row_order = sorted(
                row_points,
                key=lambda row: abs(row_v[row] - center_v),
            )

        plan: list[Point] = []
        cursor = current
        for row in row_order:
            points = list(row_points[row])
            reverse = False
            if used_direction:
                weights = [point_weights[point] for point in points]
                best_weight = max(weights)
                first_best = weights.index(best_weight)
                last_best = len(weights) - 1 - weights[::-1].index(best_weight)
                forward_rank = (
                    first_best,
                    _distance(cursor, points[0]),
                )
                reverse_rank = (
                    len(points) - 1 - last_best,
                    _distance(cursor, points[-1]),
                )
                reverse = reverse_rank < forward_rank
            else:
                reverse = (
                    _distance(cursor, points[-1])
                    < _distance(cursor, points[0])
                )
            if reverse:
                points.reverse()
            plan.extend(points)
            cursor = points[-1]
        return plan, used_direction

    @staticmethod
    def _estimated_grid_time_s(plan: list[Point], current: Point) -> float:
        """Estimate a full scan with the same cost used by both terminals."""
        return estimate_full_clear_time_s(plan, current)

    def _analytic_clear_plan(
        self,
        track: ChannelTrack,
        current: Point,
    ) -> CertifiedStripPlan | None:
        """Construct a certified adaptive-strip cover in the first-bearing frame."""
        if not track.polygon:
            return None
        certified_radius_m = min(
            self.options.guaranteed_clear_radius_m,
            self.options.clear_radius_m - 1e-6,
        )
        return build_certified_strip_plan(
            track.polygon,
            origin=track.first_point or track.polygon[0],
            bearing_deg=track.first_bearing_deg or 0.0,
            current=current,
            certified_radius_m=certified_radius_m,
        )

    def _tail_terminal_cost_s(
        self,
        track: ChannelTrack,
        current: Point,
        grid_plan: list[Point],
    ) -> float:
        """Return A1 grid cost or the A2 linked certified terminal cost."""
        grid_cost_s = self._estimated_grid_time_s(grid_plan, current)
        if not self.options.tail_terminal_linkage:
            return grid_cost_s

        self._tail_terminal_linkage_evaluations += 1
        analytic = self._analytic_clear_plan(track, current)
        if analytic is None:
            return grid_cost_s
        if grid_plan and analytic.estimated_time_s + 1e-9 >= grid_cost_s:
            return grid_cost_s

        self._tail_terminal_analytic_choices += 1
        self._tail_terminal_estimated_cost_reduction_s += max(
            0.0,
            grid_cost_s - analytic.estimated_time_s,
        )
        return analytic.estimated_time_s

    def _tail_visibility_fraction(
        self,
        track: ChannelTrack,
        candidate: Point,
    ) -> float | None:
        sources = _representative_polygon_points(
            track.polygon,
            max(self.options.q2_source_samples, 96),
        )
        return _directional_visibility_fraction(
            candidate,
            sources,
            self._visible_points_by_channel[track.channel],
            self._blind_points_by_channel[track.channel],
            self.options.direction_heading_samples,
            self._q2_config.near_radius,
        )

    def _try_adaptive_tail_probe(
        self,
        env: Environment,
        track: ChannelTrack,
        avoided: list[Point],
    ) -> None:
        """Buy one extra probe only when its geometric value beats grid cost."""
        if len(self._blind_points_by_channel[track.channel]) < 2:
            return
        current = _point(env.current_position)
        plan, _ = self._clear_grid_plan(
            track,
            current,
            direction_aware=self.options.direction_aware_grid_ordering,
        )
        terminal_cost_s = self._tail_terminal_cost_s(track, current, plan)
        candidate = self._choose_untried_q2_candidate(
            env,
            track,
            avoided,
            force_joint_direction=True,
        )
        if candidate is None:
            return
        visible_fraction = self._tail_visibility_fraction(track, candidate)
        if visible_fraction is None:
            return
        if visible_fraction < self.options.adaptive_tail_min_visibility:
            return
        probe_cost_s = _distance(current, candidate) / 5.0 + 5.0
        current_diameter_m = max(
            _distance(first, second)
            for first in track.polygon
            for second in track.polygon
        )
        score = self._last_candidate_score_by_channel.get(track.channel)
        if score is None or current_diameter_m <= 1e-9:
            return
        retained_area_fraction = min(
            1.0,
            (score.worst_posterior_diameter_m / current_diameter_m) ** 2,
        )
        estimated_saving_s = (
            visible_fraction
            * terminal_cost_s
            * (1.0 - retained_area_fraction)
        )
        if probe_cost_s >= estimated_saving_s:
            return

        self._adaptive_tail_probe_attempts += 1
        result = env.measure(_position(candidate), track.channel)
        track.active_measurements += 1
        if result.status is MeasureStatus.NO_SIGNAL:
            track.no_signal_during_localization += 1
            self._record_blind_probe(track.channel, candidate)
            return
        self._adaptive_tail_probe_hits += 1
        self._handle_measurement(env, track, candidate, result)

    def _clear_by_grid(self, env: Environment, track: ChannelTrack) -> None:
        """Choose the cheaper certified terminal, retaining the V3 grid fallback."""
        if not self.options.prioritized_clear_grid:
            super()._clear_by_grid(env, track)
            return
        if not track.polygon:
            return

        current = _point(env.current_position)
        grid_plan, used_direction = self._clear_grid_plan(
            track,
            current,
            direction_aware=self.options.direction_aware_grid_ordering,
        )
        selected_plan = grid_plan
        selected_analytic = False

        if self.options.analytic_clear_terminal:
            self._analytic_plan_generated += 1
            analytic = self._analytic_clear_plan(track, current)
            if analytic is None:
                self._analytic_plan_fallbacks += 1
            else:
                self._analytic_plan_certified += 1
                grid_cost_s = self._estimated_grid_time_s(grid_plan, current)
                if (
                    not grid_plan
                    or analytic.estimated_time_s + 1e-9 < grid_cost_s
                ):
                    selected_plan = list(analytic.points)
                    selected_analytic = True
                    self._analytic_plan_selected += 1
                    self._analytic_estimated_saving_s += max(
                        0.0, grid_cost_s - analytic.estimated_time_s
                    )

        if used_direction and not selected_analytic:
            self._direction_aware_grid_uses += 1
        for point in selected_plan:
            self._fallback_clear_attempts += 1
            result = env.clear(_position(point), track.channel)
            if result.status is ClearStatus.SUCCESS:
                track.status = ChannelStatus.CLEARED
                return
__all__ = [
    "DIRECTIONAL_INNER_RADIUS_M",
    "DIRECTIONAL_OUTER_RADIUS_M",
    "DIRECTIONAL_SEARCH_POINTS",
    "DIRECTIONAL_SEARCH_ROUTE_INDICES",
    "GuaranteedDirectionalQ4Strategy",
    "Q4StrategyOptions",
    "build_directionally_complete_search_points",
    "directional_search_certificate",
    "directional_search_route_length_m",
    "directional_search_triangles",
]
