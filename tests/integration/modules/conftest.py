import json
from pathlib import Path

import pytest

from bee_py.modules.debug.stamps import create_postage_batch, get_postage_batch
from bee_py.types.type import BatchId

# test_chunk

BEE_API_URL = "http://localhost:1633"
BEE_PEER_API_URL = "http://127.0.0.1:11633"
PROJECT_PATH = Path(__file__).parent
DATA_FOLDER = PROJECT_PATH / "../../test_files"
BEE_DATA_FILE = DATA_FOLDER / "bee_data.json"


@pytest.fixture
def bee_url() -> str:
    return BEE_API_URL


@pytest.fixture
def bee_peer_url() -> str:
    return BEE_PEER_API_URL


@pytest.fixture
def bee_debug_url() -> str:
    return "http://127.0.0.1:1635"


@pytest.fixture
def bee_peer_debug_url() -> str:
    return "http://127.0.0.1:11635"


@pytest.fixture
def read_bee_postage() -> dict:
    with open(BEE_DATA_FILE) as f:
        data = json.loads(f.read())
    return data


@pytest.fixture
def bee_ky_options(bee_url) -> dict:
    return {"baseURL": bee_url, "timeout": 100, "onRequest": True}


@pytest.fixture
def bee_debug_ky_options(bee_debug_url) -> dict:
    return {"baseURL": bee_debug_url, "timeout": 100, "onRequest": True}


# @pytest.fixture
# def get_debug_postage(printer, bee_debug_ky_options) -> BatchId:
#     stamp: BatchId

#     printer("[*]Getting Debug Postage....")
#     stamp = create_postage_batch(bee_debug_ky_options, 100, 20)

#     if not stamp:
#         msg = "There is no valid postage stamp"
#         raise ValueError(msg)

#     printer("[*]Waiting for postage to be usable....")
#     while True:
#         usable = get_postage_batch(bee_debug_ky_options, stamp).usable
#         if usable:
#             break
#     printer(f"[*]Valid Postage found: {stamp}")
#     return stamp


# @pytest.fixture
# def get_peer_debug_postage(printer, bee_peer_debug_ky_options) -> BatchId:
#     stamp: BatchId
#     printer("[*]Getting Debug Postage....")
#     stamp = create_postage_batch(bee_peer_debug_ky_options, 100, 20)

#     if not stamp:
#         msg = "There is no valid postage stamp"
#         raise ValueError(msg)

#     printer("[*]Waiting for postage to be usable....")
#     while True:
#         usable = get_postage_batch(bee_peer_debug_ky_options, stamp).usable
#         if usable:
#             break
#     printer(f"[*]Valid Postage found: {stamp}")
#     return stamp


@pytest.fixture
def bee_debug_url_postage(get_postage_batch) -> BatchId:
    return get_postage_batch("bee_debug_url")


@pytest.fixture
def bee_peer_debug_url_postage(get_postage_batch) -> BatchId:
    return get_postage_batch("bee_peer_debug_url")
