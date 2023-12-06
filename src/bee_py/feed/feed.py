import datetime
from typing import NewType, Optional, Union

from ape.managers.accounts import AccountAPI
from eth_typing import ChecksumAddress as AddressType
from pydantic import BaseModel

from bee_py.chunk.serialize import serialize_bytes
from bee_py.chunk.soc import make_single_owner_chunk_from_data, upload_single_owner_chunk_data
from bee_py.feed.identifiers import make_feed_identifier
from bee_py.feed.type import FeedType
from bee_py.modules.bytes import read_big_endian, write_big_endian
from bee_py.modules.chunk import download
from bee_py.modules.feed import fetch_latest_feed_update
from bee_py.types.type import (  # Reference,
    FEED_INDEX_HEX_LENGTH,
    BatchId,
    BeeRequestOptions,
    FeedType,
    FeedUpdateOptions,
    FeedWriter,
    MakeFeedReader,
    Reference,
    Topic,
)
from bee_py.utils.bytes import bytes_at_offset, make_bytes
from bee_py.utils.eth import make_hex_eth_address
from bee_py.utils.hash import keccak256_hash
from bee_py.utils.hex import bytes_to_hex, make_hex_string
from bee_py.utils.reference import make_bytes_reference

TIMESTAMP_PAYLOAD_OFFSET = 0
TIMESTAMP_PAYLOAD_SIZE = 8
REFERENCE_PAYLOAD_OFFSET = TIMESTAMP_PAYLOAD_SIZE


IndexBytes = NewType("IndexBytes", bytes)


class Epoch(BaseModel):
    """
    Epoch model.

    :param time: The time of the epoch.
    :type time: int
    :param level: The level of the epoch.
    :type level: int
    """

    time: int
    level: int


class Index(BaseModel):
    """
    Index model.

    :param index: The index can be a number, an epoch, index bytes or a string.
    :type index: Union[int, Epoch, bytes, str]
    """

    index: Union[int, Epoch, bytes, str]


class FeedUpdate(BaseModel):
    """
    Represents a feed update.

    Attributes:
        timestamp: The timestamp of the update.
        reference: The reference of the update.
    """

    timestamp: int
    reference: bytes


def find_next_index(
    request_options: BeeRequestOptions,
    owner: AddressType,
    topic: Topic,
    options: Optional[FeedUpdateOptions] = None,
) -> bytes:
    """
    Fetches the latest feed update and returns the next feed index.

    Args:
        request_options (AsyncClient): The HTTP client instance for making requests to the Bee API.
        owner (bytes): The owner of the feed.
        topic (bytes): The topic of the feed.
        options (Optional[FeedUpdateOptions]): Additional options for fetching the latest feed update.

    Returns:
        bytes: The next feed index.
    """

    try:
        feed_update = fetch_latest_feed_update(request_options, owner, topic, options)
        return make_hex_string(feed_update.feed_index_next, FEED_INDEX_HEX_LENGTH)
    except Exception as e:
        if e.response.status_code == 404:  # noqa: PLR2004
            return bytes_to_hex(make_bytes(8))
        raise e


def update_feed(
    request_options: BeeRequestOptions,
    signer: AccountAPI,
    topic: Topic,
    reference: Reference,
    postage_batch_id: BatchId,
    options: Optional[FeedUpdateOptions] = None,
    index: str = "latest",
):
    """
    Updates a feed.

    :param request_options: The request options.
    :type request_options: BeeRequestOptions
    :param signer: The signer.
    :type signer: Signer
    :param topic: The topic.
    :type topic: Topic
    :param reference: The reference.
    :type reference: BytesReference
    :param postage_batch_id: The postage batch ID.
    :type postage_batch_id: BatchId
    :param options: The options for uploading the feed (default is None).
    :type options: FeedUploadOptions
    :param index: The index (default is 'latest').
    :type index: Index
    :return: The reference.
    :rtype: Reference
    """
    owner_hex = make_hex_eth_address(signer.address)
    next_index = index if index != "latest" else find_next_index(request_options, owner_hex, topic, options)

    identifier = make_feed_identifier(topic, next_index)
    at = options.at if options and options.at else datetime.now().timestamp()
    timestamp = write_big_endian(at)
    payload_bytes = serialize_bytes(timestamp, reference)

    return upload_single_owner_chunk_data(request_options, signer, postage_batch_id, identifier, payload_bytes, options)


def get_feed_update_chunk_reference(owner: AddressType, topic: Topic, index: Index) -> bytes:
    """
    Gets the feed update chunk reference.

    :param owner: The owner.
    :type owner: EthAddress
    :param topic: The topic.
    :type topic: Topic
    :param index: The index.
    :type index: Index
    :return: The feed update chunk reference.
    :rtype: PlainBytesReference
    """
    identifier = make_feed_identifier(topic, index)

    return keccak256_hash(identifier, owner)


def download_feed_update(
    request_options: BeeRequestOptions, owner: AddressType, topic: Topic, index: Index
) -> FeedUpdate:
    """
    Downloads a feed update.

    :param request_options: The request options.
    :type request_options: BeeRequestOptions
    :param owner: The owner.
    :type owner: EthAddress
    :param topic: The topic.
    :type topic: Topic
    :param index: The index.
    :type index: Index
    :return: The feed update.
    :rtype: FeedUpdate
    """
    address = get_feed_update_chunk_reference(owner, topic, index)
    address_hex = bytes_to_hex(address)
    data = download(request_options, address_hex)
    soc = make_single_owner_chunk_from_data(data, address)
    payload = soc.payload
    timestamp_bytes = bytes_at_offset(payload, TIMESTAMP_PAYLOAD_OFFSET, TIMESTAMP_PAYLOAD_SIZE)
    timestamp = read_big_endian(timestamp_bytes)
    reference = make_bytes_reference(payload, REFERENCE_PAYLOAD_OFFSET)

    return FeedUpdate(timestamp=timestamp, reference=reference)


def make_feed_reader(
    request_options: BeeRequestOptions,
    _type: FeedType,
    topic: Topic,
    owner: AddressType,
    options: Optional[FeedUpdateOptions] = None,
) -> MakeFeedReader:
    """
    Creates a new feed reader object.

    Args:
        request_options (AsyncClient): The HTTP client instance for making requests to the Bee API.
        type (str): The type of feed.
        topic (bytes): The topic of the feed.
        owner (bytes): The owner of the feed.

    Returns:
        FeedReader: The feed reader object.
    """
    return MakeFeedReader(request_options=request_options, Type=_type, owner=owner, topic=topic, options=options)


def make_feed_writer(
    request_options: BeeRequestOptions, _type: FeedType, topic: Topic, signer: AccountAPI
) -> FeedWriter:
    """
    Creates a new feed writer object.

    Args:
        request_options (BeeRequestOptions): The HTTP client instance for making requests to the Bee API.
        type (FeedType): The type of feed.
        topic (Topic): The topic of the feed.
        signer (AccountAPI): The account to sign.

    Returns:
        FeedWriter: The feed writer object.
    """
    return FeedWriter(request_options=request_options, type=_type, topic=topic, signer=signer)
