import pytest

from bee_py.utils.bytes import wrap_bytes_with_helpers


@pytest.fixture
def max_int():
    return 2**53 - 1


# assuming these are the values you're testing with
@pytest.fixture
def test_data():
    return bytes.fromhex("00112233445566778899aabbccddeeff"), "00112233445566778899aabbccddeeff"


@pytest.fixture
def wrap_bytes_with_helpers_fixture():
    data = b"hello world"
    wrapped_bytes = wrap_bytes_with_helpers(data)
    return wrapped_bytes


@pytest.fixture
def wrapped_bytes(wrap_bytes_with_helpers_fixture):
    return wrap_bytes_with_helpers_fixture
