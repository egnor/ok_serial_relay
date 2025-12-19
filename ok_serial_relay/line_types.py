"""Basic serial-line protocol definitions"""

import msgspec


class Line(msgspec.Struct, frozen=True):
    prefix: bytes
    payload: msgspec.Raw  # JSON contents


#
# payload types embedded in Line.payload
#


class MessagePayload(msgspec.Struct, array_like=True, omit_defaults=True):
    PREFIX = b""
    topic: str
    body: msgspec.Raw  # JSON message body
    msec: int = 0
    schema_name: str = ""


class ProfileStartPayload(msgspec.Struct, array_like=True, omit_defaults=True):
    PREFIX = b"Ps"
    id: int = 0
    entries: int = 0
    firmware: str = ""
    version: str = ""
    mode: str = ""


class ProfileEntryPayload(msgspec.Struct, array_like=True):
    PREFIX = b"Pe"
    seq: int
    entry: msgspec.Raw


class TimeQueryPayload(msgspec.Struct, array_like=True):
    PREFIX = b"Tq"
    yyyymmdd: int
    hhmmssmmm: int
    ack_profile_id: int = 0
    ack_profile_seq: int = 0


class TimeReplyPayload(msgspec.Struct, array_like=True):
    PREFIX = b"Tr"
    yyyymmdd: int
    hhmmssmmm: int
    rx_msec: int
    tx_msec: int


#
# profile entry types embedded in ProfileEntryPayload.entry
#
