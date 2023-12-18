import pytest
import requests

from bee_py.modules.bzz import download_file, upload_collection, upload_file
from bee_py.modules.tag import create_tag, retrieve_tag
from bee_py.types.type import ENCRYPTED_REFERENCE_HEX_LENGTH, Reference
from bee_py.utils.collection_node import make_collection_from_fs

BIG_FILE_TIMEOUT = 100_000


def test_store_and_retrieve_collection_with_single_file(bee_ky_options, get_debug_postage):
    directory_structure = [{"path": "0", "data": bytes([0])}]

    result = upload_collection(bee_ky_options, directory_structure, get_debug_postage)
    file = download_file(bee_ky_options, result.reference, directory_structure[0]["path"])  # type: ignore

    assert file.headers.name == directory_structure[0]["path"]
    assert file.data == directory_structure[0]["data"]


def test_retrieve_the_filename_but_not_the_complete_path(bee_ky_options, get_debug_postage):
    path = "a/b/c/d/"
    name = "0"

    directory_structure = [
        {
            "path": f"{path}{name}",
            "data": bytes([0]),
        },
    ]

    result = upload_collection(bee_ky_options, directory_structure, get_debug_postage)
    file = download_file(bee_ky_options, result.reference, directory_structure[0]["path"])  # type: ignore

    assert file.headers.name == name
    assert file.data == directory_structure[0]["data"]


def test_work_with_pinning(bee_ky_options, get_debug_postage):
    directory_structure = [
        {
            "path": "0",
            "data": bytes([0]),
        },
    ]

    result = upload_collection(bee_ky_options, directory_structure, get_debug_postage, {"pin": True})
    file = download_file(bee_ky_options, result.reference, directory_structure[0]["path"])  # type: ignore

    assert file.headers.name == directory_structure[0]["path"]
    assert file.data == directory_structure[0]["data"]


def test_upload_and_download_with_encryption(bee_ky_options, get_debug_postage):
    directory_structure = [
        {
            "path": "0",
            "data": bytes([0]),
        },
    ]

    result = upload_collection(
        bee_ky_options,
        directory_structure,
        get_debug_postage,
        {
            "encrypt": True,
        },
    )
    file = download_file(bee_ky_options, result.reference, directory_structure[0]["path"])  # type: ignore

    assert file.headers.name == directory_structure[0]["path"]
    assert file.data == directory_structure[0]["data"]
    assert len(result.reference) == ENCRYPTED_REFERENCE_HEX_LENGTH


@pytest.mark.timeout(BIG_FILE_TIMEOUT)
def test_upload_large_file(bee_ky_options, get_debug_postage):
    directory_structure = [
        {
            "path": "0",
            "data": bytes(32 * 1024 * 1024),
        },
    ]

    result = upload_collection(bee_ky_options, directory_structure, get_debug_postage)

    assert isinstance(str(result.reference), str)
    assert isinstance(result.tag_uid, int)


def test_store_retrieve_multiple_file(bee_ky_options, get_debug_postage):
    directory_structure = [
        {
            "path": "0",
            "data": bytes(0),
        },
        {
            "path": "1",
            "data": bytes([1]),
        },
    ]

    result = upload_collection(bee_ky_options, directory_structure, get_debug_postage)

    file1 = download_file(bee_ky_options, result.reference, directory_structure[0]["path"])  # type: ignore

    assert file1.headers.name == directory_structure[0]["path"]
    assert file1.data == directory_structure[0]["data"]

    file2 = download_file(bee_ky_options, result.reference, directory_structure[1]["path"])  # type: ignore

    assert file2.headers.name == directory_structure[1]["path"]
    assert file2.data == directory_structure[1]["data"]


def test_store_and_retrieve_collection_with_index_document(bee_ky_options, get_debug_postage):
    directory_structure = [
        {
            "path": "0",
            "data": bytes(0),
        },
        {
            "path": "1",
            "data": bytes([1]),
        },
    ]

    result = upload_collection(bee_ky_options, directory_structure, get_debug_postage, {"indexDocument": "0"})
    index_file = download_file(bee_ky_options, result.reference)

    assert index_file.headers.name == directory_structure[0]["path"]
    assert index_file.data == directory_structure[0]["data"]


def test_store_and_retrieve_collection_with_error_document(bee_ky_options, get_debug_postage):
    directory_structure = [
        {
            "path": "0",
            "data": bytes(0),
        },
        {
            "path": "1",
            "data": bytes([1]),
        },
    ]

    result = upload_collection(bee_ky_options, directory_structure, get_debug_postage, {"errorDocument": "0"})
    index_file = download_file(bee_ky_options, result.reference, "error")

    assert index_file.headers.name == directory_structure[0]["path"]
    assert index_file.data == directory_structure[0]["data"]


def test_store_and_retrieve_actual_directory(bee_ky_options, get_debug_postage, get_data_folder):
    path = get_data_folder
    directory = f"{path}"
    file3_name = "3.txt"
    sub_dir = "sub/"
    data = bytes([51, 10])

    directory_structure = make_collection_from_fs(directory)
    result = upload_collection(bee_ky_options, directory_structure, get_debug_postage)

    file3 = download_file(bee_ky_options, result.reference, f"{sub_dir}{file3_name}")
    assert file3.headers.name == file3_name
    assert file3.data == data


def test_should_store_and_retrieve_actual_directory_with_index_document(
    bee_ky_options, get_data_folder, get_debug_postage
):
    path = get_data_folder
    directory = f"{path}"
    file_name = "1.txt"
    data = bytes([49, 10])

    directory_structure = make_collection_from_fs(directory)
    result = upload_collection(
        bee_ky_options,
        directory_structure,
        get_debug_postage,
        {"indexDocument": file_name},
    )
    file = download_file(bee_ky_options, result.reference)

    assert file.headers.name == file_name
    assert file.data == data


def test_should_store_and_retrieve_file(bee_ky_options, get_debug_postage):
    data = b"hello world"
    filename = "hello.txt"

    result = upload_file(bee_ky_options, data, get_debug_postage, filename)
    file_data = download_file(bee_ky_options, result.reference)

    assert file_data.data.decode() == data.decode()
    assert file_data.headers.name == filename


def test_should_store_file_without_filename(bee_ky_options, get_debug_postage):
    data = "hello world"

    result = upload_file(bee_ky_options, data, get_debug_postage)
    file_data = download_file(bee_ky_options, result.reference)

    assert file_data.data.decode() == data


def test_should_store_readable_file(bee_ky_options, get_debug_postage, random_byte_array):
    filename = "hello.txt"
    data = random_byte_array

    result = upload_file(
        bee_ky_options,
        data,
        get_debug_postage,
        filename,
        {
            "size": len(data),
        },
    )
    file_data = download_file(bee_ky_options, result.reference)

    assert file_data.data == data


def test_store_file_with_tag(bee_ky_options, get_debug_postage, random_byte_array):
    """
    Relates to how many chunks is uploaded which depends on manifest serialization.
    https://github.com/ethersphere/bee/pull/1501#discussion_r611385602
    """
    expected_tags_count = 4

    data = random_byte_array
    filename = "hello.txt"

    tag1 = create_tag(bee_ky_options)
    upload_file(bee_ky_options, data, get_debug_postage, filename, {"tag": tag1.uid})
    tag2 = retrieve_tag(bee_ky_options, tag1.uid)

    # * For older version of the API
    if tag2.split == 0:
        assert tag2.total == expected_tags_count
        assert tag2.seen == 0
    # * Newer version of the API
    else:
        assert tag2.split == expected_tags_count
        assert tag2.synced == 0


@pytest.mark.timeout(BIG_FILE_TIMEOUT)
def test_fail_time_out_error(bee_ky_options, invalid_reference):
    with pytest.raises(requests.exceptions.HTTPError, match="404 Client Error"):
        download_file(bee_ky_options, invalid_reference)


@pytest.mark.timeout(BIG_FILE_TIMEOUT)
def test_upload_bigger_file(bee_ky_options, get_debug_postage):
    # * create a bytearray of 32MB
    data = bytearray(32 * 1024 * 1024)

    response = upload_file(bee_ky_options, data, get_debug_postage)

    assert isinstance(response.reference, Reference)
    assert isinstance(response.tag_uid, int)
