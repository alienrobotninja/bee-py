import json
import os
import random
from pathlib import Path
from typing import Union
from unittest.mock import MagicMock

import pytest

from bee_py.bee import Bee
from bee_py.modules.debug.chunk import delete_chunk_from_local_storage
from bee_py.modules.debug.connectivity import get_node_addresses
from bee_py.modules.debug.stamps import create_postage_batch, get_postage_batch
from bee_py.types.type import BatchId, Reference
from bee_py.utils.hex import bytes_to_hex

PROJECT_PATH = Path(__file__).parent
DATA_FOLDER = PROJECT_PATH / "data"
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
            BEE_DEBUG_PEER_API_URL = data["BEE_DEBUG_PEER_API_URL"]  # noqa: N806
    else:
        BEE_DEBUG_PEER_API_URL = "http://localhost:11635"  # noqa: N806

    return BEE_DEBUG_PEER_API_URL


@pytest.fixture
def get_data_folder() -> Path:
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
def bee_debug_ky_options(bee_debug_url) -> dict:
    return {"baseURL": bee_debug_url, "timeout": 300, "onRequest": True}


@pytest.fixture
def bee_debug_peer_ky_options(bee_peer_debug_url) -> dict:
    return {"baseURL": bee_peer_debug_url, "timeout": 300, "onRequest": True}


@pytest.fixture
def read_local_bee_stamp() -> Union[str, bool]:
    with open(BEE_DATA_FILE) as f:
        stamp = json.loads(f.read())
    if stamp["BEE_POSTAGE"]:
        return stamp["BEE_POSTAGE"]
    return False


@pytest.fixture
def read_local_bee_peer_stamp() -> Union[str, bool]:
    with open(BEE_DATA_FILE) as f:
        stamp = json.loads(f.read())
    if stamp["BEE_PEER_POSTAGE"]:
        return stamp["BEE_PEER_POSTAGE"]
    return False


# * Not a fixture
def request_debug_postage_stamp(bee_debug_ky_options) -> BatchId:
    stamp: BatchId
    stamp = create_postage_batch(bee_debug_ky_options, 100, 20)

    if not stamp:
        msg = "There is no valid postage stamp"
        raise ValueError(msg)

    print("[*]Waiting for postage to be usable....")  # noqa: T201
    while True:
        usable = get_postage_batch(bee_debug_ky_options, stamp).usable
        if usable:
            break
    print(f"[*]Valid Postage found: {stamp}")  # noqa: T201
    return stamp


# * Not a fixture
def request_peer_debug_postage_stamp(bee_peer_debug_ky_options) -> BatchId:
    stamp: BatchId

    # print("[*]Getting Debug Postage....")
    stamp = create_postage_batch(bee_peer_debug_ky_options, 100, 20)

    if not stamp:
        msg = "There is no valid postage stamp"
        raise ValueError(msg)

    print("[*]Waiting for postage to be usable....")  # noqa: T201
    while True:
        usable = get_postage_batch(bee_peer_debug_ky_options, stamp).usable
        if usable:
            break
    print(f"[*]Valid Postage found: {stamp}")  # noqa: T201
    return stamp


@pytest.fixture
def get_cache_debug_postage_stamp(request, bee_debug_ky_options) -> BatchId:
    stamp = request.config.cache.get("debug_postage_stamp", None)

    if not stamp:
        print("[*]Getting postage stamp!....")  # noqa: T201
        stamp = request_debug_postage_stamp(bee_debug_ky_options)
        request.config.cache.set("debug_postage_stamp", stamp)
    return stamp


@pytest.fixture
def get_debug_postage(get_cache_debug_postage_stamp) -> BatchId:
    print("[*]Getting Debug Postage....")  # noqa: T201
    # return "b0a5239a968736020a56517b7bad14d4634d2147896e9bacd840ff56f20bb05b"
    return get_cache_debug_postage_stamp


@pytest.fixture
def get_cache_peer_debug_postage_stamp(request, bee_peer_debug_ky_options) -> BatchId:
    stamp = request.config.cache.get("peer_debug_postage_stamp", None)

    if not stamp:
        print("[*]Getting Peer postage stamp!....")  # noqa: T201
        stamp = request_peer_debug_postage_stamp(bee_peer_debug_ky_options)
        request.config.cache.set("peer_debug_postage_stamp", stamp)
    return stamp


@pytest.fixture
def get_peer_debug_postage(get_cache_peer_debug_postage_stamp) -> BatchId:
    print("[*]Getting Peer Debug Postage....")  # noqa: T201
    return get_cache_peer_debug_postage_stamp


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
def peer_overlay(bee_debug_peer_ky_options) -> str:
    node_addresses = get_node_addresses(bee_debug_peer_ky_options)
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
def test_collection() -> list[dict]:
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
                response.code == 400  # noqa: B015
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


@pytest.fixture
def test_chunk_hash() -> Reference:
    return Reference.model_validate({"value": "ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"})


@pytest.fixture
def feed_reference_hash() -> str:
    # return Reference(value="ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a1111")
    return "ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a1111"


@pytest.fixture
def feed_reference(feed_reference_hash) -> dict:
    return {"reference": feed_reference_hash}


@pytest.fixture
def test_address():
    return "ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"


@pytest.fixture
def mock_bee():
    return MagicMock(spec=Bee)

    # with patch("bee_py.bee.Bee") as mock_bee:
    #     yield mock_bee


@pytest.fixture
def test_chunk_encrypted_reference() -> str:
    return "ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"  # noqa: E501


@pytest.fixture
def test_chunk_encrypted_reference_cid() -> str:
    return "bah5acgzazjrvpieogf6rl3cwb7xtjzgel6hrt4a4g4vkody5u4v7u7y2im4muy2xuchdc7iv5rla73zu4tcf7dyz6aodokvhb4o2ok72p4negoa"  # noqa: E501


@pytest.fixture
def test_batch_id() -> str:
    return "ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"


@pytest.fixture
def test_chunk_hash_str() -> str:
    return "ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"


@pytest.fixture(scope="session")
def create_blank_temp_files(tmp_path_factory):
    # Create a temporary directory
    temp_dir = tmp_path_factory.mktemp("temp")

    # Create 2-3 temporary files in the temporary directory
    temp_files = [temp_dir / f"temp_file_{i}.txt" for i in range(2, 5)]

    return temp_files
