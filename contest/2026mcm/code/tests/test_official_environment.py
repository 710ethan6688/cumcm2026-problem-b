from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from urllib.error import HTTPError, URLError

from radio_sim.domain.models import ClearStatus, MeasureStatus, Position
from radio_sim.environment.official import (
    OfficialEnvironment,
    OfficialHTTPError,
    OfficialPendingRequestError,
    OfficialRejectedError,
    OfficialTransportError,
)


class FakeResponse:
    def __init__(self, payload: dict[str, object], status: int = 200) -> None:
        self.status = status
        self._body = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


class SequenceOpener:
    def __init__(self, *items: object) -> None:
        self.items = list(items)
        self.calls: list[tuple[str, bytes, dict[str, str]]] = []

    def __call__(self, request: object, timeout: float) -> FakeResponse:
        self.calls.append(
            (
                request.full_url,
                request.data,
                dict(request.header_items()),
            )
        )
        item = self.items.pop(0)
        if isinstance(item, BaseException):
            raise item
        return FakeResponse(item)


ENTER = {
    "accepted": True,
    "real_timestamp_ms": 1760000000000,
    "virtual_time_s": 0,
    "max_virtual_duration_s": 360000,
    "max_real_duration_s": 1200,
    "remaining_real_duration_s": 1200,
}



def make_http_error(status_code: int) -> HTTPError:
    payload = {
        "accepted": False,
        "real_timestamp_ms": 1760000000000,
        "virtual_time_s": 0,
    }
    return HTTPError(
        url="http://127.0.0.1:2026/enter",
        code=status_code,
        msg="test error",
        hdrs=None,
        fp=BytesIO(json.dumps(payload).encode("utf-8")),
    )

class OfficialEnvironmentTests(unittest.TestCase):
    def test_full_flow_maps_protocol_and_preserves_measurement_channel(self) -> None:
        opener = SequenceOpener(
            ENTER,
            {
                "accepted": True,
                "real_timestamp_ms": 1760000000100,
                "virtual_time_s": 105,
                "measure_result": "direction",
                "svd_deg": 123.45,
            },
            {
                "accepted": True,
                "real_timestamp_ms": 1760000000200,
                "virtual_time_s": 188,
                "clear_result": "success",
            },
            {
                "accepted": True,
                "real_timestamp_ms": 1760000000300,
                "virtual_time_s": 188,
                "exit_reason": "user_exit",
            },
        )
        env = OfficialEnvironment("team-123", opener=opener, sleeper=lambda _: None)

        state = env.enter()
        self.assertTrue(state.is_active)
        measured = env.measure(Position(300.0, 400.0), 2)
        self.assertIs(measured.status, MeasureStatus.DIRECTION)
        self.assertEqual(measured.angle_deg, 123.45)
        self.assertEqual(measured.action_time_s, 105.0)
        self.assertEqual(env.current_channel, 2)

        cleared = env.clear(Position(300.0, 0.0), 7)
        self.assertIs(cleared.status, ClearStatus.SUCCESS)
        self.assertEqual(cleared.action_time_s, 83.0)
        self.assertEqual(env.current_channel, 2)
        self.assertEqual(env.successful_clear_count, 1)

        final_state = env.exit()
        self.assertTrue(final_state.is_finished)
        self.assertFalse(final_state.is_active)
        self.assertEqual([call[0].rsplit("/", 1)[-1] for call in opener.calls], ["enter", "measure", "clear", "exit"])

        bodies = [json.loads(call[1].decode("utf-8")) for call in opener.calls]
        request_ids = [body["request_id"] for body in bodies]
        self.assertEqual(len(request_ids), len(set(request_ids)))
        self.assertEqual(set(bodies[0]), {"arena_id", "robot_id", "request_id"})
        self.assertEqual(
            set(bodies[1]),
            {"arena_id", "robot_id", "request_id", "position", "channel"},
        )
        self.assertEqual(opener.calls[0][2]["Content-type"], "application/json")

    def test_transport_retry_reuses_identical_request_id_and_body(self) -> None:
        opener = SequenceOpener(URLError("temporary disconnect"), ENTER)
        env = OfficialEnvironment(
            "team-123",
            opener=opener,
            max_retries=1,
            sleeper=lambda _: None,
        )
        env.enter()
        self.assertEqual(len(opener.calls), 2)
        self.assertEqual(opener.calls[0][0], opener.calls[1][0])
        self.assertEqual(opener.calls[0][1], opener.calls[1][1])

    def test_exhausted_transport_request_is_retained_and_recovered(self) -> None:
        recovered_measure = {
            "accepted": True,
            "real_timestamp_ms": 1760000000100,
            "virtual_time_s": 5,
            "measure_result": "no_signal",
        }
        opener = SequenceOpener(
            ENTER,
            URLError("first timeout"),
            URLError("second timeout"),
            recovered_measure,
        )
        env = OfficialEnvironment(
            "team-123",
            opener=opener,
            max_retries=1,
            sleeper=lambda _: None,
        )
        env.enter()

        with self.assertRaises(OfficialTransportError):
            env.measure(Position(10.0, 20.0), 3)
        self.assertTrue(env.has_pending_request)
        self.assertEqual(env.pending_request["action"], "measure")

        with self.assertRaises(OfficialPendingRequestError):
            env.clear(Position(0.0, 0.0), 3)
        with self.assertRaises(OfficialPendingRequestError):
            env.exit()

        recovered = env.recover_pending()
        self.assertIs(recovered.status, MeasureStatus.NO_SIGNAL)
        self.assertFalse(env.has_pending_request)
        self.assertEqual(env.current_position, Position(10.0, 20.0))
        self.assertEqual(env.current_channel, 3)

        request_bodies = [call[1] for call in opener.calls[1:]]
        self.assertEqual(len(request_bodies), 3)
        self.assertTrue(all(body == request_bodies[0] for body in request_bodies))

    def test_rejected_action_does_not_reset_virtual_time_or_state(self) -> None:
        opener = SequenceOpener(
            ENTER,
            {
                "accepted": True,
                "real_timestamp_ms": 1760000000100,
                "virtual_time_s": 5,
                "measure_result": "no_signal",
            },
            {
                "accepted": False,
                "real_timestamp_ms": 1760000000200,
                "virtual_time_s": 0,
            },
        )
        env = OfficialEnvironment("team-123", opener=opener, sleeper=lambda _: None)
        env.enter()
        env.measure(Position(0.0, 0.0), 1)
        with self.assertRaises(OfficialRejectedError):
            env.measure(Position(50.0, 0.0), 2)
        self.assertEqual(env.virtual_time_s, 5.0)
        self.assertEqual(env.current_position, Position(0.0, 0.0))
        self.assertEqual(env.current_channel, 1)


    def test_fatal_http_statuses_are_reported_without_retry(self) -> None:
        for status_code in (400, 404, 405, 409, 413, 415):
            with self.subTest(status_code=status_code):
                opener = SequenceOpener(make_http_error(status_code))
                env = OfficialEnvironment(
                    "team-123",
                    opener=opener,
                    max_retries=3,
                    sleeper=lambda _: None,
                )
                with self.assertRaises(OfficialHTTPError) as context:
                    env.enter()
                self.assertEqual(context.exception.status_code, status_code)
                self.assertEqual(len(opener.calls), 1)

    def test_transient_http_statuses_retry_with_the_same_body(self) -> None:
        for status_code in (429, 500):
            with self.subTest(status_code=status_code):
                opener = SequenceOpener(make_http_error(status_code), ENTER)
                env = OfficialEnvironment(
                    "team-123",
                    opener=opener,
                    max_retries=1,
                    sleeper=lambda _: None,
                )
                env.enter()
                self.assertEqual(len(opener.calls), 2)
                self.assertEqual(opener.calls[0][1], opener.calls[1][1])

    def test_jsonl_log_records_requests_and_responses(self) -> None:
        with TemporaryDirectory() as directory:
            log_path = Path(directory) / "official.jsonl"
            opener = SequenceOpener(ENTER)
            env = OfficialEnvironment(
                "team-123",
                opener=opener,
                sleeper=lambda _: None,
                log_path=log_path,
            )
            env.enter()
            records = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual([record["event"] for record in records], ["request", "response"])
            self.assertEqual(records[0]["payload"]["request_id"], "enter-000001")


if __name__ == "__main__":
    unittest.main()
