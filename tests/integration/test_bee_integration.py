# from unittest.mock import MagicMock, patch

# import pydantic
import random
from pathlib import Path

import pytest

from bee_py.bee import Bee
from bee_py.feed.topic import make_topic_from_string
from bee_py.feed.type import FeedType
from bee_py.types.type import (
    CHUNK_SIZE,
    REFERENCE_HEX_LENGTH,
    SPAN_SIZE,
    BatchId,
    BeeRequestOptions,
    CollectionUploadOptions,
    PssMessageHandler,
    ReferenceResponse,
    UploadOptions,
)
from bee_py.utils.error import BeeArgumentError, BeeError

# * Global variables


# * Helper Functions
def random_byte_array(length=100, seed=500):
    # * not completely random
    random.seed(seed)
    return bytearray(random.randint(0, 255) for _ in range(length))  # noqa: S311


def sample_file(data: bytes):
    project_path = Path(__file__).parent
    temp_folder = project_path / "../data"
    tmp_file = f"{temp_folder}/tmp_file"  # noqa: S108
    with open(tmp_file, "wb+") as f:
        f.write(data)
    return tmp_file


def test_strip_trailing_slash():
    bee = Bee("http://127.0.0.1:1633/")

    assert bee.url == "http://127.0.0.1:1633"


def test_upload_and_downalod_chunk(bee_class, get_debug_postage, random_byte_array):
    data = bytes(random_byte_array)

    referece = bee_class.upload_chunk(get_debug_postage, data)
    downloaded_chunk = bee_class.download_chunk(referece)

    assert downloaded_chunk.data == data


def test_upload_and_downalod_chunk_with_direct_upload(bee_class, get_debug_postage, random_byte_array):
    content = bytes(random_byte_array)

    referece = bee_class.upload_chunk(get_debug_postage, content, {"deferred": False})
    downloaded_chunk = bee_class.download_chunk(referece)

    assert downloaded_chunk.data == content


def test_work_with_files(bee_class, get_debug_postage):
    content = bytes([1, 2, 3])
    name = "hello.txt"

    result = bee_class.upload_file(get_debug_postage, content, name)
    file = bee_class.download_file(str(result.reference))

    assert file.headers.name == name
    assert file.data == content


def test_work_with_files_and_CIDs(bee_class, get_debug_postage):  # noqa: N802
    content = bytes([1, 2, 3])
    name = "hello.txt"

    result = bee_class.upload_file(get_debug_postage, content, name)
    file = bee_class.download_file(str(result.cid()))

    assert file.headers.name == name
    assert file.data == content


def test_work_with_files_and_direct_upload(bee_class, get_debug_postage):
    content = bytes([1, 2, 3])
    name = "hello.txt"

    result = bee_class.upload_file(get_debug_postage, content, name, {"deferred": False})
    file = bee_class.download_file(str(result.reference))

    assert file.headers.name == name
    assert file.data == content


def test_work_with_files_and_tags(bee_class, get_debug_postage):
    tag = bee_class.create_tag()
    name = "hello.txt"
    # * Should fit into 4 chunks
    content = bytes(random_byte_array(13000))

    result = bee_class.upload_file(get_debug_postage, content, name, {"tag": tag.uid})
    file = bee_class.download_file(str(result.reference))

    assert file.headers.name == name
    assert file.data == content

    retrieve_tag = bee_class.retrieve_tag(tag)
    # ? Backwards compatibility for older versions of Bee API
    if retrieve_tag.split == 0:
        assert retrieve_tag.processed == 8
    else:
        assert retrieve_tag.split == 8


def test_should_work_with_file_object(bee_class, get_debug_postage):
    content = bytes([1, 2, 3])
    name = "hello.txt"

    input_file = sample_file(content)

    with open(input_file, "rb") as f:
        content = f.read()

    result = bee_class.upload_file(get_debug_postage, content)
    downloaded_file = bee_class.download_file(str(result.reference))

    print(downloaded_file)

    assert downloaded_file.headers.name == name
    assert downloaded_file.data == content

    input_file.unlink()
