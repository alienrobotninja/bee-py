import pytest


@pytest.fixture
def max_int():
    return 2**53 - 1 


# assuming these are the values you're testing with
@pytest.fixture
def test_data():
    return bytes.fromhex("00112233445566778899aabbccddeeff"), "00112233445566778899aabbccddeeff"
