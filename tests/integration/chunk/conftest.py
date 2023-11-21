import os
from typing import Union

import ape
import pytest
from dotenv import load_dotenv

from bee_py.modules.debug.chunk import delete_chunk_from_local_storage
from bee_py.types.type import BatchId
from bee_py.utils.hex import bytes_to_hex

load_dotenv()


MOCK_SERVER_URL = "http://localhost:1633"


@pytest.fixture
def bee_debug_url() -> str:
    return "http://127.0.0.1:1635"


@pytest.fixture
def bee_peer_debug_url() -> str:
    return "http://127.0.0.1:11635"


@pytest.fixture
def bee_ky_options() -> dict:
    return {"baseURL": MOCK_SERVER_URL, "timeout": False}


@pytest.fixture
def bee_debug_ky_options(bee_debug_url) -> dict:
    return {"baseURL": bee_debug_url(), "timeout": False}


@pytest.fixture
def get_postage_batch(url: str = "bee_debug_url") -> BatchId:
    stamp: BatchId

    if url == "bee_debug_url":
        stamp = os.environ.get("BEE_POSTAGE", None)
    elif url == "bee_peer_debug_url":
        stamp = os.environ.get("BEE_PEER_POSTAGE", None)
    else:
        msg = f"Unknown url: {url}"
        raise ValueError(msg)

    if not stamp:
        msg = f"There is no postage stamp configured for URL: {url}"
        raise ValueError(msg)
    return stamp


@pytest.fixture
def bee_debug_url_postage(get_postage_batch) -> BatchId:
    return get_postage_batch("bee_debug_url")


@pytest.fixture
def bee_peer_debug_url_postage(get_postage_batch) -> BatchId:
    return get_postage_batch("bee_peer_debug_url")


@pytest.fixture
def try_delete_chunk_from_local_storage(address: Union[str, bytes], bee_debug_ky_options):
    if isinstance(address, bytes):
        address = bytes_to_hex(address)

    try:
        response = delete_chunk_from_local_storage(bee_debug_ky_options, address)
    except ValueError as e:
        if response.status_code == 400:
            return
        else:
            raise e


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
