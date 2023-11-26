import json
from pathlib import Path

import pytest

from bee_py.modules.debug.connectivity import get_node_addresses
from bee_py.types.type import BatchId


@pytest.fixture
def max_int() -> int:
    return 9007199254740991


BEE_API_URL = "http://localhost:1633"
BEE_PEER_API_URL = "http://127.0.0.1:11633"
PROJECT_PATH = Path(__file__).parent
DATA_FOLDER = PROJECT_PATH / "data"
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
    """
    make it dynamic
    """
    with open(BEE_DATA_FILE) as f:
        data = json.loads(f.read())
    return data


@pytest.fixture
def bee_ky_options(bee_debug_url) -> dict:
    return {"baseURL": bee_debug_url, "timeout": 300, "onRequest": True}


@pytest.fixture
def bee_debug_ky_options(bee_peer_debug_url) -> dict:
    return {"baseURL": bee_peer_debug_url, "timeout": 300, "onRequest": True}


@pytest.fixture
def get_postage_batch(request, url: str = "bee_debug_url") -> BatchId:
    stamp: BatchId

    if url == "bee_debug_url":
        stamp = request.getfixturevalue("read_bee_postage")["BEE_POSTAGE"]
    elif url == "bee_peer_debug_url":
        stamp = request.getfixturevalue("read_bee_postage")["BEE_PEER_POSTAGE"]
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
def bee_peer_debug_ky_options(bee_peer_debug_url):
    return {"baseURL": bee_peer_debug_url, "timeout": 300, "onRequest": True}


@pytest.fixture
def peer_overlay(bee_peer_debug_ky_options) -> str:
    node_addresses = get_node_addresses(bee_peer_debug_ky_options)

    return node_addresses.overlay
