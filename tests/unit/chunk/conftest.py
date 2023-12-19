from pathlib import Path

import ape
import eth_keys  # type: ignore
import pytest
from eth_keys import keys
from eth_utils import decode_hex

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
# @pytest.fixture
# def test_account_from_file() -> dict:
#     return json.loads(open(ACCOUNTS_FILE))


@pytest.fixture(scope="session")
def accounts():
    return ape.accounts


@pytest.fixture(scope="session")
def test_accounts(accounts):
    return accounts.test_accounts


@pytest.fixture(scope="session")
def signer(test_accounts):
    return test_accounts[0]


@pytest.fixture
def data_to_sign_bytes() -> bytes:
    return hex_to_bytes("2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae")


@pytest.fixture
def data_to_sign_with_helper(data_to_sign_bytes) -> Data:
    return wrap_bytes_with_helpers(data_to_sign_bytes())


@pytest.fixture
def expected_signature_hex() -> str:
    return "1b6258da274d981bdccac1d52435681248a92758ede98195fd8d658b8b3390b2de4023e296185b58614c0f61483edf6e3ef7e9262ce3e1da3efd3a15acfe96c2e6"  # noqa: E501


@pytest.fixture
def public_key(signer) -> eth_keys.datatypes.PublicKey:
    priv_key_bytes = decode_hex(signer.private_key)
    priv_key = keys.PrivateKey(priv_key_bytes)
    pub_key = priv_key.public_key
    return pub_key


@pytest.fixture
def public_key_str(public_key) -> str:
    return public_key.to_hex()


@pytest.fixture
def public_key_bytes(public_key) -> bytes:
    return public_key.to_bytes()


@pytest.fixture
def expected_signature_bytes(expected_signature_hex) -> bytes:
    return hex_to_bytes(expected_signature_hex)
