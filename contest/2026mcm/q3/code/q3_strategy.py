"""具有完备发现保证并支持快速主动定位的 Q3 策略。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from pathlib import Path
import sys
from typing import Sequence

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SHARED_CODE = _PROJECT_ROOT / "code"
_Q1_CODE = _PROJECT_ROOT / "q1" / "code"
_Q2_CODE = _PROJECT_ROOT / "q2" / "code"
for _code_dir in (_SHARED_CODE, _Q1_CODE, _Q2_CODE):
    if str(_code_dir) not in sys.path:
        sys.path.insert(0, str(_code_dir))

from radio_sim.domain.models import (  # noqa: E402
    ClearResult,
    ClearStatus,
    MeasureResult,
    MeasureStatus,
    Position,
    StrategyResult,
)
from radio_sim.environment.base import Environment, EnvironmentStateError  # noqa: E402
from q2_fast import (  # noqa: E402
    CandidateScore,
    build_position_outer_polygon,
    conservative_safety_margin,
    evaluate_candidate,
    generate_sparse_candidates,
    minimum_enclosing_circle,
    posterior_polygon,
)
from q2_state import FirstObservation, Q2Config  # noqa: E402

Point = tuple[float, float]


class ChannelStatus(str, Enum):
    UNKNOWN = "unknown"
    ALIVE = "alive"
    CLEARED = "cleared"
    ABSENT_CERTIFIED = "absent_certified"


class AbsenceReason(str, Enum):
    COVER_COMPLETE_NO_SIGNAL = "cover_complete_no_signal"
    GLOBAL_COUNT_UPPER_BOUND = "global_count_upper_bound"


class RegionHealth(str, Enum):
    EMPTY = "empty"
    HEALTHY_CURRENT = "healthy_current"
    SAFE_STALE = "safe_stale"
    INVALID = "invalid"


@dataclass(frozen=True)
class ObservationEvent:
    event_id: int
    purpose: str
    point: Point
    status: MeasureStatus
    angle_deg: float | None
    virtual_time_s: float


@dataclass(frozen=True)
class ClearEvent:
    event_id: int
    purpose: str
    point: Point
    status: ClearStatus
    virtual_time_s: float


@dataclass(frozen=True)
class LifecycleEvent:
    event_id: int
    old_status: ChannelStatus
    new_status: ChannelStatus
    reason: str


@dataclass(frozen=True)
class CompletionCertificate:
    valid: bool
    state_version: int
    built_from_version: int
    history_consistent: bool
    pending_request_empty: bool
    cleared_channels: tuple[int, ...]
    absent_channels: tuple[int, ...]
    per_channel_reasons: tuple[tuple[int, str], ...]
    per_channel_evidence: tuple[
        tuple[int, tuple[int, ...], tuple[Point, ...], tuple[int, ...]], ...
    ]
    global_reason: str | None

    def to_record(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "state_version": self.state_version,
            "built_from_version": self.built_from_version,
            "history_consistent": self.history_consistent,
            "pending_request_empty": self.pending_request_empty,
            "cleared_channels": list(self.cleared_channels),
            "absent_channels": list(self.absent_channels),
            "per_channel_reasons": {
                str(channel): reason for channel, reason in self.per_channel_reasons
            },
            "per_channel_evidence": {
                str(channel): {
                    "event_ids": list(event_ids),
                    "search_points": [list(point) for point in search_points],
                    "confirmed_channels": list(confirmed_channels),
                }
                for channel, event_ids, search_points, confirmed_channels
                in self.per_channel_evidence
            },
            "global_reason": self.global_reason,
        }


@dataclass
class ChannelTrack:
    channel: int
    status: ChannelStatus = ChannelStatus.UNKNOWN
    polygon: list[Point] = field(default_factory=list)
    first_point: Point | None = None
    first_bearing_deg: float | None = None
    last_point: Point | None = None
    last_bearing_deg: float | None = None
    active_measurements: int = 0
    no_signal_during_localization: int = 0
    observations: list[ObservationEvent] = field(default_factory=list)
    clear_attempts: list[ClearEvent] = field(default_factory=list)
    lifecycle_events: list[LifecycleEvent] = field(default_factory=list)
    repeated_location_anchors: dict[Point, int] = field(default_factory=dict)
    absence_reason: AbsenceReason | None = None
    absence_evidence_event_ids: tuple[int, ...] = ()
    absence_confirmed_channels: tuple[int, ...] = ()
    region_health: RegionHealth = RegionHealth.EMPTY
    state_version: int = 0
    region_built_from_version: int = 0


@dataclass(frozen=True)
class Q3StrategyOptions:
    bearing_error_deg: float = 1.005
    safety_buffer_m: float = 5.0
    max_active_measurements: int = 4
    q2_circle_sides: int = 48
    q2_source_samples: int = 30
    q2_error_nodes: int = 3
    q2_seed_count: int = 3
    q2_local_rounds: int = 3
    clear_radius_m: float = 20.0
    clear_cell_side_m: float = 26.0
    guaranteed_clear_radius_m: float = 19.5

    def validate(self) -> None:
        if not 1.0 <= self.bearing_error_deg < 90.0:
            raise ValueError("bearing_error_deg 必须覆盖官方规定的 1° 误差")
        if not 0.0 <= self.safety_buffer_m < 995.0:
            raise ValueError("safety_buffer_m 必须位于 [0, 995) 内")
        if self.max_active_measurements < 0:
            raise ValueError("max_active_measurements 必须非负")
        if self.q2_circle_sides < 8:
            raise ValueError("q2_circle_sides 必须至少为 8")
        if self.q2_source_samples <= 0 or self.q2_error_nodes <= 0:
            raise ValueError("Q2 采样数量必须为正数")
        if self.q2_seed_count <= 0 or self.q2_local_rounds < 0:
            raise ValueError("Q2 局部搜索设置无效")
        if not 0.0 < self.clear_cell_side_m < self.clear_radius_m * math.sqrt(2.0):
            raise ValueError("清除单元的半对角线必须小于清除半径")
        if not 0.0 < self.guaranteed_clear_radius_m <= self.clear_radius_m:
            raise ValueError("保证清除半径无效")


SEARCH_RING_RADIUS_M = 1140.0
_SEARCH_RING_HEIGHT_M = SEARCH_RING_RADIUS_M * math.sqrt(3.0) / 2.0
SEARCH_ROUTE: tuple[Point, ...] = (
    (0.0, 0.0),
    (SEARCH_RING_RADIUS_M, 0.0),
    (SEARCH_RING_RADIUS_M / 2.0, _SEARCH_RING_HEIGHT_M),
    (-SEARCH_RING_RADIUS_M / 2.0, _SEARCH_RING_HEIGHT_M),
    (-SEARCH_RING_RADIUS_M, 0.0),
    (-SEARCH_RING_RADIUS_M / 2.0, -_SEARCH_RING_HEIGHT_M),
    (SEARCH_RING_RADIUS_M / 2.0, -_SEARCH_RING_HEIGHT_M),
)


def search_cover_bound_m() -> float:
    """计算圆心加正六边形覆盖在外边界上的解析最坏距离。"""
    return math.sqrt(
        1800.0**2
        + SEARCH_RING_RADIUS_M**2
        - 2.0 * 1800.0 * SEARCH_RING_RADIUS_M * math.cos(math.pi / 6.0)
    )


def _point(position: Position) -> Point:
    return (position.x, position.y)


def _position(point: Point) -> Position:
    return Position(point[0], point[1])


def _distance(first: Point, second: Point) -> float:
    return math.hypot(first[0] - second[0], first[1] - second[1])


def _deduplicate(points: Sequence[Point], tolerance: float = 1e-7) -> list[Point]:
    result: list[Point] = []
    for point in points:
        if all(_distance(point, other) > tolerance for other in result):
            result.append(point)
    return result


def _fallback_initial_polygon(
    point: Point, bearing_deg: float, error_deg: float, range_m: float = 1500.0
) -> list[Point]:
    """仅在正式外包交集退化时使用的保守三角形。"""
    theta = math.radians(bearing_deg)
    epsilon = math.radians(error_deg)
    # 半径 ``range_m`` 上两点之间的弦是内接弦，会漏掉合法圆弧的中部。
    # 将两条射线延伸至 range/cos(epsilon)，可使该弦落在切向支撑线上，
    # 从而让此三角形成为完整扇形的外包近似。
    outer_ray_m = range_m / math.cos(epsilon)
    return [
        point,
        (
            point[0] + outer_ray_m * math.cos(theta - epsilon),
            point[1] + outer_ray_m * math.sin(theta - epsilon),
        ),
        (
            point[0] + outer_ray_m * math.cos(theta + epsilon),
            point[1] + outer_ray_m * math.sin(theta + epsilon),
        ),
    ]


def _representative_polygon_points(
    polygon: Sequence[Point], limit: int
) -> list[Point]:
    if not polygon:
        return []
    centroid = (
        sum(point[0] for point in polygon) / len(polygon),
        sum(point[1] for point in polygon) / len(polygon),
    )
    pool: list[Point] = list(polygon) + [centroid]
    for index, first in enumerate(polygon):
        second = polygon[(index + 1) % len(polygon)]
        for fraction in (0.25, 0.5, 0.75):
            pool.append(
                (
                    first[0] + fraction * (second[0] - first[0]),
                    first[1] + fraction * (second[1] - first[1]),
                )
            )
        pool.append(((first[0] + centroid[0]) / 2.0, (first[1] + centroid[1]) / 2.0))
    pool = _deduplicate(pool)
    if len(pool) <= limit:
        return pool

    selected = [max(pool, key=lambda item: _distance(item, centroid))]
    while len(selected) < limit:
        selected.append(
            max(
                pool,
                key=lambda item: min(_distance(item, chosen) for chosen in selected),
            )
        )
    return _deduplicate(selected)[:limit]


def _error_grid(error_deg: float, count: int) -> list[float]:
    if count <= 1:
        return [0.0]
    return [
        -error_deg + 2.0 * error_deg * index / (count - 1)
        for index in range(count)
    ]


def _score_key(
    score: CandidateScore,
    current: Point,
    target: Point,
) -> tuple[float, float, float, float]:
    """估计先测量后清除的移动代价，并惩罚过宽的后验区域。"""
    route_m = _distance(current, score.point) + _distance(score.point, target)
    excess_diameter_m = max(0.0, score.worst_posterior_diameter_m - 39.0)
    time_aware_cost_m = route_m + 0.85 * excess_diameter_m
    return (
        time_aware_cost_m,
        score.worst_posterior_diameter_m,
        route_m,
        -score.conservative_safety_margin_m,
    )


def _channel_order(channels: Sequence[int], current_channel: int) -> list[int]:
    """优先扫描当前信道，再按单调顺序扫描，以减少可避免的信道切换。"""
    unique = sorted(set(channels))
    if current_channel not in unique:
        return unique
    return [current_channel] + [channel for channel in unique if channel != current_channel]


class GuaranteedRollingQ3Strategy:
    """带确定性发现与清除兜底的 Q3 基线策略。"""

    def __init__(self, options: Q3StrategyOptions | None = None) -> None:
        self.options = options or Q3StrategyOptions()
        self.options.validate()
        self._tracks = {channel: ChannelTrack(channel) for channel in range(1, 21)}
        self._q2_config = Q2Config(
            center=(0.0, 0.0),
            target_radius=1800.0,
            error_deg=self.options.bearing_error_deg,
            near_radius=5.0,
            receive_min=1000.0 - self.options.safety_buffer_m,
            receive_max=1500.0,
        )
        self._search_points_visited = 0
        self._fallback_clear_attempts = 0
        self._guaranteed_clear_attempts = 0
        self._state_version = 0
        self._polygon_rebuild_count = 0
        self._polygon_rebuild_failure_count = 0
        self._last_completion_certificate: CompletionCertificate | None = None

    @property
    def completion_certificate(self) -> CompletionCertificate | None:
        return self._last_completion_certificate

    def _next_state_version(self) -> int:
        self._state_version += 1
        return self._state_version

    @staticmethod
    def _has_pending_request(env: Environment) -> bool:
        return bool(getattr(env, "has_pending_request", False))

    def _call_with_pending_recovery(self, env: Environment, action: object, *args: object) -> object:
        try:
            return action(*args)  # type: ignore[operator]
        except EnvironmentStateError:
            if not self._has_pending_request(env):
                raise
            recover = getattr(env, "recover_pending", None)
            if not callable(recover):
                raise
            return recover()

    def _record_observation(
        self,
        track: ChannelTrack,
        point: Point,
        result: MeasureResult,
        purpose: str,
    ) -> ObservationEvent:
        event = ObservationEvent(
            event_id=self._next_state_version(),
            purpose=purpose,
            point=point,
            status=result.status,
            angle_deg=result.angle_deg,
            virtual_time_s=result.virtual_time_s,
        )
        track.observations.append(event)
        anchor = (round(point[0], 7), round(point[1], 7))
        track.repeated_location_anchors.setdefault(anchor, event.event_id)
        track.state_version = event.event_id
        return event

    def _record_clear(
        self,
        track: ChannelTrack,
        point: Point,
        result: ClearResult,
        purpose: str,
    ) -> ClearEvent:
        event = ClearEvent(
            event_id=self._next_state_version(),
            purpose=purpose,
            point=point,
            status=result.status,
            virtual_time_s=result.virtual_time_s,
        )
        track.clear_attempts.append(event)
        track.state_version = event.event_id
        return event

    def _transition(
        self,
        track: ChannelTrack,
        new_status: ChannelStatus,
        reason: str,
    ) -> None:
        if track.status is new_status:
            return
        old_status = track.status
        event_id = self._next_state_version()
        track.status = new_status
        track.state_version = event_id
        track.lifecycle_events.append(
            LifecycleEvent(event_id, old_status, new_status, reason)
        )

    def _measure_action(
        self,
        env: Environment,
        track: ChannelTrack,
        point: Point,
        purpose: str,
    ) -> MeasureResult:
        result = self._call_with_pending_recovery(
            env, env.measure, _position(point), track.channel
        )
        if not isinstance(result, MeasureResult):
            raise EnvironmentStateError("恢复的测量请求返回了错误的结果类型")
        self._record_observation(track, point, result, purpose)
        return result

    def _clear_action(
        self,
        env: Environment,
        track: ChannelTrack,
        point: Point,
        purpose: str,
    ) -> ClearResult:
        result = self._call_with_pending_recovery(
            env, env.clear, _position(point), track.channel
        )
        if not isinstance(result, ClearResult):
            raise EnvironmentStateError("恢复的清除请求返回了错误的结果类型")
        self._record_clear(track, point, result, purpose)
        return result

    def _exit_action(self, env: Environment) -> None:
        self._call_with_pending_recovery(env, env.exit)

    def run(self, env: Environment) -> StrategyResult:
        try:
            self._call_with_pending_recovery(env, env.enter)
            self._rolling_search_and_clear(env)
            certificate = self._completion_certificate(env)
            self._last_completion_certificate = certificate
            if certificate.valid and env.state.is_active:
                self._exit_action(env)
            elif env.state.is_active and not self._has_pending_request(env):
                # 正常结束未完成会话，但绝不能将其描述为成功。
                self._exit_action(env)
            note = (
                f"visited_search_points={self._search_points_visited};"
                f"fallback_clear_attempts={self._fallback_clear_attempts};"
                f"guaranteed_clear_attempts={self._guaranteed_clear_attempts};"
                f"polygon_rebuilds={self._polygon_rebuild_count};"
                f"polygon_rebuild_failures={self._polygon_rebuild_failure_count};"
                f"state_version={self._state_version};"
                f"certificate={certificate.valid};"
                f"certificate_reason={certificate.global_reason}"
            )
            return StrategyResult(
                strategy_name=type(self).__name__,
                completed=certificate.valid,
                note=note,
            )
        except EnvironmentStateError as exc:
            pending = self._has_pending_request(env)
            if env.state.is_active and not pending:
                try:
                    self._exit_action(env)
                except EnvironmentStateError:
                    pass
            certificate = self._completion_certificate(env)
            self._last_completion_certificate = certificate
            return StrategyResult(
                strategy_name=type(self).__name__,
                completed=False,
                note=(
                    "environment ended before the completion certificate: "
                    f"{type(exc).__name__}: {exc};"
                    f"pending_request={pending};"
                    f"state_version={self._state_version}"
                ),
            )

    def _confirmed_count(self) -> int:
        return sum(
            track.status in (ChannelStatus.ALIVE, ChannelStatus.CLEARED)
            for track in self._tracks.values()
        )

    def _required_absence_cover_points(self) -> Sequence[Point]:
        return SEARCH_ROUTE

    def _absence_evidence_valid(self, track: ChannelTrack) -> bool:
        if track.absence_reason is AbsenceReason.GLOBAL_COUNT_UPPER_BOUND:
            confirmed = set(track.absence_confirmed_channels)
            return len(confirmed) >= 16 and all(
                channel in self._tracks
                and any(
                    event.status in (MeasureStatus.DIRECTION, MeasureStatus.NEAR)
                    for event in self._tracks[channel].observations
                )
                for channel in confirmed
            )
        if track.absence_reason is AbsenceReason.COVER_COMPLETE_NO_SIGNAL:
            events = {
                event.event_id: event
                for event in track.observations
                if event.purpose == "search" and event.status is MeasureStatus.NO_SIGNAL
            }
            evidence = [
                events[event_id]
                for event_id in track.absence_evidence_event_ids
                if event_id in events
            ]
            if len(evidence) != len(track.absence_evidence_event_ids):
                return False
            observed_points = {
                (round(event.point[0], 7), round(event.point[1], 7))
                for event in evidence
            }
            required_points = {
                (round(point[0], 7), round(point[1], 7))
                for point in self._required_absence_cover_points()
            }
            return bool(evidence) and required_points.issubset(observed_points)
        return False

    def _completion_certificate(self, env: Environment | None = None) -> CompletionCertificate:
        cleared = tuple(
            channel
            for channel, track in self._tracks.items()
            if track.status is ChannelStatus.CLEARED
        )
        absent = tuple(
            channel
            for channel, track in self._tracks.items()
            if track.status is ChannelStatus.ABSENT_CERTIFIED
        )
        history_consistent = all(
            (
                track.status is not ChannelStatus.CLEARED
                or any(
                    event.status is ClearStatus.SUCCESS
                    for event in track.clear_attempts
                )
            )
            and (
                track.status is not ChannelStatus.ABSENT_CERTIFIED
                or self._absence_evidence_valid(track)
            )
            for track in self._tracks.values()
        )
        pending_empty = env is None or not self._has_pending_request(env)
        all_resolved = all(
            track.status in (ChannelStatus.CLEARED, ChannelStatus.ABSENT_CERTIFIED)
            for track in self._tracks.values()
        )
        if len(cleared) >= 16:
            global_reason = "sixteen_cleared_by_count_bound"
        elif all_resolved:
            global_reason = "all_channels_resolved"
        else:
            global_reason = None
        valid = bool(global_reason) and history_consistent and pending_empty
        per_channel_reasons = tuple(
            (
                channel,
                "clear_success"
                if track.status is ChannelStatus.CLEARED
                else track.absence_reason.value
                if track.absence_reason is not None
                else track.status.value,
            )
            for channel, track in self._tracks.items()
        )
        per_channel_evidence = tuple(
            (
                channel,
                tuple(
                    event.event_id
                    for event in track.clear_attempts
                    if event.status is ClearStatus.SUCCESS
                )
                if track.status is ChannelStatus.CLEARED
                else track.absence_evidence_event_ids,
                tuple(
                    event.point
                    for event in track.observations
                    if event.event_id in track.absence_evidence_event_ids
                ),
                track.absence_confirmed_channels,
            )
            for channel, track in self._tracks.items()
            if track.status in (ChannelStatus.CLEARED, ChannelStatus.ABSENT_CERTIFIED)
        )
        return CompletionCertificate(
            valid=valid,
            state_version=self._state_version,
            built_from_version=self._state_version,
            history_consistent=history_consistent,
            pending_request_empty=pending_empty,
            cleared_channels=cleared,
            absent_channels=absent,
            per_channel_reasons=per_channel_reasons,
            per_channel_evidence=per_channel_evidence,
            global_reason=global_reason,
        )

    def _rolling_search_and_clear(self, env: Environment) -> None:
        """以贪心方式交错安排强制覆盖点和已发现干扰源。"""
        unvisited = list(SEARCH_ROUTE)
        while unvisited or any(
            track.status is ChannelStatus.ALIVE for track in self._tracks.values()
        ):
            if self._confirmed_count() >= 16:
                unvisited.clear()
                self._mark_unknown_absent()

            current = _point(env.current_position)
            tasks: list[tuple[float, int, str, int]] = []
            for index, search_point in enumerate(unvisited):
                tasks.append((_distance(current, search_point), 1, "search", index))
            for channel, track in self._tracks.items():
                if track.status is ChannelStatus.ALIVE:
                    center = minimum_enclosing_circle(track.polygon).center
                    tasks.append((_distance(current, center), 0, "source", channel))
            if not tasks:
                break

            _, _, task_type, identifier = min(tasks)
            if task_type == "source":
                self._localize_and_clear(env, self._tracks[identifier])
                continue

            search_point = unvisited.pop(identifier)
            unknown_channels = [
                channel
                for channel, track in self._tracks.items()
                if track.status is ChannelStatus.UNKNOWN
            ]
            for channel in _channel_order(unknown_channels, env.current_channel):
                track = self._tracks[channel]
                result = self._measure_action(env, track, search_point, "search")
                self._handle_measurement(
                    env,
                    track,
                    search_point,
                    result,
                )
                if self._confirmed_count() >= 16:
                    break
            self._search_points_visited += 1
            if not unvisited or self._confirmed_count() >= 16:
                self._mark_unknown_absent()

    def _set_absent_certified(
        self,
        track: ChannelTrack,
        reason: AbsenceReason,
        *,
        evidence_event_ids: Sequence[int] = (),
        confirmed_channels: Sequence[int] = (),
    ) -> None:
        track.absence_reason = reason
        track.absence_evidence_event_ids = tuple(evidence_event_ids)
        track.absence_confirmed_channels = tuple(confirmed_channels)
        self._transition(track, ChannelStatus.ABSENT_CERTIFIED, reason.value)

    def _mark_unknown_absent(self) -> None:
        confirmed_channels = tuple(
            channel
            for channel, track in self._tracks.items()
            if track.status in (ChannelStatus.ALIVE, ChannelStatus.CLEARED)
        )
        count_bound = len(confirmed_channels) >= 16
        required_points = {
            (round(point[0], 7), round(point[1], 7)) for point in SEARCH_ROUTE
        }
        for track in self._tracks.values():
            if track.status is not ChannelStatus.UNKNOWN:
                continue
            if count_bound:
                self._set_absent_certified(
                    track,
                    AbsenceReason.GLOBAL_COUNT_UPPER_BOUND,
                    confirmed_channels=confirmed_channels,
                )
                continue
            search_events = [
                event
                for event in track.observations
                if event.purpose == "search" and event.status is MeasureStatus.NO_SIGNAL
            ]
            observed_points = {
                (round(event.point[0], 7), round(event.point[1], 7))
                for event in search_events
            }
            if required_points.issubset(observed_points):
                self._set_absent_certified(
                    track,
                    AbsenceReason.COVER_COMPLETE_NO_SIGNAL,
                    evidence_event_ids=[event.event_id for event in search_events],
                )

    def _discovery_phase(self, env: Environment) -> None:
        for search_point in SEARCH_ROUTE:
            if self._confirmed_count() >= 16:
                break
            unknown_channels = [
                channel
                for channel, track in self._tracks.items()
                if track.status is ChannelStatus.UNKNOWN
            ]
            if not unknown_channels:
                break
            for channel in _channel_order(unknown_channels, env.current_channel):
                track = self._tracks[channel]
                result = self._measure_action(env, track, search_point, "search")
                self._handle_measurement(env, track, search_point, result)
                if self._confirmed_count() >= 16:
                    break
            self._search_points_visited += 1

        if self._confirmed_count() >= 16 or self._search_points_visited == len(SEARCH_ROUTE):
            self._mark_unknown_absent()

    def _handle_measurement(
        self,
        env: Environment,
        track: ChannelTrack,
        point: Point,
        result: MeasureResult,
    ) -> None:
        status = result.status
        if status is MeasureStatus.NO_SIGNAL:
            return
        if status is MeasureStatus.NEAR:
            self._transition(track, ChannelStatus.ALIVE, "near_observation")
            clear_result = self._clear_action(env, track, point, "near_immediate")
            if clear_result.status is ClearStatus.SUCCESS:
                self._transition(track, ChannelStatus.CLEARED, "near_clear_success")
            else:
                track.region_health = RegionHealth.INVALID
                raise EnvironmentStateError(
                    "near 观测后在同一点清除失败；官方几何约定出现矛盾"
                )
            return

        assert status is MeasureStatus.DIRECTION
        assert result.angle_deg is not None
        self._transition(track, ChannelStatus.ALIVE, "direction_observation")
        if not track.polygon:
            first = FirstObservation(point, result.angle_deg)
            try:
                polygon = build_position_outer_polygon(
                    first, self._q2_config, self.options.q2_circle_sides
                )
            except ValueError:
                polygon = _fallback_initial_polygon(
                    point, result.angle_deg, self.options.bearing_error_deg
                )
            if len(polygon) < 3:
                polygon = _fallback_initial_polygon(
                    point, result.angle_deg, self.options.bearing_error_deg
                )
            track.polygon = polygon
            track.region_health = RegionHealth.HEALTHY_CURRENT
            track.region_built_from_version = track.state_version
            track.first_point = point
            track.first_bearing_deg = result.angle_deg
        else:
            old_polygon = list(track.polygon)
            clipped = posterior_polygon(
                track.polygon,
                point,
                result.angle_deg,
                self.options.bearing_error_deg,
            )
            if len(clipped) >= 3:
                track.polygon = clipped
                track.region_health = RegionHealth.HEALTHY_CURRENT
                track.region_built_from_version = track.state_version
            else:
                self._polygon_rebuild_count += 1
                rebuilt = self._rebuild_polygon_from_evidence(track)
                if rebuilt is not None:
                    track.polygon = rebuilt
                    track.region_health = RegionHealth.HEALTHY_CURRENT
                    track.region_built_from_version = track.state_version
                elif old_polygon:
                    self._polygon_rebuild_failure_count += 1
                    track.polygon = old_polygon
                    track.region_health = RegionHealth.SAFE_STALE
                else:
                    self._polygon_rebuild_failure_count += 1
                    track.region_health = RegionHealth.INVALID
        track.last_point = point
        track.last_bearing_deg = result.angle_deg

    def _rebuild_polygon_from_evidence(self, track: ChannelTrack) -> list[Point] | None:
        direction_events = [
            event
            for event in track.observations
            if event.status is MeasureStatus.DIRECTION and event.angle_deg is not None
        ]
        if not direction_events:
            return None

        unique: list[ObservationEvent] = []
        by_anchor: dict[Point, ObservationEvent] = {}
        for event in direction_events:
            anchor = (round(event.point[0], 7), round(event.point[1], 7))
            prior = by_anchor.get(anchor)
            if prior is not None:
                difference = abs(
                    (float(event.angle_deg) - float(prior.angle_deg) + 180.0)
                    % 360.0
                    - 180.0
                )
                if difference > 1e-7:
                    return None
                continue
            by_anchor[anchor] = event
            unique.append(event)

        first_event = unique[0]
        first = FirstObservation(first_event.point, float(first_event.angle_deg))
        try:
            polygon = build_position_outer_polygon(
                first, self._q2_config, self.options.q2_circle_sides
            )
        except ValueError:
            polygon = _fallback_initial_polygon(
                first_event.point,
                float(first_event.angle_deg),
                self.options.bearing_error_deg,
            )
        if len(polygon) < 3:
            polygon = _fallback_initial_polygon(
                first_event.point,
                float(first_event.angle_deg),
                self.options.bearing_error_deg,
            )
        for event in unique[1:]:
            polygon = posterior_polygon(
                polygon,
                event.point,
                float(event.angle_deg),
                self.options.bearing_error_deg,
            )
            if len(polygon) < 3:
                return None
        return polygon

    def _localization_phase(self, env: Environment) -> None:
        while True:
            alive = [
                track
                for track in self._tracks.values()
                if track.status is ChannelStatus.ALIVE
            ]
            if not alive:
                return
            current = _point(env.current_position)
            track = min(
                alive,
                key=lambda item: _distance(
                    current, minimum_enclosing_circle(item.polygon).center
                ),
            )
            self._localize_and_clear(env, track)

    def _localize_and_clear(self, env: Environment, track: ChannelTrack) -> None:
        if track.region_health is RegionHealth.INVALID or not track.polygon:
            raise EnvironmentStateError(
                f"信道 {track.channel} 没有经过认证的位置外包"
            )
        for _ in range(self.options.max_active_measurements):
            circle = minimum_enclosing_circle(track.polygon)
            if circle.radius <= self.options.guaranteed_clear_radius_m:
                if self._try_guaranteed_clear(env, track, circle.center):
                    return
                break

            candidate = self._choose_q2_candidate(env, track)
            if candidate is None:
                break
            result = self._measure_action(
                env, track, candidate, "active_localization"
            )
            track.active_measurements += 1
            if result.status is MeasureStatus.NO_SIGNAL:
                track.no_signal_during_localization += 1
                break
            self._handle_measurement(env, track, candidate, result)
            if track.status is ChannelStatus.CLEARED:
                return

        if track.status is not ChannelStatus.CLEARED:
            circle = minimum_enclosing_circle(track.polygon)
            if circle.radius <= self.options.clear_radius_m:
                if self._try_guaranteed_clear(env, track, circle.center):
                    return
            self._clear_by_grid(env, track)

    def _try_guaranteed_clear(
        self, env: Environment, track: ChannelTrack, point: Point
    ) -> bool:
        self._guaranteed_clear_attempts += 1
        result = self._clear_action(env, track, point, "guaranteed_center")
        if result.status is ClearStatus.SUCCESS:
            self._transition(track, ChannelStatus.CLEARED, "guaranteed_clear_success")
            return True
        return False

    def _choose_q2_candidate(
        self, env: Environment, track: ChannelTrack
    ) -> Point | None:
        if track.region_health is not RegionHealth.HEALTHY_CURRENT:
            return None
        if track.last_bearing_deg is None:
            return None
        current = _point(env.current_position)
        reference = FirstObservation(current, track.last_bearing_deg)
        candidates, circle = generate_sparse_candidates(
            reference,
            self._q2_config,
            track.polygon,
        )
        if not candidates:
            return None

        sources = _representative_polygon_points(
            track.polygon, self.options.q2_source_samples
        )
        errors = _error_grid(
            self.options.bearing_error_deg, self.options.q2_error_nodes
        )
        scores = [
            evaluate_candidate(
                candidate,
                "q3_sparse",
                reference,
                self._q2_config,
                track.polygon,
                sources,
                errors,
            )
            for candidate in candidates
        ]
        scores.sort(key=lambda score: _score_key(score, current, circle.center))

        slack = max(0.0, self._q2_config.receive_min - circle.radius)
        step = min(150.0, max(12.0, 0.4 * slack))
        directions = [
            (math.cos(index * math.pi / 4.0), math.sin(index * math.pi / 4.0))
            for index in range(8)
        ]
        best_scores: list[CandidateScore] = []
        for seed in scores[: self.options.q2_seed_count]:
            best = seed
            local_step = step
            for _ in range(self.options.q2_local_rounds):
                for dx, dy in directions:
                    point = (
                        best.point[0] + local_step * dx,
                        best.point[1] + local_step * dy,
                    )
                    if (
                        conservative_safety_margin(
                            point, track.polygon, self._q2_config.receive_min
                        )
                        < -1e-7
                    ):
                        continue
                    score = evaluate_candidate(
                        point,
                        "q3_local",
                        reference,
                        self._q2_config,
                        track.polygon,
                        sources,
                        errors,
                    )
                    if _score_key(score, current, circle.center) < _score_key(best, current, circle.center):
                        best = score
                local_step *= 0.5
            best_scores.append(best)

        best_scores.extend(scores[:3])
        best = min(best_scores, key=lambda score: _score_key(score, current, circle.center))
        return best.point

    def _clear_by_grid(self, env: Environment, track: ChannelTrack) -> None:
        if not track.polygon:
            return
        if track.region_health is RegionHealth.INVALID:
            raise EnvironmentStateError(
                f"信道 {track.channel} 不能使用未经认证的清除区域"
            )
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

        for row in range(rows):
            column_order = range(columns) if row % 2 == 0 else range(columns - 1, -1, -1)
            for column in column_order:
                u = min_u + (column + 0.5) * step
                v = min_v + (row + 0.5) * step
                point = (
                    origin[0] + u * ux + v * vx,
                    origin[1] + u * uy + v * vy,
                )
                self._fallback_clear_attempts += 1
                result = self._clear_action(env, track, point, "grid_fallback")
                if result.status is ClearStatus.SUCCESS:
                    self._transition(track, ChannelStatus.CLEARED, "grid_clear_success")
                    return


__all__ = [
    "AbsenceReason",
    "ChannelStatus",
    "ChannelTrack",
    "ClearEvent",
    "CompletionCertificate",
    "GuaranteedRollingQ3Strategy",
    "LifecycleEvent",
    "ObservationEvent",
    "Q3StrategyOptions",
    "RegionHealth",
    "SEARCH_ROUTE",
    "_fallback_initial_polygon",
    "search_cover_bound_m",
]
