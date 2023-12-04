import json
import os
import random
from pathlib import Path

import pytest

from bee_py.modules.debug.chunk import delete_chunk_from_local_storage
from bee_py.modules.debug.connectivity import get_node_addresses
from bee_py.modules.debug.stamps import create_postage_batch, get_postage_batch
from bee_py.types.type import BatchId
from bee_py.utils.hex import bytes_to_hex

PROJECT_PATH = Path(__file__).parent
DATA_FOLDER = PROJECT_PATH / "test_files"
BEE_DATA_FILE = DATA_FOLDER / "bee_data.json"
ENV_FILE = PROJECT_PATH / "../Env"


@pytest.fixture
def max_int() -> int:
    return 9007199254740991


@pytest.fixture(scope="session", autouse=True)
def get_api_url():
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            data = json.loads(f.read())
        if data["BEE_API_URL"]:
            BEE_API_URL = data["BEE_API_URL"]  # noqa: N806
    else:
        BEE_API_URL = "http://localhost:1633"  # noqa: N806

    return BEE_API_URL


@pytest.fixture(scope="session", autouse=True)
def get_peer_api_url():
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            data = json.loads(f.read())
        if data["BEE_PEER_API_URL"]:
            BEE_PEER_API_URL = data["BEE_PEER_API_URL"]  # noqa: N806
    else:
        BEE_PEER_API_URL = "http://localhost:11633"  # noqa: N806

    return BEE_PEER_API_URL


@pytest.fixture(scope="session", autouse=True)
def bee_debug_url():
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            data = json.loads(f.read())
        if data["BEE_DEBUG_API_URL"]:
            BEE_DEBUG_API_URL = data["BEE_DEBUG_API_URL"]  # noqa: N806
    else:
        BEE_DEBUG_API_URL = "http://localhost:1635"  # noqa: N806

    return BEE_DEBUG_API_URL


@pytest.fixture(scope="session", autouse=True)
def bee_peer_debug_url():
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            data = json.loads(f.read())
        if data["BEE_DEBUG_PEER_API_URL"]:
            BEE_DEBUG_PEER_API_URL = data["BEE_DEBUG_API_URL"]  # noqa: N806
    else:
        BEE_DEBUG_PEER_API_URL = "http://localhost:11635"  # noqa: N806

    return BEE_DEBUG_PEER_API_URL


@pytest.fixture
def get_data_folder() -> str:
    return DATA_FOLDER


@pytest.fixture
def bee_url(get_api_url) -> str:
    return get_api_url


@pytest.fixture
def bee_peer_url(get_peer_api_url) -> str:
    return get_peer_api_url


@pytest.fixture
def read_bee_postage() -> dict:
    """
    make it dynamic
    """
    with open(BEE_DATA_FILE) as f:
        data = json.loads(f.read())
    return data


@pytest.fixture
def bee_ky_options(bee_url) -> dict:
    return {"baseURL": bee_url, "timeout": 300, "onRequest": True}


@pytest.fixture
def bee_peer_ky_options(bee_peer_url) -> dict:
    return {"baseURL": bee_peer_url, "timeout": 300, "onRequest": True}


@pytest.fixture
def bee_debug_ky_options(bee_peer_debug_url) -> dict:
    return {"baseURL": bee_peer_debug_url, "timeout": 300, "onRequest": True}


@pytest.fixture
def read_local_bee_stamp() -> str:
    with open(BEE_DATA_FILE) as f:
        stamp = json.loads(f.read())
    if stamp["BEE_POSTAGE"]:
        return stamp["BEE_POSTAGE"]
    return False


@pytest.fixture
def read_local_bee_peer_stamp() -> str:
    with open(BEE_DATA_FILE) as f:
        stamp = json.loads(f.read())
    if stamp["BEE_PEER_POSTAGE"]:
        return stamp["BEE_PEER_POSTAGE"]
    return False


@pytest.fixture
def get_debug_postage(printer, bee_debug_ky_options) -> BatchId:
    stamp: BatchId

    printer("[*]Getting Debug Postage....")
    # return "0717e834668a3da917dacacacab61ca5a3ea1e5411e1e3d2de5f96a9fb8a0a0d"

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


@pytest.fixture
def get_peer_debug_postage(printer, bee_peer_debug_ky_options) -> BatchId:
    stamp: BatchId

    # if read_local_bee_peer_stamp:
    #     return read_local_bee_peer_stamp
    # return "6be2b2aacd687180a109d960cb9b1da0b446f4fca3966c6b7fdd84e6d9fdad52"

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


@pytest.fixture
def try_delete_chunk_from_local_storage(bee_debug_ky_options):
    def _method(soc_hash):
        address = soc_hash
        if isinstance(address, bytes):
            address = bytes_to_hex(address)

        try:
            response = delete_chunk_from_local_storage(bee_debug_ky_options, address)
            return response
        except ValueError as e:
            try:
                response.status_code == 400  # noqa: B015
                return response
            except:  # noqa: E722
                raise e  # noqa: B904

    return _method


@pytest.fixture(scope="session")
def create_fake_file(tmp_path_factory):
    # Create a temporary file in the tmp_path directory
    temp_file = tmp_path_factory.mktemp("temp") / "temp_file.txt"

    # Write 32 bytes of data to the file
    temp_file.write_bytes(b"a" * 32)

    return temp_file
