import ape
import pytest

from bee_py.utils.bytes import wrap_bytes_with_helpers
from bee_py.utils.stamps import (
    get_stamp_cost_in_bzz,
    get_stamp_cost_in_plur,
    get_stamp_maximum_capacity_bytes,
    get_stamp_ttl_seconds,
    get_stamp_usage,
)

# Endpoints
FEED_ENDPOINT = "/feeds"
BZZ_ENDPOINT = "/bzz"
BYTES_ENDPOINT = "/bytes"
POSTAGE_ENDPOINT = "/stamps"
CHEQUEBOOK_ENDPOINT = "/chequebook"


@pytest.fixture
def max_int():
    return 2**53 - 1


# assuming these are the values you're testing with
@pytest.fixture
def test_data():
    return bytes.fromhex("00112233445566778899aabbccddeeff"), "00112233445566778899aabbccddeeff"


# text_bytes
@pytest.fixture
def wrap_bytes_with_helpers_fixture():
    data = b"hello world"
    wrapped_bytes = wrap_bytes_with_helpers(data)
    return wrapped_bytes


@pytest.fixture
def wrapped_bytes(wrap_bytes_with_helpers_fixture):
    return wrap_bytes_with_helpers_fixture


# test_stamps
@pytest.fixture
def stamp_usage(utilization=4, depth=18, bucket_depth=16):
    return get_stamp_usage(utilization, depth, bucket_depth)


@pytest.fixture
def stamp_maximum_capacity_bytes(depth=20):
    return get_stamp_maximum_capacity_bytes(depth)


@pytest.fixture
def stamp_ttl_seconds(amount=20_000_000_000, price_per_block=24_000, block_time=5):
    return get_stamp_ttl_seconds(amount, price_per_block, block_time)


@pytest.fixture
def stamp_cost_in_bzz(depth=20, amount=20_000_000_000):
    return get_stamp_cost_in_bzz(depth, amount)


@pytest.fixture
def stamp_cost_in_plur(depth=20, amount=20_000_000_000):
    return get_stamp_cost_in_plur(depth, amount)


# test_http

MOCK_SERVER_URL = "http://localhost:12345/"


@pytest.fixture
def ky_options() -> dict:
    return {"baseURL": MOCK_SERVER_URL, "onRequest": True}


# test eth


@pytest.fixture(scope="session")
def accounts():
    return ape.accounts


@pytest.fixture(scope="session")
def test_accounts(accounts):
    return accounts.test_accounts


@pytest.fixture(scope="session")
def alice(test_accounts):
    return test_accounts[0]


@pytest.fixture(scope="session")
def bob():
    return test_accounts[1]
