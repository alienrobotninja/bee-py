import pytest

from bee_py.chunk.bmt import bmt_hash
from bee_py.chunk.serialize import serialize_bytes
from bee_py.chunk.span import make_span

# test cac


@pytest.fixture
def payload() -> bytes:
    return bytes([1, 2, 3])


@pytest.fixture
def invalid_address():
    return bytes.fromhex("ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4335")


@pytest.fixture
def content_hash():
    return "ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"


@pytest.fixture
def valid_address(content_hash):
    return bmt_hash(bytes.fromhex(content_hash))


@pytest.fixture
def data(payload):
    return serialize_bytes(make_span(len(payload)), payload)
