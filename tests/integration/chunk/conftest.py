from pathlib import Path

import ape
import pytest

# from bee_py.types.type import BatchId

BEE_API_URL = "http://localhost:1633"
PROJECT_PATH = Path(__file__).parent
DATA_FOLDER = PROJECT_PATH / "../../data"
BEE_DATA_FILE = DATA_FOLDER / "bee_data.json"
ACCOUNT_FILE = DATA_FOLDER / "test_account.json"


# @pytest.fixture
# def bee_debug_url() -> str:
#     return "http://127.0.0.1:1635"


# @pytest.fixture
# def bee_peer_debug_url() -> str:
#     return "http://127.0.0.1:11635"


# @pytest.fixture
# def bee_ky_options() -> dict:
#     return {"baseURL": BEE_API_URL, "timeout": 300, "onRequest": True}


# @pytest.fixture
# def bee_debug_ky_options(bee_debug_url) -> dict:
#     return {"baseURL": bee_debug_url, "timeout": 300, "onRequest": True}


# @pytest.fixture
# def get_postage_batch(request, url: str = "bee_debug_url") -> BatchId:
#     stamp: BatchId

#     if url == "bee_debug_url":
#         stamp = request.getfixturevalue("read_bee_postage")["BEE_POSTAGE"]
#     elif url == "bee_peer_debug_url":
#         stamp = request.getfixturevalue("read_bee_postage")["BEE_PEER_POSTAGE"]
#     else:
#         msg = f"Unknown url: {url}"
#         raise ValueError(msg)

#     if not stamp:
#         msg = f"There is no postage stamp configured for URL: {url}"
#         raise ValueError(msg)
#     return stamp


# @pytest.fixture
# def bee_debug_url_postage(get_postage_batch) -> BatchId:
#     return get_postage_batch("bee_debug_url")


# @pytest.fixture
# def bee_peer_debug_url_postage(get_postage_batch) -> BatchId:
#     return get_postage_batch("bee_peer_debug_url")


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
def payload() -> bytes:
    return bytes([1, 2, 3])


@pytest.fixture
def soc_hash() -> str:
    return "9d453ebb73b2fedaaf44ceddcf7a0aa37f3e3d6453fea5841c31f0ea6d61dc85"


# @pytest.fixture
# def soc_signer():
#     private_key = json.loads(open(ACCOUNT_FILE).read())["private_key"]
#     return Account.from_key(private_key)
