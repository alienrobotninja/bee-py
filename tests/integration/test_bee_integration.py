import json
import random

# import time
from pathlib import Path

import pytest
import requests

from bee_py.bee import Bee
from bee_py.chunk.soc import make_soc_address
from bee_py.Exceptions import PinNotFoundError
from bee_py.modules import bzz
from bee_py.types.type import REFERENCE_HEX_LENGTH, Collection, CollectionEntry, GetAllPinResponse
from bee_py.utils.eth import make_eth_address

# * Global variables
ERR_TIMEOUT = 40_000
test_chunk_payload = bytes([1, 2, 3])
test_json_hash = "5a424d833847b8fe977c5c7ca205cd018f29c003c95db24f48e962d535aa3523"
test_json_payload = [{"some": "Json Object"}]
TOPIC = "some=very%nice#topic"


# * Helper Functions
def random_byte_array(length=100):
    # * not completely random
    random.seed(500)
    return bytearray(random.randint(0, 255) for _ in range(length))  # noqa: S311


def sample_file(data: bytes):
    project_path = Path(__file__).parent
    temp_folder = project_path / "../data"
    tmp_file = f"{temp_folder}/tmp_file"  # noqa: S108
    with open(tmp_file, "wb+") as f:
        f.write(data)
    return tmp_file


# * Global Settings for testing
existing_topic = bytes(random_byte_array(32))
updates: list = [
    {"index": "0000000000000000", "reference": bytes([0] * 32)},
    {
        "index": "0000000000000001",
        "reference": bytes(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        ),
    },
    {
        "index": "0000000000000002",
        "reference": bytes(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
        ),
    },
]


# * Tests
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
    content = bytes(random_byte_array(16))
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
    content = bytes(random_byte_array(16))
    result = bee_class.upload_file(get_debug_postage, content, "test", {"pin": True})

    # * Does not return anything, but will throw exception if something is going wrong
    bee_class.reupload_pinned_data(str(result.reference))


@pytest.mark.timeout(ERR_TIMEOUT)
def test_if_reference_is_retrievable(bee_class):
    # content = bytes(random_byte_array(16))
    # result = bee_class.upload_file(get_debug_postage, content, "test", {"pin": True})

    # assert bee_class.is_reference_retrievable(result.reference.value) is True

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
def test_write_updates_reference_zero(bee_url, get_debug_postage, signer):
    topic = bytes(random_byte_array(32))
    bee_class = Bee(bee_url, {"signer": signer})

    feed = bee_class.make_feed_writer("sequence", topic, signer)
    reference_zero = bytes([0] * 32)

    feed.upload(get_debug_postage, reference_zero)
    feed_reader = bee_class.make_feed_reader("sequence", topic, signer)
    first_update_reference_response = feed_reader.download()

    assert str(first_update_reference_response) == reference_zero.hex()
    assert first_update_reference_response.feed_index == "0000000000000000"


@pytest.mark.timeout(ERR_TIMEOUT)
def test_write_updates_reference_non_zero(bee_url, get_debug_postage, signer):
    topic = bytes(random_byte_array(32))
    bee_class = Bee(bee_url, {"signer": signer})

    feed = bee_class.make_feed_writer("sequence", topic, signer)
    # * with referenceOne
    reference_one = bytes(
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    )
    feed.upload(get_debug_postage, reference_one)
    feed_reader = bee_class.make_feed_reader("sequence", topic, signer)
    first_update_reference_response = feed_reader.download()

    assert str(first_update_reference_response) == reference_one.hex()
    assert first_update_reference_response.feed_index_next == "0000000000000001"


@pytest.mark.timeout(ERR_TIMEOUT)
def test_fail_fetching_non_existing_index(bee_url, get_debug_postage, signer):
    topic = bytes(random_byte_array(32))
    bee_class = Bee(bee_url, {"signer": signer})

    feed = bee_class.make_feed_writer("sequence", topic, signer)
    reference_zero = bytes([0] * 32)

    feed.upload(get_debug_postage, reference_zero)
    feed_reader = bee_class.make_feed_reader("sequence", topic, signer)
    first_update_reference_response = feed_reader.download()

    assert str(first_update_reference_response) == reference_zero.hex()
    assert first_update_reference_response.feed_index == "0000000000000000"

    with pytest.raises(requests.exceptions.HTTPError):
        feed_reader.download({"index": "0000000000000001"})


@pytest.mark.timeout(ERR_TIMEOUT)
def test_create_feeds_manifest_and_retreive_data(bee_url, get_debug_postage, signer, bee_ky_options):
    topic = bytes(random_byte_array(32))
    bee_class = Bee(bee_url, {"signer": signer})
    owner = signer.address

    directory_structure = Collection(
        entries=[CollectionEntry.model_validate({"path": "index.html", "data": bytearray(b"Some Data")})]
    )

    cac_result = bzz.upload_collection(bee_ky_options, directory_structure, get_debug_postage)

    feed = bee_class.make_feed_writer("sequence", topic, signer)
    feed.upload(get_debug_postage, str(cac_result.reference))

    manifest_result = bee_class.create_feed_manifest(get_debug_postage, "sequence", topic, owner)

    assert isinstance(str(manifest_result.reference), str)
    assert manifest_result.cid()

    # * this calls /bzz endpoint that should resolve the manifest and the feed returning the latest feed's content
    file = bee_class.download_file(str(cac_result.reference), "index.html")

    assert file.data.decode() == "Some Data"


def test_create_feed_topic(bee_url, signer):
    owner = signer.address

    bee_class = Bee(bee_url, {"signer": signer})
    topic = bee_class.make_feed_topic("swarm.eth:application:handshake")
    feed = bee_class.make_feed_reader("sequence", topic, owner)

    assert feed.topic == str(topic)


def test_read_and_write(bee_url, signer, get_debug_postage, try_delete_chunk_from_local_storage):
    soc_hash = "6618137d8b33329d36ffa00cb97c130f871cbfe6f406ac63e7a30ae6a56a350f"
    identifier = bytes([0] * 32)
    soc_address = make_soc_address(identifier, make_eth_address(signer.address))
    bee_class = Bee(bee_url, {"signer": signer})

    try_delete_chunk_from_local_storage(soc_address)

    soc_writer = bee_class.make_soc_writer(signer)

    referecne = soc_writer.upload(get_debug_postage, identifier, test_chunk_payload)

    assert referecne.value == soc_hash

    soc = soc_writer.download(identifier)
    payload = soc.payload

    assert payload == test_chunk_payload


def test_fail_not_signer_passed(bee_url, signer):
    with pytest.raises(AttributeError):
        bee_class = Bee(bee_url)
        bee_class.make_soc_writer(signer)


@pytest.mark.timeout(ERR_TIMEOUT)
def test_set_JSON_to_feed(get_debug_postage, bee_url, signer):  # noqa: N802
    bee_class = Bee(bee_url, {"signer": signer})
    bee_class.set_json_feed(get_debug_postage, TOPIC, test_json_payload, signer.address)

    hashed_topic = bee_class.make_feed_topic(TOPIC)
    reader = bee_class.make_feed_reader("sequence", hashed_topic, signer.address)
    chunk_reference_response = reader.download()

    assert chunk_reference_response.reference == test_json_hash

    downloaded_data = bee_class.download_data(chunk_reference_response)

    assert json.loads(downloaded_data.data.decode()) == test_json_payload


@pytest.mark.timeout(ERR_TIMEOUT)
def test_get_JSON_from_feed(get_debug_postage, bee_url, signer):  # noqa: N802
    bee_class = Bee(bee_url, {"signer": signer})
    data = [{"some": {"other": "object"}}]

    hashed_topic = bee_class.make_feed_topic(TOPIC)
    writer = bee_class.make_feed_writer("sequence", hashed_topic, signer.address)
    data_chunk_result = bee_class.upload_data(get_debug_postage, json.dumps(data))

    writer.upload(get_debug_postage, data_chunk_result.reference)

    fetched_data = bee_class.get_json_feed(TOPIC)

    assert json.loads(fetched_data["data"]) == data


@pytest.mark.timeout(ERR_TIMEOUT)
def test_get_JSON_from_feed_with_address(get_debug_postage, bee_url, signer):  # noqa: N802
    bee_class = Bee(bee_url, {"signer": signer})
    data = [{"some": {"other": "object"}}]

    hashed_topic = bee_class.make_feed_topic(TOPIC)
    writer = bee_class.make_feed_writer("sequence", hashed_topic, signer.address)
    data_chunk_result = bee_class.upload_data(get_debug_postage, json.dumps(data))

    writer.upload(get_debug_postage, data_chunk_result.reference)

    fetched_data = bee_class.get_json_feed(TOPIC, {"address": signer.address})

    assert json.loads(fetched_data["data"]) == data
