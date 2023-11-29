import json
import random
from os import environ
from pathlib import Path

import pytest
from dotenv import load_dotenv

from bee_py.modules.debug.connectivity import get_node_addresses
from bee_py.modules.debug.stamps import create_postage_batch, get_postage_batch
from bee_py.types.type import BatchId

load_dotenv()


@pytest.fixture
def max_int() -> int:
    return 9007199254740991


if environ["BEE_API_URL"]:
    BEE_API_URL = environ["BEE_API_URL"]
else:
    BEE_API_URL = "http://localhost:1633"

if environ["BEE_PEER_API_URL"]:
    BEE_PEER_API_URL = environ["BEE_API_URL"]
else:
    BEE_PEER_API_URL = "http://127.0.0.1:11633"

PROJECT_PATH = Path(__file__).parent
DATA_FOLDER = PROJECT_PATH / "test_files"
BEE_DATA_FILE = DATA_FOLDER / "bee_data.json"


@pytest.fixture
def get_data_folder() -> str:
    return DATA_FOLDER


@pytest.fixture
def bee_url() -> str:
    return BEE_API_URL


@pytest.fixture
def bee_peer_url() -> str:
    return BEE_PEER_API_URL


@pytest.fixture
def bee_debug_url() -> str:
    if environ["BEE_DEBUG_API_URL"]:
        return environ["BEE_DEBUG_API_URL"]
    return "http://127.0.0.1:1635"


@pytest.fixture
def bee_peer_debug_url() -> str:
    if environ["BEE_DEBUG_PEER_API_URL"]:
        return environ["BEE_DEBUG_PEER_API_URL"]
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
def bee_peer_ky_options(bee_peer_url) -> dict:
    return {"baseURL": bee_peer_url, "timeout": 300, "onRequest": True}


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
def get_debug_postage(printer, bee_debug_ky_options) -> BatchId:
    stamp: BatchId

    printer("[*]Getting Debug Postage....")

    # if read_local_bee_stamp:
    #     printer(read_local_bee_stamp)
    #     return read_local_bee_stamp

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
    # return "7fc4f823619c539708eabc3210f2c09eb6373ec4d3b62b1a8013c85b9bb14bfd"


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


@pytest.fixture
def random_byte_array(length=10, seed=500):
    # * not completely random
    random.seed(seed)
    return bytearray(random.randint(0, 255) for _ in range(length))  # noqa: S311


@pytest.fixture
def invalid_reference() -> str:
    return "0000000000000000000000000000000000000000000000000000000000000000"


@pytest.fixture
def test_collection() -> dict:
    return [
        {
            "path": "0",
            "data": bytes([0]),
        },
        {
            "path": "1",
            "data": bytes([1]),
        },
    ]
