"""Present Foxglove JSON schemas as bytes"""

import functools
import importlib.resources

_PACKAGE_NAME = "ok_serial_relay.foxglove_jsonschema"


@functools.cache
def get(name: str) -> bytes:
    try:
        return importlib.resources.read_binary(_PACKAGE_NAME, f"{name}.json")
    except FileNotFoundError:
        return b""
