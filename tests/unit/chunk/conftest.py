import json
from pathlib import Path

import pytest

from bee_py.chunk.bmt import bmt_hash
from bee_py.chunk.serialize import serialize_bytes
from bee_py.chunk.span import make_span
from bee_py.types.type import Data
from bee_py.utils.bytes import wrap_bytes_with_helpers
from bee_py.utils.hex import hex_to_bytes

PROJECT_PATH = Path(__file__).parent
DATA_FOLDER = PROJECT_PATH / "data"
ACCOUNTS_FILE = DATA_FOLDER / "test_account.json"


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


# test signer
@pytest.fixture
def test_account_from_file() -> dict:
    return json.loads(open(ACCOUNTS_FILE))


@pytest.fixture
def data_to_sign_bytes() -> bytes:
    return hex_to_bytes("2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae")


@pytest.fixture
def data_to_sign_with_helper(data_to_sign_bytes) -> Data:
    return wrap_bytes_with_helpers(data_to_sign_bytes())


@pytest.fixture
def expected_signature_hex() -> str:
    return "336d24afef78c5883b96ad9a62552a8db3d236105cb059ddd04dc49680869dc16234f6852c277087f025d4114c4fac6b40295ecffd1194a84cdb91bd571769491b"  # noqa: E501


@pytest.fixture
def expected_signature_bytes(expected_signature_hex) -> bytes:
    return hex_to_bytes(expected_signature_hex)
