from typing import Union

from eth_pydantic_types import HexBytes
from pydantic import BaseModel, Field

from bee_py.chunk.bmt import bmt_hash
from bee_py.chunk.serialize import serialize_bytes
from bee_py.chunk.span import SPAN_SIZE, make_span
from bee_py.utils.bytes import bytes_equal, flex_bytes_at_offset

MIN_PAYLOAD_SIZE = 1
MAX_PAYLOAD_SIZE = 4096

CAC_SPAN_OFFSET = 0
CAC_PAYLOAD_OFFSET = CAC_SPAN_OFFSET + SPAN_SIZE


class Chunk(BaseModel):
    """
    * General chunk class for Swarm

    It stores the serialized data and provides functions to access
    the fields of a chunk.

    It also provides an address function to calculate the address of
    the chunk that is required for the Chunk API.
    """

    data: bytes = Field(..., description="The data of the chunk")
    span: bytes = Field(..., description="The span of the chunk")
    payload: bytes = Field(..., description="The payload of the chunk")
    address: Union[HexBytes, bytes] = Field(..., description="The address of the chunk")


def is_valid_chunk_data(data: bytes, chunk_address: bytes) -> bool:
    """
    Checks if the provided data represents a valid content-addressed chunk with the given address.

    Args:
        data (bytes): The chunk data to be validated.
        chunk_address (bytes): The expected address of the chunk.

    Returns:
        bool: True if the data represents a valid content-addressed chunk with the given address; False otherwise.
    """
    if not isinstance(data, bytes):
        return False

    calculated_address = bmt_hash(data)
    return bytes_equal(calculated_address, chunk_address)


def assert_valid_chunk_data(data: bytes, chunk_address: bytes) -> None:
    """
    Asserts that the provided data represents a valid content-addressed chunk with the given address.

    Args:
        data (bytes): The chunk data to be validated.
        chunk_address (bytes): The expected address of the chunk.

    Raises:
        ValueError: If the data does not represent a valid content-addressed chunk with the given address.
    """
    if not is_valid_chunk_data(data, chunk_address):
        msg = "Address of content addressed chunk does not match given data!"
        raise ValueError(msg)


def make_content_addressed_chunk(payload_bytes: bytes) -> Chunk:
    span = make_span(len(payload_bytes))

    data = serialize_bytes(span, payload_bytes)
    payload = flex_bytes_at_offset(data, CAC_PAYLOAD_OFFSET, MIN_PAYLOAD_SIZE, MAX_PAYLOAD_SIZE)
    address = bmt_hash(data)

    return Chunk(data=data, span=span, payload=payload, address=address)
