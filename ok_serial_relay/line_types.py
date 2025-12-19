"""Basic serial-line protocol definitions"""

import msgspec


class Line(msgspec.Struct, frozen=True):
    prefix: bytes
    payload: msgspec.Raw  # JSON contents


#
# payload types embedded in Line.payload
#


class PayloadBase(msgspec.Struct, array_like=True, omit_defaults=True):
    PREFIX = b"~undefined~"


class PublishPayload(PayloadBase):
    PREFIX = b""
    topic: str
    body: msgspec.Raw  # JSON message body
    msec: int = 0
    schema_name: str = ""


class ProfileStartPayload(PayloadBase):
    PREFIX = b"P"
    profile_id: int = 0
    entries: int = 0
    firmware: str = ""
    version: str = ""
    mode: str = ""


class ProfileEntryBase(PayloadBase):
    entry_seq: int


class PublishRuleEntry(ProfileEntryBase):
    PREFIX = b"Pp"
    rule_prefix: str
    topic: str
    rewrite: msgspec.Raw


class SubscribeRuleEntry(ProfileEntryBase):
    PREFIX = b"Ps"
    topic: str
    rule_prefix: str
    rewrite: msgspec.Raw


class TimeQueryPayload(PayloadBase):
    PREFIX = b"Tq"
    yyyymmdd: int
    hhmmssmmm: int
    ack_profile_id: int = 0
    ack_entry_seq: int = 0


class TimeReplyPayload(PayloadBase):
    PREFIX = b"Tr"
    yyyymmdd: int
    hhmmssmmm: int
    rx_msec: int
    tx_msec: int
