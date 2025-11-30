"""Unit tests for ok_serial_pubsub_relay.protocol"""

import ok_serial_pubsub_relay.protocol as proto

def test_line_to_bytes():
    assert proto.line_to_bytes(proto.Line("LABEL", [1,2,{"x": 3}])) == ""
