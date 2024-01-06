from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from typing_extensions import TypeGuard

from bee_py.types.type import Data, Length

Min = TypeVar("Min", bound=int)
Max = TypeVar("Max", bound=int)


class FlexBytes(BaseModel, Generic[Min, Max]):
    """Helper type for dealing with flexible sized byte arrays.

    The actual min and and max values are not stored in runtime, they
    are only there to differentiate the type from the Uint8Array at
    compile time.

    Args:
    data: The data of the byte array.
    min: The minimum length of the byte array.
    max: The maximum length of the byte array.

    Raises:
    ValueError: If the length of the byte array is not within the specified range.
    """

    data: bytes
    min_length: Min
    max_length: Max

    class Config:
        validate_assignment = True


def is_valid_flex_bytes(flex_bytes: FlexBytes) -> bool:
    """Checks if a byte array is within the specified length range.

    Args:
                            flex_bytes: The byte array to check.

    Returns:
                            True if the byte array is valid, False otherwise.
    """

    return flex_bytes.min_length <= len(flex_bytes) <= flex_bytes.max_length  # type: ignore


def is_bytes(b: Any, length: int) -> TypeGuard[bytes]:
    """Type guard for the `bytes` type.

    Args:
            b: The value to check.
            length: The length of the byte array.

    Returns:
            True if the value is a byte array of the specified length, False otherwise.
    """

    return isinstance(b, bytes) and len(b) == length


def has_bytes_at_offset(data: bytes, offset: int, length: int) -> bool:
    """Checks if the specified byte array is contained in the given data at the specified offset.

    Args:
            data: The data to check.
            offset: The offset to check at.
            length: The length of the byte array to check.

    Returns:
            True if the byte array is contained in the data at the specified offset, False otherwise.
    """

    if not isinstance(data, bytes):
        msg = "Data must be a byte array."
        raise TypeError(msg)

    if offset < 0 or offset + length > len(data):
        return False

    offset_bytes = data[offset : offset + length]

    return is_bytes(offset_bytes, length)


def is_flex_bytes(b: Any, flex_bytes: FlexBytes) -> TypeGuard[bytes]:
    """Type guard for the `FlexBytes` type.

    Args:
            b: The value to check.
            flex_bytes: A `FlexBytes` object.

    Returns:
            True if the value is a byte array within the specified length range, False otherwise.
    """

    return isinstance(b, bytes) and flex_bytes.min_length <= len(b) <= flex_bytes.max_length


def assert_bytes_length(b: bytes, length: int):
    """Asserts that the length of the given byte array is equal to the specified length.

    Args:
            b: The byte array to check.
            length: The specified length.

    Raises:
            TypeError: If the length of the byte array is not equal to the specified length.
    """

    if not is_bytes(b, length):
        msg = f"Parameter is not valid Bytes of length: {length} !== {len(b)}"
        raise TypeError(msg)


def flex_bytes_at_offset(data: bytes, offset: int, min_size: int, max_size: int) -> bytes:
    """Returns a flex bytes object starting from the specified offset, ensuring the size is within the specified range.

    Args:
        data: The original byte data.
        offset: The offset to start extracting the flex bytes from.
        min_size: The minimum allowed size of the extracted flex bytes.
        max_size: The maximum allowed size of the extracted flex bytes.

    Raises:
        ValueError if the extracted flex bytes size falls outside the specified range.

    Returns:
        A flex bytes object representing the extracted byte sequence.
    """

    extracted_bytes = data[offset:]
    extracted_bytes_size = len(extracted_bytes)

    if extracted_bytes_size < min_size or extracted_bytes_size > max_size:
        msg = f"Flex bytes size must be between {min_size} and {max_size}, but found {extracted_bytes_size}"
        raise ValueError(msg)

    return extracted_bytes


def bytes_equal(a: bytes, b: bytes) -> bool:
    """Returns True if the two byte arrays are equal, False otherwise.

    Args:
            a: The first byte array to compare.
            b: The second byte array to compare.

    Returns:
            True if the two byte arrays are equal, False otherwise.
    """

    if len(a) != len(b):
        return False

    return all(a[i] == b[i] for i in range(len(a)))


def make_bytes(length: int) -> bytes:
    """Returns a new byte array filled with zeroes with the specified length.

    Args:
            length: The length of the byte array.

    Returns:
            A byte array filled with zeroes with the specified length.
    """

    return bytes(b"\x00" * length)


def wrap_bytes_with_helpers(data: bytes) -> Data:
    """Wraps the given byte array with helper methods for text, JSON, and hex encoding.

    Args:
            data: The byte array to wrap.

    Returns:
            A byte array wrapped with helper methods for text, JSON, and hex encoding.
    """
    if not isinstance(data, bytes):
        msg = "Data must be a byte array."
        raise TypeError(msg)

    return Data(data=data)


def bytes_at_offset(data: bytes, offset: int, length: Length) -> bytes:
    """
    Returns `length` bytes starting from `offset`.

    Args:
        data: The original data.
        offset: The offset to start from.
        length: The length of data to be returned.

    Returns:
        bytes: The bytes at the given offset and length.
    """
    offset_bytes = data[offset : offset + length]

    # * We are returning strongly typed Bytes so we have to verify that length is really what we claim
    if not len(offset_bytes) == length:
        msg = f"Lenght mismatch. Expected {length}, got {offset_bytes!r}"
        raise ValueError(msg)

    return offset_bytes
