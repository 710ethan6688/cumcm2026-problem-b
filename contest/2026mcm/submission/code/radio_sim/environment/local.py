from __future__ import annotations

from dataclasses import dataclass

from radio_sim.domain.models import (
    ClearResult,
    ClearStatus,
    EnvironmentState,
    MeasureResult,
    MeasureStatus,
    Position,
    ProblemType,
)
from radio_sim.environment.base import EnvironmentStateError, InvalidActionError
from radio_sim.scenario.config import ScenarioConfig
from radio_sim.scenario.generator import ScenarioGenerator
from radio_sim.scenario.models import Scenario, Source, SourceType
from radio_sim.utils.deterministic_noise import measurement_error_deg
from radio_sim.utils.geometry import bearing_deg, distance, in_directional_coverage


@dataclass(frozen=True, slots=True)
class PhysicsConfig:
    movement_speed_mps: float = 5.0
    channel_switch_time_s: float = 1.0
    measurement_time_s: float = 5.0
    failed_clear_time_s: float = 3.0
    successful_clear_time_s: float = 5.0
    near_distance_m: float = 5.0
    clear_distance_m: float = 20.0
    directional_half_angle_deg: float = 90.0
    coordinate_limit_m: float = 2_000_000.0
    max_virtual_duration_s: float = 360_000.0
    angle_decimal_places: int = 2

    def __post_init__(self) -> None:
        positive_fields = (
            self.movement_speed_mps,
            self.measurement_time_s,
            self.failed_clear_time_s,
            self.successful_clear_time_s,
            self.near_distance_m,
            self.clear_distance_m,
            self.coordinate_limit_m,
            self.max_virtual_duration_s,
        )
        if any(value <= 0 for value in positive_fields):
            raise ValueError("physics distances, durations, limits, and speed must be positive")
        if self.channel_switch_time_s < 0:
            raise ValueError("channel switch time cannot be negative")
        if not 0 < self.directional_half_angle_deg <= 180:
            raise ValueError("directional half angle must be in (0, 180]")
        if self.angle_decimal_places < 0:
            raise ValueError("angle_decimal_places cannot be negative")


@dataclass(frozen=True, slots=True)
class _EvaluationSnapshot:
    total_distance_m: float
    measure_count: int
    clear_count: int
    failed_clear_count: int
    channel_switch_count: int
    cleared_count: int
    source_count: int
    timed_out: bool


class LocalEnvironment:

    def __init__(
        self,
        scenario: Scenario,
        physics: PhysicsConfig | None = None,
    ) -> None:
        self._seed = scenario.seed
        self._sources_by_channel = scenario.source_by_channel()
        self._physics = physics or PhysicsConfig()
        self._cleared_channels: set[int] = set()
        self._position = Position(0.0, 0.0)
        self._channel = 1
        self._virtual_time_s = 0.0
        self._active = False
        self._finished = False
        self._timed_out = False
        self._total_distance_m = 0.0
        self._measure_count = 0
        self._clear_count = 0
        self._failed_clear_count = 0
        self._channel_switch_count = 0

    @classmethod
    def from_seed(
        cls,
        seed: int,
        problem: ProblemType | str,
        scenario_config: ScenarioConfig | None = None,
        physics: PhysicsConfig | None = None,
    ) -> "LocalEnvironment":
        problem_type = ProblemType.coerce(problem)
        config = scenario_config or ScenarioConfig.for_problem(problem_type)
        if config.problem is not problem_type:
            config = config.with_problem(problem_type)
        scenario = ScenarioGenerator().generate(seed=seed, config=config)
        return cls(scenario=scenario, physics=physics)

    @property
    def state(self) -> EnvironmentState:
        return EnvironmentState(
            current_position=self._position,
            current_channel=self._channel,
            virtual_time_s=self._virtual_time_s,
            is_active=self._active,
            is_finished=self._finished,
        )

    @property
    def current_position(self) -> Position:
        return self._position

    @property
    def current_channel(self) -> int:
        return self._channel

    @property
    def virtual_time_s(self) -> float:
        return self._virtual_time_s

    def _evaluation_snapshot(self) -> _EvaluationSnapshot:
        return _EvaluationSnapshot(
            total_distance_m=self._total_distance_m,
            measure_count=self._measure_count,
            clear_count=self._clear_count,
            failed_clear_count=self._failed_clear_count,
            channel_switch_count=self._channel_switch_count,
            cleared_count=len(self._cleared_channels),
            source_count=len(self._sources_by_channel),
            timed_out=self._timed_out,
        )

    def enter(self) -> EnvironmentState:
        if self._active or self._finished:
            raise EnvironmentStateError("enter may be called exactly once")
        self._active = True
        return self.state

    def exit(self) -> EnvironmentState:
        self._require_active()
        self._active = False
        self._finished = True
        return self.state

    def measure(self, position: Position, channel: int) -> MeasureResult:
        self._require_active()
        position, channel = self._validate_action(position, channel)

        move_distance = distance(self._position, position)
        switched = channel != self._channel
        action_time = (
            move_distance / self._physics.movement_speed_mps
            + self._physics.measurement_time_s
            + (self._physics.channel_switch_time_s if switched else 0.0)
        )
        self._advance_position(position, move_distance, action_time)
        self._channel = channel
        self._measure_count += 1
        if switched:
            self._channel_switch_count += 1

        source = self._available_source(channel)
        if source is None or not self._can_receive(source, position):
            result = MeasureResult(
                status=MeasureStatus.NO_SIGNAL,
                angle_deg=None,
                action_time_s=action_time,
                virtual_time_s=self._virtual_time_s,
            )
        else:
            source_distance = distance(position, source.position)
            if source_distance <= self._physics.near_distance_m:
                result = MeasureResult(
                    status=MeasureStatus.NEAR,
                    angle_deg=None,
                    action_time_s=action_time,
                    virtual_time_s=self._virtual_time_s,
                )
            else:
                true_bearing = bearing_deg(position, source.position)
                noisy_bearing = (
                    true_bearing
                    + measurement_error_deg(self._seed, channel, position)
                ) % 360.0
                result = MeasureResult(
                    status=MeasureStatus.DIRECTION,
                    angle_deg=round(noisy_bearing, self._physics.angle_decimal_places) % 360.0,
                    action_time_s=action_time,
                    virtual_time_s=self._virtual_time_s,
                )

        self._finish_if_timed_out()
        return result

    def clear(self, position: Position, channel: int) -> ClearResult:
        self._require_active()
        position, channel = self._validate_action(position, channel)

        move_distance = distance(self._position, position)
        source = self._available_source(channel)
        success = (
            source is not None
            and distance(position, source.position) <= self._physics.clear_distance_m
        )
        clear_time = (
            self._physics.successful_clear_time_s
            if success
            else self._physics.failed_clear_time_s
        )
        action_time = move_distance / self._physics.movement_speed_mps + clear_time
        self._advance_position(position, move_distance, action_time)
        self._clear_count += 1

        if success:
            self._cleared_channels.add(channel)
            status = ClearStatus.SUCCESS
        else:
            self._failed_clear_count += 1
            status = ClearStatus.NO_TARGET_IN_RANGE

        result = ClearResult(
            status=status,
            action_time_s=action_time,
            virtual_time_s=self._virtual_time_s,
        )
        self._finish_if_timed_out()
        return result

    def _available_source(self, channel: int) -> Source | None:
        if channel in self._cleared_channels:
            return None
        return self._sources_by_channel.get(channel)

    def _can_receive(self, source: Source, receiver: Position) -> bool:
        if distance(source.position, receiver) > source.receive_radius_m:
            return False
        if source.source_type is SourceType.OMNIDIRECTIONAL:
            return True
        assert source.direction_deg is not None
        return in_directional_coverage(
            source_position=source.position,
            source_direction_deg=source.direction_deg,
            receiver_position=receiver,
            half_angle_deg=self._physics.directional_half_angle_deg,
        )

    def _validate_action(self, position: Position, channel: int) -> tuple[Position, int]:
        if not isinstance(position, Position):
            raise InvalidActionError("position must be a Position instance")
        if abs(position.x) > self._physics.coordinate_limit_m or abs(position.y) > self._physics.coordinate_limit_m:
            raise InvalidActionError("position coordinate exceeds simulator limit")
        if isinstance(channel, bool) or not isinstance(channel, int) or not 1 <= channel <= 20:
            raise InvalidActionError("channel must be an integer in 1..20")
        return position, channel

    def _require_active(self) -> None:
        if not self._active:
            if self._timed_out:
                raise EnvironmentStateError("environment ended at the virtual-time limit")
            raise EnvironmentStateError("environment is not active; call enter first")

    def _advance_position(
        self,
        position: Position,
        move_distance: float,
        action_time_s: float,
    ) -> None:
        self._position = position
        self._total_distance_m += move_distance
        self._virtual_time_s += action_time_s

    def _finish_if_timed_out(self) -> None:
        if self._virtual_time_s >= self._physics.max_virtual_duration_s:
            self._timed_out = True
            self._active = False
            self._finished = True
