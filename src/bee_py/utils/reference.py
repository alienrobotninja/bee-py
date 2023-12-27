from typing import Union

from bee_py.types.type import (
    ENCRYPTED_REFERENCE_BYTES_LENGTH,
    ENCRYPTED_REFERENCE_HEX_LENGTH,
    REFERENCE_BYTES_LENGTH,
    REFERENCE_HEX_LENGTH,
    Reference,
)
from bee_py.utils.bytes import bytes_at_offset, has_bytes_at_offset
from bee_py.utils.hex import hex_to_bytes, make_hex_string


def make_bytes_reference(reference: Union[Reference, bytes, str], offset: int = 0) -> bytes:
    """
    Converts a chunk reference to a byte array.

    Args:
        reference (Union[bytes, str]): The chunk reference.
        offset (int): The offset of the reference in the byte array.

    Returns:
        bytes: The byte array representation of the chunk reference.
    """
    if isinstance(reference, Reference):
        reference = str(reference)

    if isinstance(reference, str):
        if offset:
            msg = "Offset property can be set only for UintArray reference!"
            raise TypeError(msg)

        try:
            # Non-encrypted chunk hex string reference
            hex_reference = make_hex_string(reference, REFERENCE_HEX_LENGTH)
            return hex_to_bytes(hex_reference)
        except TypeError:
            # Encrypted chunk hex string reference
            hex_reference = make_hex_string(reference, ENCRYPTED_REFERENCE_HEX_LENGTH)
            return hex_to_bytes(hex_reference)

    elif isinstance(reference, bytes):
        if has_bytes_at_offset(reference, offset, ENCRYPTED_REFERENCE_BYTES_LENGTH):
            return bytes_at_offset(reference, offset, ENCRYPTED_REFERENCE_BYTES_LENGTH)
        elif has_bytes_at_offset(reference, offset, REFERENCE_BYTES_LENGTH):
            return bytes_at_offset(reference, offset, REFERENCE_BYTES_LENGTH)

    msg = "invalid chunk reference"
    raise TypeError(msg)
