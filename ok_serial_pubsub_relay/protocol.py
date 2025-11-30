"""Basic serial-line protocol definitions"""

import anycrc
import logging
import msgspec
import re

class Line(msgspec.Struct):
    """Basic unit of serial port exchange"""

    label: str
    value: object


_logger = logging.getLogger(__name__)

# https://reveng.sourceforge.io/crc-catalogue/16.htm#crc.cat.crc-16-opensafety-b
# https://users.ece.cmu.edu/~koopman/crc/c16/0xbaad_len.txt
_crc16 = anycrc.Model("CRC16-OPENSAFETY-B")

_LABEL_RE = re.compile(b"\w*")
_LINE_RE = re.compile(b"\s*(\w*)(\W.*\W)([0-9A-Fa-f]{4}|!CRC)\s*")


def line_from_bytes(data: bytes) -> Line | None:
    match = _LINE_RE.fullmatch(data)
    if not match:
        return None
    label, json, check = match.groups()
    if check != "!CRC":
        message_crc = int(check, 16)
        actual_crc = _crc16.calc(label + json)
        if message_crc != actual_crc:
            return None
    try:
        msgspec.json.decode(json)
    except msgspec.DecodeError:
        return None


def line_to_bytes(line: Line) -> bytes:
    assert _LABEL_RE.fullmatch(line.label)
    json = msgspec.json.encode(line.value)
    if json[0] in b'"[{':
        body = line.label + json
    else:
        body = line.label + b" " + json + b" "
    return b"%s%04x" % (body, _crc16.calc(body))
