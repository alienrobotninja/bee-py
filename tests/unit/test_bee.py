from unittest.mock import patch

import pydantic
import pytest

from bee_py.bee import Bee
from bee_py.feed.topic import make_topic_from_string

# from bee_py.feed.type import FeedType
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


batch_id_assertion_data = [
    (1, TypeError),
    (True, TypeError),
    ({}, BeeError),
    (None, BeeError),
    ([], BeeError),
    ("", BeeError),
    ("ZZZfb5a872396d9693e5c9f9d7233cfa93f395c093371017ff44aa9ae6564cdd", TypeError),
    ("0x634fb5a872396d9693e5c9f9d7233cfa93f395c093371017ff44aa9ae6564cdd", TypeError),
]

request_options_assertions = [
    (1, TypeError),
    (True, TypeError),
    ([], TypeError),
    (lambda: {}, TypeError),
    ("string", TypeError),
    ({"timeout": "plur"}, pydantic.ValidationError),
    ({"timeout": True}, TypeError),
    ({"timeout": {}}, pydantic.ValidationError),
    ({"timeout": []}, pydantic.ValidationError),
    ({"timeout": -1}, BeeArgumentError),
    ({"retry": "plur"}, pydantic.ValidationError),
    ({"retry": True}, TypeError),
    ({"retry": {}}, pydantic.ValidationError),
    ({"retry": []}, pydantic.ValidationError),
    ({"retry": -1}, BeeArgumentError),
]

data_assertions: list[tuple] = [
    (1, TypeError),
    (True, TypeError),
    (None, TypeError),
    (lambda: {}, TypeError),
    ({}, TypeError),
]


reference_or_ens_test_data = [
    (1, TypeError),
    (True, TypeError),
    ({}, TypeError),
    (None, TypeError),
    ([], TypeError),
    # Not an valid hexstring (ZZZ)
    ("ZZZfb5a872396d9693e5c9f9d7233cfa93f395c093371017ff44aa9ae6564cdd", TypeError),
    # Prefixed hexstring is not accepted
    ("0x634fb5a872396d9693e5c9f9d7233cfa93f395c093371017ff44aa9ae6564cdd", TypeError),
    # Length mismatch
    ("4fb5a872396d9693e5c9f9d7233cfa93f395c093371017ff44aa9ae6564cdd", TypeError),
    # ENS with invalid characters
    ("", TypeError),
    ("some space.eth", TypeError),
    ("http://example.eth", TypeError),
]


upload_options_assertions: list[tuple] = [
    (1, TypeError),
    (True, TypeError),
    ([], TypeError),
    ("string", TypeError),
    ({"pin": "plur"}, pydantic.ValidationError),
    ({"pin": 1}, TypeError),
    ({"pin": {}}, pydantic.ValidationError),
    ({"pin": []}, pydantic.ValidationError),
    ({"encrypt": "plur"}, pydantic.ValidationError),
    ({"encrypt": 1}, TypeError),
    ({"encrypt": {}}, pydantic.ValidationError),
    ({"encrypt": []}, pydantic.ValidationError),
    ({"tag": "plur"}, pydantic.ValidationError),
    ({"tag": True}, TypeError),
    ({"tag": {}}, pydantic.ValidationError),
    ({"tag": []}, pydantic.ValidationError),
    ({"tag": -1}, BeeArgumentError),
]


file_data_assertions: list[tuple] = [
    (1, TypeError),
    (True, TypeError),
    (None, TypeError),
    ([], TypeError),
    ({}, TypeError),
    ({"name": "some file"}, TypeError),
    ({"pipe": lambda: None}, TypeError),
]


file_upload_option_assertions: list[tuple] = [
    ({"content_type": True}, pydantic.ValidationError),
    ({"content_type": 1}, pydantic.ValidationError),
    ({"content_type": {}}, pydantic.ValidationError),
    ({"content_type": []}, pydantic.ValidationError),
    ({"size": "plur"}, pydantic.ValidationError),
    ({"size": True}, TypeError),
    ({"size": {}}, pydantic.ValidationError),
    ({"size": []}, pydantic.ValidationError),
    ({"size": -1}, ValueError),
]


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

    assert str(reference.cid()) == test_chunk_encrypted_reference_cid


@pytest.mark.parametrize("input_value, expected_error_type", batch_id_assertion_data)
def test_upload_data_batch_id_assertion(input_value, expected_error_type):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.upload_data(input_value, "")


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_upload_data_request_options_assertions_with_test_data(input_value, expected_error_type, test_batch_id):
    with pytest.raises(expected_error_type):
        bee = Bee(MOCK_SERVER_URL, input_value)
        bee.upload_data(test_batch_id, "", None, input_value)


@pytest.mark.parametrize("input_value, expected_error_type", data_assertions)
def test_upload_data_data_assertsions(input_value, expected_error_type, test_batch_id):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.upload_data(test_batch_id, input_value)


@pytest.mark.parametrize("input_value, expected_error_type", upload_options_assertions)
def test_upload_options_assertions(input_value, expected_error_type, test_batch_id):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.upload_data(test_batch_id, "", input_value)


@pytest.mark.parametrize("input_value, expected_error_type", reference_or_ens_test_data)
def test_download_data_reference_or_ens_assertions(input_value, expected_error_type):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.download_data(input_value)


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_download_data_request_options_assertions(input_value, expected_error_type, test_chunk_hash_str):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.download_data(test_chunk_hash_str, input_value)


@patch("bee_py.bee.Bee")
def test_accept_valid_ens_domain(mock_bee, requests_mock):
    test_json_ens = "example.eth"
    test_json_string_payload = "testing.eth"

    requests_mock.get("http://localhost:12345/bytes/example.eth", text=test_json_string_payload, status_code=200)

    bee_instance = mock_bee.return_value
    bee_instance.download_data.return_value.text.return_value = test_json_string_payload

    bee = Bee(MOCK_SERVER_URL)
    result = bee.download_data(test_json_ens)

    assert result.text() == test_json_string_payload


@patch("bee_py.bee.Bee")
def test_accept_valid_ens_sub_domain(mock_bee, requests_mock):
    test_json_ens = "subdomain.example.eth"
    test_json_string_payload = "testing.eth"

    requests_mock.get(
        "http://localhost:12345/bytes/subdomain.example.eth", text=test_json_string_payload, status_code=200
    )

    bee_instance = mock_bee.return_value
    bee_instance.download_data.return_value.text.return_value = test_json_string_payload

    bee = Bee(MOCK_SERVER_URL)
    result = bee.download_data(test_json_ens)

    assert result.text() == test_json_string_payload


def test_fail_for_small_data(test_batch_id):
    content = bytes([1, 2, 3, 4, 5, 6, 7])

    bee = Bee(MOCK_SERVER_URL)

    with pytest.raises(BeeArgumentError):
        bee.upload_chunk(test_batch_id, content)


def test_fail_chunk_big_data(test_batch_id):
    chunk_size = 4096
    span_size = 512

    bee = Bee(MOCK_SERVER_URL)

    with pytest.raises(BeeArgumentError):
        bee.upload_chunk(test_batch_id, bytes(chunk_size + span_size + 1))


@pytest.mark.parametrize("input_value, expected_error_type", reference_or_ens_test_data)
def test_download_readable_data_reference_or_ens_assertions(input_value, expected_error_type):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.download_readable_data(input_value)


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_download_readable_data_request_options_assertion(input_value, expected_error_type, test_chunk_hash):
    with pytest.raises(expected_error_type):
        bee = Bee(MOCK_SERVER_URL, input_value)
        bee.download_readable_data(test_chunk_hash, input_value)


# * upload_file
@pytest.mark.parametrize("input_value, expected_error_type", batch_id_assertion_data)
def test_upload_file_batch_id_assertion(input_value, expected_error_type):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.upload_file(input_value, "")


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_upload_file_request_option_assertion(input_value, expected_error_type, test_batch_id):
    with pytest.raises(expected_error_type):
        bee = Bee(MOCK_SERVER_URL, input_value)
        bee.upload_file(test_batch_id, "", None, None, input_value)


@pytest.mark.parametrize("input_value, expected_error_type", file_data_assertions)
def test_upload_file_file_data_assertion(input_value, expected_error_type, test_batch_id):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.upload_file(test_batch_id, input_value)


# TODO: Check this one out later
# @pytest.mark.parametrize("input_value, expected_error_type", upload_options_assertions)
# def test_upload_file_upload_options_assertion(input_value, expected_error_type, test_batch_id):
#     bee = Bee(MOCK_SERVER_URL)
#     with pytest.raises(expected_error_type):
#         bee.upload_file(test_batch_id, "", None, input_value)


@pytest.mark.parametrize("input_value, expected_error_type", file_upload_option_assertions)
def test_upload_file_file_upload_options_assertion(input_value, expected_error_type, test_batch_id):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.upload_file(test_batch_id, "", None, input_value)


# * download_file
@pytest.mark.parametrize("input_value, expected_error_type", reference_or_ens_test_data)
def test_downalod_file_reference_or_ens_assertion(input_value, expected_error_type):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.download_file(input_value)


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_downalod_file_request_options_assertion(input_value, expected_error_type, test_chunk_hash_str):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.download_file(test_chunk_hash_str, "", input_value)


@pytest.mark.parametrize("input_value, expected_error_type", reference_or_ens_test_data)
def test_downalod_redable_data_file_assertion(input_value, expected_error_type):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.download_readable_file(input_value)


@pytest.mark.parametrize("input_value, expected_error_type", reference_or_ens_test_data)
def test_downalod_redable_data_file_request_options_assertion(input_value, expected_error_type, test_chunk_hash):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.download_readable_file(test_chunk_hash, "", input_value)


# * upload_files
@pytest.mark.parametrize("input_value, expected_error_type", batch_id_assertion_data)
def test_upload_files_batch_id_assertion(input_value, expected_error_type, create_fake_file):
    bee = Bee(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.upload_files(input_value, [create_fake_file])


# TODO:
# @pytest.mark.parametrize("input_value, expected_error_type", file_upload_option_assertions)
# def test_upload_files_upload_options_assertion(input_value, expected_error_type, create_fake_file, test_batch_id):
#     bee = Bee(MOCK_SERVER_URL)
#     with pytest.raises(expected_error_type):
#         bee.upload_files(test_batch_id, [create_fake_file], input_value)

