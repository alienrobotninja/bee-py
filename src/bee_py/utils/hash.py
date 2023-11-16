from typing import Union

from eth_utils import keccak
from hexbytes import HexBytes

#! Don't need this


def keccak256_hash(*messages: Union[str, bytes, bytearray]) -> HexBytes:
    """
    Helper function for calculating the keccak256 hash with

    @param messages Any number of messages (strings, byte arrays etc.)
    """

    hashes = []
    for message in messages:
        if isinstance(message, str):
            hashes.append(keccak(text=message))
        elif isinstance(message, bytes):
            hashes.append(keccak(hexstr=message.hex()))
        elif not isinstance(message, bytearray):
            msg = "Input should be either a string or bytes"
            raise ValueError(msg)

    # Concatenate the bytes objects
    result = b"".join(hashes)
    return HexBytes(keccak(result))
