from bee_py.modules.bzz import upload_collection, upload_file
from bee_py.modules.stewardship import reupload


def test_reupload_directory(bee_ky_options, get_debug_postage):
    directory_structure = [
        {
            "path": "0",
            "data": bytearray([0]),
        },
    ]

    result = upload_collection(bee_ky_options, directory_structure, get_debug_postage, {"pin": True})

    # * Does not return anything, but will throw error if something is wrong
    reupload(bee_ky_options, result.reference)


def test_reupload_file(bee_ky_options, get_debug_postage):
    data = "hello world"
    filename = "hello.txt"

    result = upload_file(bee_ky_options, data, get_debug_postage, filename, {"pin": True})

    # *  Does not return anything, but will throw error if something is wrong
    reupload(bee_ky_options, result.reference)
