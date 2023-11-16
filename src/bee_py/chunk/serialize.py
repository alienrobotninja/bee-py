from collections.abc import ByteString, Sequence
from itertools import chain


def serialize_bytes(*arrays: Sequence[ByteString]) -> ByteString:
    """
    Serializes a sequence of byte arrays into a single byte array.

    Args:
        *arrays (Sequence[ByteString]): The sequence of byte arrays to serialize.

    Returns:
        ByteString: The serialized byte array.
    """
    flattened_bytes = chain.from_iterable(arrays)
    return bytes(flattened_bytes)
