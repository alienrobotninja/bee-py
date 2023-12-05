import io
from typing import Union


def prepare_websocket_data(data: Union[str, bytes, bytearray, memoryview]) -> bytes:
    if isinstance(data, str):
        return data.encode()

    if isinstance(data, (bytes, bytearray, memoryview)):
        return bytes(data)

    if isinstance(data, io.IOBase):
        # Read the data from the file-like object
        return data.read()

    msg = "Unknown websocket data type"
    raise TypeError(msg)
