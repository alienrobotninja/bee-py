import pytest

# test_chunk

MOCK_SERVER_URL = "http://localhost:1633"


@pytest.fixture
def bee_ky_options() -> dict:
    return {"baseURL": MOCK_SERVER_URL, "timeout": False}


@pytest.fixture
def get_postage_batch() -> str:
    ...
