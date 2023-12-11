# from collections.abc import ByteString, Sequence
# from itertools import chain


def serialize_bytes(*arrays: bytes) -> bytes:
    """
    Serializes a sequence of byte arrays into a single byte array.

    Args:
        *arrays (bytes): The sequence of byte arrays to serialize.

    Returns:
        ByteString: The serialized byte array.
    """
    return b"".join(arrays)
