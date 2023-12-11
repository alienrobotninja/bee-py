from unittest.mock import patch

import pytest

from bee_py.bee import Bee
from bee_py.feed.topic import make_topic_from_string
from bee_py.feed.type import FeedType
from bee_py.types.type import (
    CHUNK_SIZE,
    SPAN_SIZE,
    BatchId,
    BeeRequestOptions,
    CollectionUploadOptions,
    PssMessageHandler,
    ReferenceResponse,
    UploadOptions,
)
from bee_py.utils.error import BeeArgumentError, BeeError

TOPIC = "some=very%nice#topic"
HASHED_TOPIC = make_topic_from_string(TOPIC)
MOCK_SERVER_URL = "http://localhost:12345/"

# * Endpoints
FEED_ENDPOINT = "/feeds"
BZZ_ENDPOINT = "/bzz"
BYTES_ENDPOINT = "/bytes"
POSTAGE_ENDPOINT = "/stamps"
CHEQUEBOOK_ENDPOINT = "/chequebook"


@pytest.mark.parametrize(
    "url", ["", None, "some-invalid-url", "invalid:protocol", "javascript:console.log()", "ws://localhost:1633"]
)
def test_bee_constructor(url):
    with pytest.raises(BeeArgumentError):
        Bee(url)


@patch("bee_py.bee.Bee")
def test_upload_file_mock(mock_bee, requests_mock):
    default_headers = {"X-Awesome-Header": "123"}
    mock_bee.return_value.upload_file.return_value = {
        "reference": "e032d8ddc7227d0d6c4d0f87db16027924216afd0c00012884ba7af835b4a7c7",
        "tagUid": 123,
    }
    mock_bee.return_value.cid.return_value = "1b20e032d8ddc7227d0d6c4d0f87db16027924216afd0c00012884ba7af835b4a7c7"

    requests_mock.post(
        # f"{MOCK_SERVER_URL}{BZZ_ENDPOINT}", # idk this doesn't work
        "http://localhost:12345/bzz",
        json={
            "reference": "e032d8ddc7227d0d6c4d0f87db16027924216afd0c00012884ba7af835b4a7c7",
            "tagUid": 123,
        },
        status_code=200,
    )

    bee = Bee(MOCK_SERVER_URL, {"headers": default_headers})
    reference = bee.upload_file("testBatchId", "hello world", "nice.txt")

    assert str(reference.reference) == "e032d8ddc7227d0d6c4d0f87db16027924216afd0c00012884ba7af835b4a7c7"
    assert reference.cid().multihash.hex() == "1b20e032d8ddc7227d0d6c4d0f87db16027924216afd0c00012884ba7af835b4a7c7"


@patch("bee_py.bee.Bee")
def test_cid_encrypted_references(
    mock_bee, requests_mock, test_chunk_encrypted_reference, test_chunk_encrypted_reference_cid
):
    test_tag_id = "123"
    # Mock the upload_file method
    mock_bee.return_value.upload_file.return_value = {
        "reference": test_chunk_encrypted_reference,
        "tagUid": test_tag_id,
    }

    requests_mock.post(
        # f"{MOCK_SERVER_URL}{BZZ_ENDPOINT}", # idk this doesn't work
        "http://localhost:12345/bzz",
        json={"reference": test_chunk_encrypted_reference},
        status_code=200,
        headers={"swarm-tag": test_tag_id},
    )

    # Create an instance of Bee with the mock instance
    bee = Bee(MOCK_SERVER_URL)

    # Call the upload_file method
    reference = bee.upload_file("testBatchId", "hello world", "nice.txt")

    # Check the return values
    assert str(reference.reference) == test_chunk_encrypted_reference

    assert reference.tag_uid == int(test_tag_id)

    assert reference.cid() == test_chunk_encrypted_reference_cid


def batch_id_assertion(executor):
    @pytest.mark.parametrize(
        "input_value, expected_error_type",
        [
            (1, TypeError),
            (True, TypeError),
            ({}, BeeError),
            (None, BeeError),
            ([], BeeError),
            ("", BeeError),
            ("ZZZfb5a872396d9693e5c9f9d7233cfa93f395c093371017ff44aa9ae6564cdd", TypeError),
            ("0x634fb5a872396d9693e5c9f9d7233cfa93f395c093371017ff44aa9ae6564cdd", TypeError),
        ],
    )
    def test_function(input_value, expected_error_type):
        with pytest.raises(expected_error_type):
            executor(input_value)

    return test_function


def test_upload_data():
    def executor(input_value):
        bee = Bee(MOCK_SERVER_URL)
        return bee.upload_data(input_value, "")

    batch_id_assertion(executor)
