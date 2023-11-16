import pytest

from bee_py.chunk.cac import assert_valid_chunk_data, make_content_addressed_chunk
from bee_py.chunk.serialize import serialize_bytes
from bee_py.chunk.span import make_span
from bee_py.utils.hex import assert_bytes, hex_to_bytes


def test_make_content_addressed_chunk(payload):
    chunk = make_content_addressed_chunk(payload)
    address = chunk.address()

    assert address.hex() == "0xca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"


def test_content_address_chunk_verification(payload, content_hash, invalid_address):
    valid_address = hex_to_bytes(content_hash)
    assert_bytes(valid_address, 32)
    assert_bytes(invalid_address, 32)

    data = serialize_bytes(make_span(len(payload)), payload)

    with pytest.raises(ValueError):
        assert_valid_chunk_data(data, invalid_address)

    assert_valid_chunk_data(data, valid_address)
