import pytest

from bee_py.modules.bzz import download_file, extract_file_upload_headers, upload_collection
from bee_py.modules.tag import create_tag
from bee_py.types.type import ENCRYPTED_REFERENCE_HEX_LENGTH

# d63ff7833b8f6fb69f49e69bb5ed53428399aa03c510a801d52e046be1a56456
BIG_FILE_TIMEOUT = 100_000


def test_store_and_retrieve_collection_with_single_file(bee_ky_options, get_debug_postage):
    directory_structure = [{"path": "0", "data": bytes([0])}]

    result = upload_collection(bee_ky_options, directory_structure, get_debug_postage)
    file = download_file(bee_ky_options, result.reference, directory_structure[0]["path"])

    assert file.headers.name == directory_structure[0]["path"]
    assert file.data.encode() == directory_structure[0]["data"]


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
    file = download_file(bee_ky_options, result.reference, directory_structure[0]["path"])

    assert file.headers.name == name
    assert file.data.encode() == directory_structure[0]["data"]


def test_work_with_pinning(bee_ky_options):
    get_debug_postage = "d63ff7833b8f6fb69f49e69bb5ed53428399aa03c510a801d52e046be1a56456"
    directory_structure = [
        {
            "path": "0",
            "data": bytes([0]),
        },
    ]

    result = upload_collection(bee_ky_options, directory_structure, get_debug_postage, {"pin": True})
    file = download_file(bee_ky_options, result.reference, directory_structure[0]["path"])

    assert file.headers.name == directory_structure[0]["path"]
    assert file.data.encode() == directory_structure[0]["data"]


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
    file = download_file(bee_ky_options, result.reference, directory_structure[0]["path"])

    assert file.headers.name == directory_structure[0]["path"]
    assert file.data.encode() == directory_structure[0]["data"]
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

    file1 = download_file(bee_ky_options, result.reference, directory_structure[0]["path"])

    assert file1.headers.name == directory_structure[0]["path"]
    assert file1.data.encode() == directory_structure[0]["data"]

    file2 = download_file(bee_ky_options, result.reference, directory_structure[1]["path"])

    assert file2.headers.name == directory_structure[1]["path"]
    assert file2.data.encode() == directory_structure[1]["data"]


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
    index_file = download_file(bee_ky_options, result.reference, directory_structure[0]["path"])

    assert index_file.headers.name == directory_structure[0]["path"]
    assert index_file.data.encode() == directory_structure[0]["data"]


# Test from here
def test_store_and_retrieve_collection_with_error_document(bee_ky_options):
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
    assert index_file.data.encode() == directory_structure[0]["data"]


def test_store_and_retrieve_actual_directory(bee_ky_options, get_debug_postage, get_data_folder):
    path = get_data_folder
    directory = f"{path}"
    file3_name = "3.txt"
    sub_dir = "sub/"
    data = bytes([51, 10])

    # directory_structure = makeCollectionFromFS(directory)
    result = upload_collection(bee_ky_options, directory_structure, get_debug_postage)

    file3 = download_file(bee_ky_options, result.reference, f"{sub_dir}{file3_name}")
    assert file3.headers.name == file3_name
    assert file3.data.encode() == data
