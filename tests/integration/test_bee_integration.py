# from unittest.mock import MagicMock, patch

# import pydantic
import random
from datetime import datetime, timezone
from pathlib import Path
from time import sleep

import pytest
import requests

from bee_py.bee import Bee
from bee_py.Exceptions import PinNotFoundError
from bee_py.feed.topic import make_topic_from_string
from bee_py.feed.type import FeedType
from bee_py.types.type import (
    CHUNK_SIZE,
    REFERENCE_HEX_LENGTH,
    SPAN_SIZE,
    BatchId,
    BeeRequestOptions,
    Collection,
    CollectionEntry,
    CollectionUploadOptions,
    GetAllPinResponse,
    PssMessageHandler,
    ReferenceResponse,
    UploadOptions,
)
from bee_py.utils.error import BeeArgumentError, BeeError

# * Global variables
ERR_TIMEOUT = 40_000


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

    result = bee_class.upload_file(get_debug_postage, content, name)
    downloaded_file = bee_class.download_file(str(result.reference))

    assert downloaded_file.headers.name == name
    assert downloaded_file.data == content


def test_work_with_directory_unicode_file_names(bee_class, get_debug_postage, data_folder):
    result = bee_class.upload_files_from_directory(get_debug_postage, data_folder)

    assert len(result.reference) == REFERENCE_HEX_LENGTH


def test_work_with_directory_unicode_file_names_direct_upload(bee_class, get_debug_postage, data_folder):
    result = bee_class.upload_files_from_directory(get_debug_postage, data_folder, {"deferred": False})

    assert len(result.reference) == REFERENCE_HEX_LENGTH


def test_upload_collection(bee_class, get_debug_postage):
    directory_structure = Collection(
        entries=[CollectionEntry.model_validate({"path": "0", "data": bytearray(b"hello-world")})]
    )

    result = bee_class.upload_collection(get_debug_postage, directory_structure)
    file = bee_class.download_file(str(result.reference), directory_structure.entries[0].path)

    assert file.headers.name == directory_structure.entries[0].path
    assert file.data.decode() == "hello-world"


def test_upload_collection_CIDs_support(bee_class, get_debug_postage):  # noqa: N802
    directory_structure = Collection(
        entries=[CollectionEntry.model_validate({"path": "0", "data": bytearray(b"hello-world")})]
    )

    result = bee_class.upload_collection(get_debug_postage, directory_structure)
    file = bee_class.download_file(str(result.cid()), directory_structure.entries[0].path)

    assert file.headers.name == directory_structure.entries[0].path
    assert file.data.decode() == "hello-world"


def test_list_tags(bee_class):
    original_tags = bee_class.get_all_tags({"limit": 1000})
    bee_class.create_tag()
    updated_tags = bee_class.get_all_tags({"limit": 1000})

    assert updated_tags[0] != original_tags[0]


def test_retreive_previously_created_empty_tags(bee_class):
    tag1 = bee_class.create_tag()
    tag2 = bee_class.retrieve_tag(tag1)

    assert tag1 == tag2


def test_delete_tags(bee_class):
    created_tag = bee_class.create_tag()
    original_tags = bee_class.get_all_tags({"limit": 1000})

    bee_class.delete_tag(created_tag)

    try:
        assert created_tag.uid != original_tags[0].uid
    except:  # noqa: E722
        assert created_tag.tag_uid != original_tags[0].tag_uid


def test_list_all_pins(bee_class, get_debug_postage):
    content = bytes([1, 2, 3])
    result = bee_class.upload_file(get_debug_postage, content)

    # * Nothing is asserted as nothing is returned, will throw error if something is wrong
    bee_class.pin(str(result.reference))

    pinned_chunks = bee_class.get_all_pins()
    pinned_chunks_references = [str(refs) for refs in pinned_chunks.references]

    assert isinstance(pinned_chunks, GetAllPinResponse)
    assert str(result.reference) in pinned_chunks_references


def test_get_pinning_status(bee_class, get_debug_postage):
    content = bytes(random_byte_array(16, datetime.now(tz=timezone.utc)))
    result = bee_class.upload_file(get_debug_postage, content, "test", {"pin": False})

    with pytest.raises(PinNotFoundError):
        bee_class.get_pin(str(result.reference))

    # * Nothing is asserted as nothing is returned, will throw error if something is wrong
    bee_class.pin(str(result.reference))

    status_after_pinnig = bee_class.get_pin(str(result.reference))

    assert status_after_pinnig.reference


def test_pin_and_unpin(bee_class, get_debug_postage):
    content = bytes([1, 2, 3])
    result = bee_class.upload_file(get_debug_postage, content)

    # * Nothing is asserted as nothing is returned, will throw error if something is wrong
    bee_class.pin(str(result.reference))
    bee_class.unpin(str(result.reference))


def test_pin_unpin_collection_from_directory(bee_class, get_debug_postage, data_folder):
    result = bee_class.upload_files_from_directory(get_debug_postage, data_folder)

    # * Nothing is asserted as nothing is returned, will throw error if something is wrong
    bee_class.pin(str(result.reference))
    bee_class.unpin(str(result.reference))


# ? Test stewardship
def test_reupload_pinned_data(bee_class, get_debug_postage):
    content = bytes(random_byte_array(16, datetime.now(tz=timezone.utc)))
    result = bee_class.upload_file(get_debug_postage, content, "test", {"pin": True})

    # * Does not return anything, but will throw exception if something is going wrong
    bee_class.reupload_pinned_data(str(result.reference))


@pytest.mark.timeout(ERR_TIMEOUT)
def test_if_reference_is_retrievable(bee_class, get_debug_postage):
    content = bytes(random_byte_array(16, datetime.now(tz=timezone.utc)))
    result = bee_class.upload_file(get_debug_postage, content, "test", {"pin": True})

    assert bee_class.is_reference_retrievable(str(result.reference)) is True

    # * Reference that has correct form, but should not exist on the network
    assert (
        bee_class.is_reference_retrievable("ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4332") is False
    )


# @pytest.mark.timeout(ERR_TIMEOUT)
# def test_send_receive_data(bee_class, get_debug_postage):
#     topic = "bee-class-topic"
#     message = bytes([1, 2, 3])
# ! need bee debug


@pytest.mark.timeout(ERR_TIMEOUT)
def test_write_two_updates(bee_url, get_debug_postage, signer):
    topic = bytes(random_byte_array(32, datetime.now(tz=timezone.utc)))
    bee_class = Bee(bee_url, {"signer": signer})

    feed = bee_class.make_feed_writer("sequence", topic, signer)
    reference_zero = bytes([0] * 32)

    feed.upload(get_debug_postage, reference_zero)
    feed_reader = bee_class.make_feed_reader("sequence", topic, signer)
    first_update_reference_response = feed_reader.download()

    assert str(first_update_reference_response) == reference_zero.hex()
    assert first_update_reference_response.feed_index == "0000000000000000"
