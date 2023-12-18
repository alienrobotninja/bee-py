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


def test_upload_and_downalod_chunk(bee_class, get_debug_postage):
    content = bytes(bytearray(100))

    referece = bee_class.upload_chunk(get_debug_postage, content)
    downloaded_chunk = bee_class.download_chunk(referece)

    assert downloaded_chunk == content
