"""官方 Q3/Q4 模拟器的 HTTP+JSON 适配器。"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import json
import math
from pathlib import Path
import threading
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from radio_sim.domain.models import (
    ClearResult,
    ClearStatus,
    EnvironmentState,
    MeasureResult,
    MeasureStatus,
    Position,
)
from radio_sim.environment.base import EnvironmentStateError, InvalidActionError


class OfficialEnvironmentError(EnvironmentStateError):
    """使用官方模拟器时各类故障的基类。"""


class OfficialTransportError(OfficialEnvironmentError):
    """幂等重试后仍未获得可信的 HTTP 响应。"""


class OfficialHTTPError(OfficialEnvironmentError):
    """模拟器返回了非 200 的 HTTP 响应。"""

    def __init__(self, status_code: int, response: object) -> None:
        self.status_code = status_code
        self.response = response
        super().__init__(f"official simulator returned HTTP {status_code}: {response!r}")


class OfficialRejectedError(OfficialEnvironmentError):
    """模拟器返回 HTTP 200，但 accepted=false。"""

    def __init__(self, response: Mapping[str, Any]) -> None:
        self.response = dict(response)
        super().__init__(f"official simulator rejected the action: {dict(response)!r}")


class OfficialProtocolError(OfficialEnvironmentError):
    """响应不符合已公布的 JSON 结构。"""


class OfficialDeadlineError(OfficialEnvironmentError):
    """已触及现实时间预留边界，此时只应尝试退出。"""


class OfficialPendingRequestError(OfficialEnvironmentError):
    """先前请求的结果未知，必须优先重放该请求。"""


@dataclass(frozen=True, slots=True)
class _PendingRequest:
    action: str
    path: str
    payload: dict[str, Any]


def _json_without_duplicate_keys(raw: bytes) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise OfficialProtocolError("response is not UTF-8") from exc

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise OfficialProtocolError(f"response contains duplicate key {key!r}")
            result[key] = value
        return result

    try:
        value = json.loads(text, object_pairs_hook=pairs_hook)
    except OfficialProtocolError:
        raise
    except (json.JSONDecodeError, ValueError) as exc:
        raise OfficialProtocolError("response body is not valid JSON") from exc
    if not isinstance(value, dict):
        raise OfficialProtocolError("response JSON must be an object")
    return value


def _finite_number(payload: Mapping[str, Any], key: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise OfficialProtocolError(f"response field {key!r} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise OfficialProtocolError(f"response field {key!r} must be finite")
    return result


class OfficialEnvironment:
    """实现公开 ``Environment`` 协议的有状态适配器。

    每个公开动作都会创建一个新的请求 ID。传输重试完全在该动作内部完成，
    并复用完全相同的序列化请求体和 ID。
    """

    def __init__(
        self,
        robot_id: str,
        *,
        base_url: str = "http://127.0.0.1:2026",
        arena_id: str = "default",
        timeout_s: float = 5.0,
        max_retries: int = 2,
        retry_backoff_s: float = 0.2,
        exit_reserve_s: float = 15.0,
        log_path: str | Path | None = None,
        opener: Callable[..., Any] | None = None,
        monotonic: Callable[[], float] | None = None,
        sleeper: Callable[[float], None] | None = None,
    ) -> None:
        robot_bytes = robot_id.encode("utf-8")
        if not 1 <= len(robot_bytes) <= 64:
            raise ValueError("robot_id UTF-8 length must be in 1..64 bytes")
        if any(ord(character) < 32 or ord(character) == 127 for character in robot_id):
            raise ValueError("robot_id cannot contain control characters")
        if arena_id != "default":
            raise ValueError("arena_id must be 'default'")
        if timeout_s <= 0.0:
            raise ValueError("timeout_s must be positive")
        if max_retries < 0:
            raise ValueError("max_retries must be nonnegative")
        if retry_backoff_s < 0.0 or exit_reserve_s < 0.0:
            raise ValueError("retry_backoff_s and exit_reserve_s must be nonnegative")

        normalized_url = base_url.rstrip("/")
        if not normalized_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")

        self._robot_id = robot_id
        self._arena_id = arena_id
        self._base_url = normalized_url
        self._timeout_s = float(timeout_s)
        self._max_retries = int(max_retries)
        self._retry_backoff_s = float(retry_backoff_s)
        self._exit_reserve_s = float(exit_reserve_s)
        self._log_path = Path(log_path) if log_path is not None else None
        self._opener = opener or urlopen
        self._monotonic = monotonic or time.monotonic
        self._sleeper = sleeper or time.sleep
        self._action_lock = threading.Lock()

        self._position = Position(0.0, 0.0)
        self._channel = 1
        self._virtual_time_s = 0.0
        self._active = False
        self._finished = False
        self._request_counter = 0
        self._http_attempt_count = 0
        self._measure_count = 0
        self._clear_count = 0
        self._successful_clear_count = 0
        self._entered_remaining_real_duration_s: float | None = None
        self._real_deadline: float | None = None
        self._pending_request: _PendingRequest | None = None

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

    @property
    def entered_remaining_real_duration_s(self) -> float | None:
        return self._entered_remaining_real_duration_s

    @property
    def remaining_real_duration_s(self) -> float | None:
        if self._real_deadline is None:
            return None
        return max(0.0, self._real_deadline - self._monotonic())

    @property
    def request_count(self) -> int:
        return self._request_counter

    @property
    def http_attempt_count(self) -> int:
        return self._http_attempt_count

    @property
    def has_pending_request(self) -> bool:
        return self._pending_request is not None

    @property
    def pending_request(self) -> dict[str, object] | None:
        pending = self._pending_request
        if pending is None:
            return None
        return {
            "action": pending.action,
            "path": pending.path,
            "request_id": pending.payload["request_id"],
        }

    @property
    def measure_count(self) -> int:
        return self._measure_count

    @property
    def clear_count(self) -> int:
        return self._clear_count

    @property
    def successful_clear_count(self) -> int:
        return self._successful_clear_count

    def enter(self) -> EnvironmentState:
        if self._active or self._finished:
            raise EnvironmentStateError("enter may be called exactly once")
        self._require_no_pending_request()
        with self._exclusive_action():
            payload = self._base_payload("enter")
            return self._execute_new_request("enter", "/enter", payload)

    def measure(self, position: Position, channel: int) -> MeasureResult:
        self._require_active()
        self._require_no_pending_request()
        self._require_real_time_for_action()
        position, channel = self._validate_action(position, channel)
        with self._exclusive_action():
            payload = self._action_payload("measure", position, channel)
            return self._execute_new_request("measure", "/measure", payload)

    def clear(self, position: Position, channel: int) -> ClearResult:
        self._require_active()
        self._require_no_pending_request()
        self._require_real_time_for_action()
        position, channel = self._validate_action(position, channel)
        with self._exclusive_action():
            payload = self._action_payload("clear", position, channel)
            return self._execute_new_request("clear", "/clear", payload)

    def exit(self) -> EnvironmentState:
        self._require_active()
        self._require_no_pending_request()
        with self._exclusive_action():
            payload = self._base_payload("exit")
            return self._execute_new_request("exit", "/exit", payload)

    def recover_pending(self) -> EnvironmentState | MeasureResult | ClearResult:
        """原样重放未决请求，不创建新的请求 ID。"""
        if self._pending_request is None:
            raise OfficialPendingRequestError("there is no pending request to recover")
        with self._exclusive_action():
            return self._complete_pending_request()

    def _execute_new_request(
        self,
        action: str,
        path: str,
        payload: Mapping[str, Any],
    ) -> EnvironmentState | MeasureResult | ClearResult:
        self._pending_request = _PendingRequest(action, path, dict(payload))
        return self._complete_pending_request()

    def _complete_pending_request(self) -> EnvironmentState | MeasureResult | ClearResult:
        pending = self._pending_request
        if pending is None:
            raise OfficialPendingRequestError("there is no pending request to complete")
        try:
            response = self._post(pending.path, pending.payload)
            result = self._apply_response(pending, response)
        except (OfficialHTTPError, OfficialRejectedError):
            # 完整的拒绝响应可以证明该动作未被执行。
            self._pending_request = None
            raise
        except (OfficialTransportError, OfficialProtocolError):
            # 服务器可能已经执行该动作，因此保留原始请求以便重放。
            raise
        self._pending_request = None
        return result

    def _apply_response(
        self,
        pending: _PendingRequest,
        response: Mapping[str, Any],
    ) -> EnvironmentState | MeasureResult | ClearResult:
        action = pending.action
        if action == "enter":
            virtual_time = self._accepted_virtual_time(response)
            max_virtual = _finite_number(response, "max_virtual_duration_s")
            max_real = _finite_number(response, "max_real_duration_s")
            remaining = _finite_number(response, "remaining_real_duration_s")
            if max_virtual <= 0.0 or max_real <= 0.0 or not 0.0 <= remaining <= max_real:
                raise OfficialProtocolError("invalid duration values in /enter response")
            self._position = Position(0.0, 0.0)
            self._channel = 1
            self._virtual_time_s = virtual_time
            self._entered_remaining_real_duration_s = remaining
            self._real_deadline = self._monotonic() + remaining
            self._active = True
            return self.state

        if action == "exit":
            virtual_time = self._accepted_virtual_time(response)
            if response.get("exit_reason") != "user_exit":
                raise OfficialProtocolError("accepted /exit must return user_exit")
            self._virtual_time_s = virtual_time
            self._active = False
            self._finished = True
            return self.state

        raw_position = pending.payload["position"]
        assert isinstance(raw_position, Mapping)
        position = Position(float(raw_position["x"]), float(raw_position["y"]))
        channel = int(pending.payload["channel"])
        new_virtual_time = self._accepted_virtual_time(response)

        if action == "measure":
            raw_status = response.get("measure_result")
            try:
                status = MeasureStatus(raw_status)
            except (TypeError, ValueError) as exc:
                raise OfficialProtocolError(
                    f"invalid measure_result {raw_status!r}"
                ) from exc
            angle: float | None = None
            if status is MeasureStatus.DIRECTION:
                angle = _finite_number(response, "svd_deg")
                if not 0.0 <= angle < 360.0:
                    raise OfficialProtocolError("svd_deg must lie in [0, 360)")
            elif "svd_deg" in response:
                raise OfficialProtocolError("svd_deg is only valid for direction responses")
            action_time = self._time_increment(new_virtual_time)
            self._position = position
            self._channel = channel
            self._virtual_time_s = new_virtual_time
            self._measure_count += 1
            return MeasureResult(status, angle, action_time, new_virtual_time)

        if action == "clear":
            raw_status = response.get("clear_result")
            try:
                status = ClearStatus(raw_status)
            except (TypeError, ValueError) as exc:
                raise OfficialProtocolError(f"invalid clear_result {raw_status!r}") from exc
            action_time = self._time_increment(new_virtual_time)
            self._position = position
            self._virtual_time_s = new_virtual_time
            self._clear_count += 1
            if status is ClearStatus.SUCCESS:
                self._successful_clear_count += 1
            return ClearResult(status, action_time, new_virtual_time)

        raise OfficialProtocolError(f"unknown pending action {action!r}")

    def _base_payload(self, action: str) -> dict[str, Any]:
        return {
            "arena_id": self._arena_id,
            "robot_id": self._robot_id,
            "request_id": self._next_request_id(action),
        }

    def _action_payload(
        self, action: str, position: Position, channel: int
    ) -> dict[str, Any]:
        payload = self._base_payload(action)
        payload["position"] = {"x": position.x, "y": position.y}
        payload["channel"] = channel
        return payload

    def _next_request_id(self, action: str) -> str:
        self._request_counter += 1
        request_id = f"{action}-{self._request_counter:06d}"
        if len(request_id.encode("utf-8")) > 128:
            raise RuntimeError("generated request_id exceeds protocol limit")
        return request_id

    def _post(self, path: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        body = json.dumps(
            dict(payload),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(body) > 65536:
            raise InvalidActionError("request body exceeds 65536 bytes")

        last_error: BaseException | None = None
        for attempt in range(self._max_retries + 1):
            self._http_attempt_count += 1
            request = Request(
                self._base_url + path,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            self._write_log(
                {
                    "event": "request",
                    "attempt": attempt + 1,
                    "path": path,
                    "payload": dict(payload),
                }
            )
            try:
                with self._opener(request, timeout=self._timeout_s) as http_response:
                    status_code = int(getattr(http_response, "status", 200))
                    raw_response = http_response.read()
            except HTTPError as exc:
                status_code = int(exc.code)
                raw_response = exc.read()
                response = self._safe_parse_error(raw_response)
                self._write_log(
                    {
                        "event": "http_error",
                        "attempt": attempt + 1,
                        "path": path,
                        "status_code": status_code,
                        "response": response,
                    }
                )
                if status_code in (429, 500) and attempt < self._max_retries:
                    self._retry_pause(attempt)
                    continue
                raise OfficialHTTPError(status_code, response) from exc
            except (URLError, TimeoutError, OSError) as exc:
                last_error = exc
                self._write_log(
                    {
                        "event": "transport_error",
                        "attempt": attempt + 1,
                        "path": path,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
                if attempt < self._max_retries:
                    self._retry_pause(attempt)
                    continue
                break

            response = _json_without_duplicate_keys(raw_response)
            self._write_log(
                {
                    "event": "response",
                    "attempt": attempt + 1,
                    "path": path,
                    "status_code": status_code,
                    "response": response,
                }
            )
            if status_code != 200:
                raise OfficialHTTPError(status_code, response)
            self._validate_envelope(response)
            if response["accepted"] is not True:
                raise OfficialRejectedError(response)
            return response

        self._write_log(
            {
                "event": "pending_request",
                "path": path,
                "request_id": payload["request_id"],
                "attempt_count": self._max_retries + 1,
            }
        )
        raise OfficialTransportError(
            f"no response for {path} after {self._max_retries + 1} attempts; "
            f"the same request_id was reused: {payload['request_id']!r}"
        ) from last_error

    def _validate_envelope(self, response: Mapping[str, Any]) -> None:
        if type(response.get("accepted")) is not bool:
            raise OfficialProtocolError("accepted must be a JSON boolean")
        _finite_number(response, "real_timestamp_ms")
        _finite_number(response, "virtual_time_s")

    def _accepted_virtual_time(self, response: Mapping[str, Any]) -> float:
        self._validate_envelope(response)
        value = _finite_number(response, "virtual_time_s")
        if value + 1e-9 < self._virtual_time_s:
            raise OfficialProtocolError("accepted virtual_time_s moved backwards")
        return value

    def _time_increment(self, new_virtual_time: float) -> float:
        increment = new_virtual_time - self._virtual_time_s
        if increment < -1e-9:
            raise OfficialProtocolError("virtual_time_s moved backwards")
        return max(0.0, increment)

    def _require_active(self) -> None:
        if not self._active:
            raise EnvironmentStateError("environment is not active; call enter first")

    def _require_no_pending_request(self) -> None:
        pending = self._pending_request
        if pending is not None:
            raise OfficialPendingRequestError(
                "request outcome is unresolved; call recover_pending() before sending "
                f"a new action (pending {pending.action} id={pending.payload['request_id']!r})"
            )

    def _require_real_time_for_action(self) -> None:
        remaining = self.remaining_real_duration_s
        if remaining is not None and remaining <= self._exit_reserve_s:
            raise OfficialDeadlineError(
                f"only {remaining:.3f}s remain; preserving time for /exit"
            )

    def _validate_action(self, position: Position, channel: int) -> tuple[Position, int]:
        if not isinstance(position, Position):
            raise InvalidActionError("position must be a Position instance")
        if abs(position.x) > 2_000_000.0 or abs(position.y) > 2_000_000.0:
            raise InvalidActionError("position coordinate exceeds simulator limit")
        if isinstance(channel, bool) or not isinstance(channel, int) or not 1 <= channel <= 20:
            raise InvalidActionError("channel must be an integer in 1..20")
        return position, channel

    def _retry_pause(self, attempt: int) -> None:
        delay = self._retry_backoff_s * (2**attempt)
        remaining = self.remaining_real_duration_s
        if remaining is not None:
            delay = min(delay, max(0.0, remaining - self._exit_reserve_s))
        if delay > 0.0:
            self._sleeper(delay)

    def _safe_parse_error(self, raw: bytes) -> object:
        try:
            return _json_without_duplicate_keys(raw)
        except OfficialProtocolError:
            return raw.decode("utf-8", errors="replace")

    def _write_log(self, record: Mapping[str, Any]) -> None:
        if self._log_path is None:
            return
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        enriched = {
            "local_timestamp_ms": int(time.time() * 1000),
            **dict(record),
        }
        with self._log_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(enriched, ensure_ascii=False, allow_nan=False))
            handle.write("\n")

    class _ActionContext:
        def __init__(self, lock: threading.Lock) -> None:
            self._lock = lock

        def __enter__(self) -> None:
            if not self._lock.acquire(blocking=False):
                raise OfficialEnvironmentError(
                    "different actions may not be sent concurrently"
                )

        def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
            self._lock.release()

    def _exclusive_action(self) -> _ActionContext:
        return self._ActionContext(self._action_lock)


__all__ = [
    "OfficialDeadlineError",
    "OfficialEnvironment",
    "OfficialEnvironmentError",
    "OfficialHTTPError",
    "OfficialPendingRequestError",
    "OfficialProtocolError",
    "OfficialRejectedError",
    "OfficialTransportError",
]
