import json
from pathlib import Path

import pytest

from bee_py.modules.debug.connectivity import get_node_addresses
from bee_py.modules.debug.stamps import create_postage_batch, get_postage_batch
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
def read_local_bee_stamp() -> str:
    with open(BEE_DATA_FILE) as f:
        stamp = json.loads(f)
    if stamp["BEE_POSTAGE"]:
        return stamp["BEE_POSTAGE"]
    return False


@pytest.fixture
def read_local_bee_peer_stamp() -> str:
    with open(BEE_DATA_FILE) as f:
        stamp = json.loads(f)
    if stamp["BEE_PEER_POSTAGE"]:
        return stamp["BEE_PEER_POSTAGE"]
    return False


@pytest.fixture
def get_debug_postage(printer, read_local_bee_stamp, bee_debug_ky_options) -> BatchId:
    stamp: BatchId

    printer("[*]Getting Debug Postage....")

    if read_local_bee_stamp:
        printer(read_local_bee_stamp)
        return read_local_bee_stamp

    stamp = create_postage_batch(bee_debug_ky_options, 100, 20)

    if not stamp:
        msg = "There is no valid postage stamp"
        raise ValueError(msg)

    printer("[*]Waiting for postage to be usable....")
    while True:
        usable = get_postage_batch(bee_debug_ky_options, stamp).usable
        if usable:
            break
    printer(f"[*]Valid Postage found: {stamp}")
    return stamp


@pytest.fixture
def get_peer_debug_postage(printer, read_local_bee_peer_stamp, bee_peer_debug_ky_options) -> BatchId:
    stamp: BatchId

    if read_local_bee_peer_stamp:
        return read_local_bee_peer_stamp

    printer("[*]Getting Debug Postage....")
    stamp = create_postage_batch(bee_peer_debug_ky_options, 100, 20)

    if not stamp:
        msg = "There is no valid postage stamp"
        raise ValueError(msg)

    printer("[*]Waiting for postage to be usable....")
    while True:
        usable = get_postage_batch(bee_peer_debug_ky_options, stamp).usable
        if usable:
            break
    printer(f"[*]Valid Postage found: {stamp}")
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


BIG_FILE_TIMEOUT = 100_000
