import binascii
import re
from typing import Optional, Union

# from bee_py.types.type import HexString


def bytes_to_hex(inp: bytes, length: Optional[int] = None) -> str:
    """Converts a byte array to a hexadecimal string.

    Args:
        inp: The byte array to convert.
        length: The length of the resulting hex string in bytes.

    Returns:
        A hexadecimal string representing the byte array.

    Raises:
        ValueError: If the length of the resulting hex string does not match the specified length.
    """
    # Convert byte array to hexadecimal
    hex_string = binascii.hexlify(inp).decode()

    if length is not None and len(hex_string) != length:
        msg = f"Length mismatch for valid hex string. Expected length {length}: {hex_string}"
        raise ValueError(msg)

    return hex_string


def hex_to_bytes(hex_string: str) -> bytes:
    """Converts a hex string to a byte array.

    Args:
        hex_string: A hex string.

    Returns:
        A byte array representing the hex string.

    Raises:
        ValueError: If the hex string is not a valid hexadecimal string.
    """
    # if ref starts with 0x remove it
    if hex_string.startswith("0x"):
        hex_string = hex_string[2:]
    return binascii.unhexlify(hex_string)


def str_to_hex(inp: str, length: Optional[int] = None) -> str:
    """Converts a string to a hexadecimal string.

    Args:
        inp: The string to convert.
        length: The length of the resulting hex string in bytes.

    Returns:
        A hexadecimal string representing the string.

    Raises:
        ValueError: If the string is not already a hexadecimal string.
    """

    if inp.startswith("0x"):
        # Remove "0x" prefix
        hex_string = inp[2:]
    else:
        hex_string = inp

    if length is not None and len(hex_string) != length:
        msg = f"Length mismatch for valid hex string. Expected length {length}: {hex_string}"
        raise ValueError(msg)

    return hex_string


def int_to_hex(inp: int, length: Optional[int] = None) -> str:
    """Converts an integer to a hexadecimal string.

    Args:
        inp: The integer to convert.
        length: The length of the resulting hex string in bytes.

    Returns:
        A hexadecimal string representing the integer.

    Raises:
        ValueError: If the length of the resulting hex string does not match the specified length.
    """
    # Convert integer to hexadecimal
    hex_string = hex(inp)[2:]

    if length is not None and len(hex_string) != length:
        msg = f"Length mismatch for valid hex string. Expected length {length}: {hex_string}"
        raise ValueError(msg)

    return hex_string


def is_hex_string(s: str, length: Optional[int] = None) -> bool:
    """Type guard for HexStrings.

    Requires no 0x prefix!

    Args:
        s: A string input.
        length: The expected length of the HexString.

    Returns:
        True if the input is a valid HexString, False otherwise.
    """

    if not isinstance(s, str):
        return False

    if not re.match(r"^[0-9a-f]+$", s, flags=re.IGNORECASE):
        return False

    if length is not None and len(s) != length:
        return False

    return True


def is_prefixed_hex_string(s: str) -> bool:
    """Type guard for PrefixedHexStrings.

    Requires the 0x prefix!

    Args:
        s: A string input.

    Returns:
        True if the input is a valid PrefixedHexString, False otherwise.
    """

    if not isinstance(s, str):
        return False

    if not re.match(r"^0x[0-9a-f]+$", s, flags=re.IGNORECASE):
        return False

    return True


def make_hex_string(input_data: Union[int, bytes, str], length: Optional[int] = None) -> str:
    """Creates an unprefixed hex string from a wide range of data.

    Args:
        input_data: The input data. It can be an integer, byte array, or string.
        length: The length of the resulting hex string in bytes.

    Returns:
        A hex string representing the input data.

    Raises:
        TypeError: If the input data is not an integer, byte array, or string.
        ValueError: If the length of the resulting hex string does not match the specified length.
    """

    if isinstance(input_data, str):
        if is_prefixed_hex_string(input_data):
            # Remove "0x" prefix
            hex_string = input_data[2:]
            if length and len(hex_string) != length:
                msg = f"Length mismatch for valid hex string. Expecting length {length}: {hex_string}"
                raise ValueError(msg)
            return hex_string  # Return string instead of HexString instance
        elif is_hex_string(input_data, length):
            return input_data
        else:
            msg = "Not a valid hex string."
            raise ValueError(msg)

    if isinstance(input_data, int):
        hex_string = int_to_hex(input_data, length)
    elif isinstance(input_data, bytes):
        hex_string = bytes_to_hex(input_data, length)
    else:
        msg = "Not HexString compatible type!"
        raise TypeError(msg)

    return hex_string