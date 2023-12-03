from typing import Union

from eth_utils import keccak

# from bee_py.utils.hex import bytes_to_hex


def keccak256_hash(*messages: Union[bytes, bytearray]) -> bytes:
    """
    Helper function for calculating the keccak256 hash with

    @param messages Any number of messages (bytes, byte arrays)
    returns bytes
    """
    combined = bytearray()
    for message in messages:
        if not isinstance(message, bytearray) and not isinstance(message, bytes):
            msg = f"Input should be either a string, bytes or bytearray: got {type(message)}."
            raise ValueError(msg)
        combined += message

    return keccak(combined)


if __name__ == "__main__":
    l = bytes([1, 2, 3])  # noqa: E741
    p = bytes([4, 5, 6])
    _hash = keccak256_hash(l, p)
    print(_hash)  # noqa: T201
