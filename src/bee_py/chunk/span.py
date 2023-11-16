import struct

from bee_py.utils.error import BeeArgumentError

SPAN_SIZE = 8
# we limit the maximum span size in 32 bits to avoid BigInt compatibility issues
MAX_SPAN_LENGTH = 2**32 - 1


def make_span(length: int) -> bytes:
    """
    Creates a span for storing the length of a chunk.

    The length is encoded in 64-bit little endian format.

    Args:
        length (int): The length of the chunk.

    Returns:
        bytes: The span representing the chunk length.
    """
    if length <= 0:
        msg = "Invalid length for span"
        raise BeeArgumentError(msg, length)

    if length > MAX_SPAN_LENGTH:
        msg = "Invalid length (> MAX_SPAN_LENGTH)"
        raise BeeArgumentError(msg, length)

    # Pack the 64-bit little-endian representation of the length
    span = struct.pack("<Q", length)

    return span
