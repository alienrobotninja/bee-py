from typing import NewType, Union

from bee_py.chunk.serialize import serialize_bytes
from bee_py.chunk.soc import make

TIMESTAMP_PAYLOAD_SIZE = 8
TIMESTAMP_PAYLOAD_SIZE_HEX = 16


IndexBytes = NewType("IndexBytes", bytes)


class Epoch:
    def __init__(self, time: int, level: int):
        self.time = time
        self.level = level


class Index:
    def __init__(self, value: Union[int, Epoch, bytes, str]):
        self._validate(value)
        self._value = value

    def _validate(self, value: Union[int, Epoch, bytes, str]):
        if not (
            isinstance(value, (int, Epoch))
            or (isinstance(value, bytes) and len(value) == TIMESTAMP_PAYLOAD_SIZE)
            or (
                isinstance(value, str)
                and len(value) == TIMESTAMP_PAYLOAD_SIZE_HEX
                and all(c in "0123456789abcdefABCDEF" for c in value)
            )
        ):
            msg = "Index must be an int, Epoch, 8-byte bytes, or a hex string of length 16"
            raise ValueError(msg)

    def __str__(self):
        return str(self._value)
