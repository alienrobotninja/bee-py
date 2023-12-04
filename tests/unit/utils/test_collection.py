import os

from bee_py.utils.collection import get_collection_size


def test_folder_size():
    size = os.path.getsize("./tests/data")
    assert size > 1


def test_collection_size(create_fake_file):
    files = [create_fake_file]
    size = get_collection_size(files)
    assert size == 32
