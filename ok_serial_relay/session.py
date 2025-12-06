"""Session-level protocol state"""

import logging
import msgspec

import ok_serial_relay.protocol as proto
import ok_serial_relay.timing

logger = logging.getLogger(__name__)

INCOMING_LINE_MAX = 131072


class Session:
    def __init__(
        self,
        *,
        when: float,
        profile: list[msgspec.Struct] = [],
    ) -> None:
        self._buffer_bytes = bytearray()
        self._buffer_time = 0.0
        self._local_profile = profile[:]
        self._time_tracker = ok_serial_relay.timing.TimeTracker(
            when=when,
            profile_id=hash(tuple(profile)),
            profile_len=len(profile),
        )

    def get_bytes_to_send(self, *, when: float, buffer_empty: bool) -> bytes:
        to_send: proto.Line | None = None
        if self._time_tracker.has_payload_to_send(when=when):
            if not buffer_empty:
                return b""  # priority buffer-empty for timed message
            if payload := self._time_tracker.get_payload_to_send(when=when):
                to_send = proto.line_from_payload(payload)

        if to_send:
            logger.debug("Sending: %s", to_send)
            return proto.line_to_bytes(to_send)
        else:
            return b""

    def on_bytes_received(self, data: bytes, *, when: float) -> None:
        while data:
            if not self._buffer_bytes:
                self._buffer_time = when
            if (newline_pos := data.find(b"\n")) >= 0:
                self._buffer_bytes.extend(data[:newline_pos])
                self._parse_buffered_line()
                self._buffer_bytes[:] = b""
                data = data[newline_pos + 1 :]
            else:
                self._buffer_bytes.extend(data)
                if len(self._buffer_bytes) >= INCOMING_LINE_MAX:
                    self._buffer_bytes[:] = b""
                return

    def _parse_buffered_line(self) -> None:
        if not (line := proto.try_parse_line(self._buffer_bytes)):
            return
        logger.debug("Received: %s", line)
        if qp := proto.try_decode_json(line, proto.TimeQueryPayload):
            self._time_tracker.on_query_received(qp, when=self._buffer_time)
        elif rp := proto.try_decode_json(line, proto.TimeReplyPayload):
            self._time_tracker.on_reply_received(rp, when=self._buffer_time)
