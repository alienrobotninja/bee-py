# from unittest.mock import MagicMock, patch

# import pydantic
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