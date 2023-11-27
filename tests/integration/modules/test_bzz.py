from bee_py.modules.bzz import download_file, extract_file_upload_headers, upload_collection
from bee_py.modules.tag import create_tag


def test_store_and_retrieve_collection_with_single_file(bee_ky_options):
    directory_structure = [{"path": "0", "data": bytes([0])}]

    get_debug_postage = "061dfc1fc656410f1901e06f5b413039a6923e2747ca7d8cfe23391cd7b86c20"
    result = upload_collection(bee_ky_options, directory_structure, get_debug_postage)
    file = download_file(bee_ky_options, result.reference, directory_structure[0]["path"])

    assert file.headers.name == directory_structure[0]["path"]
    assert file.data.encode() == directory_structure[0]["data"]
