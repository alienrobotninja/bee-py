from typing import Any, Generic, TypeVar

from typing_extensions import TypeGuard

from bee_py.types.type import Data, Length

Min = TypeVar("Min", bound=int)
Max = TypeVar("Max", bound=int)


class FlexBytes(Generic[Min, Max]):
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

    __min__: Min
    __max__: Max

    def __init__(self, data: bytes, minimum: Min, maximum: Max):
        if not (min <= len(data) <= max):
            msg = f"Byte array length must be between {min} and {max}."
            raise ValueError(msg)
        super().__init__(data)
        self.__min__ = minimum
        self.__max__ = maximum

    def __repr__(self) -> str:
        return f"FlexBytes({bytes(self)}, {self.__min__}, {self.__max__})"

    @property
    def minimum(self) -> Min:
        return self.__min__

    @property
    def maximum(self) -> Max:
        return self.__max__


def is_valid_flex_bytes(flex_bytes: FlexBytes) -> bool:
    """Checks if a byte array is within the specified length range.

    Args:
                            flex_bytes: The byte array to check.

    Returns:
                            True if the byte array is valid, False otherwise.
    """

    return flex_bytes.minimum <= len(flex_bytes) <= flex_bytes.maximum


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


def flex_bytes_at_offset(data: bytes, offset: int, length: int) -> bytes:
    """Returns the specified number of bytes from the given data starting at the specified offset.

    Args:
            data: The data to extract the bytes from.
            offset: The offset to start from.
            length: The number of bytes to extract.

    Returns:
            A byte array containing the extracted bytes.

    Raises:
            ValueError: If the offset or length is out of bounds.
    """

    if not (0 <= offset <= len(data) - length):
        msg = "Offset or length is out of bounds."
        raise ValueError(msg)

    offset_bytes = data[offset : offset + length]

    # Assert that the length of the offset bytes is equal to the specified length.
    assert_bytes_length(offset_bytes, length)

    return offset_bytes


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

    return Data(data)


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
        msg = f"Lenght mismatch. Expected {length}, got {offset_bytes}"
        raise ValueError(msg)

    return offset_bytes
