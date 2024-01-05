from datetime import datetime, timezone
from typing import Optional, Union

import requests
from ape.managers.accounts import AccountAPI
from eth_pydantic_types import HexBytes
from eth_typing import ChecksumAddress as AddressType

from bee_py.chunk.serialize import serialize_bytes
from bee_py.chunk.soc import make_single_owner_chunk_from_data, upload_single_owner_chunk_data
from bee_py.feed.identifiers import make_feed_identifier
from bee_py.feed.type import FeedType
from bee_py.modules.bytes import read_big_endian, write_big_endian
from bee_py.modules.chunk import download
from bee_py.modules.feed import fetch_latest_feed_update
from bee_py.types.type import (
    FEED_INDEX_HEX_LENGTH,
    BatchId,
    BeeRequestOptions,
    FeedReader,
    FeedUpdate,
    FeedUpdateOptions,
    FeedWriter,
    FetchFeedUpdateResponse,
    Index,
    Reference,
    Signer,
    Topic,
)
from bee_py.utils.bytes import bytes_at_offset, make_bytes
from bee_py.utils.eth import make_hex_eth_address
from bee_py.utils.hash import keccak256_hash
from bee_py.utils.hex import bytes_to_hex, hex_to_bytes, make_hex_string
from bee_py.utils.reference import make_bytes_reference

TIMESTAMP_PAYLOAD_OFFSET = 0
TIMESTAMP_PAYLOAD_SIZE = 8
REFERENCE_PAYLOAD_OFFSET = TIMESTAMP_PAYLOAD_SIZE


def find_next_index(
    request_options: BeeRequestOptions,
    owner: Union[AddressType, str],
    topic: Union[Topic, str],
    options: Optional[FeedUpdateOptions] = None,
) -> Union[bytes, str]:
    """
    Fetches the latest feed update and returns the next feed index.

    Args:
        request_options (BeeRequestOptions): The HTTP client instance for making requests to the Bee API.
        owner (bytes): The owner of the feed.
        topic (bytes): The topic of the feed.
        options (Optional[FeedUpdateOptions]): Additional options for fetching the latest feed update.

    Returns:
        bytes | str: The next feed index.
    """

    try:
        feed_update = fetch_latest_feed_update(request_options, owner, topic, options)
        return make_hex_string(feed_update.feed_index_next, FEED_INDEX_HEX_LENGTH)
    except requests.HTTPError as e:
        if e.response.status_code == 404:  # noqa: PLR2004
            return bytes_to_hex(make_bytes(8))
        raise e


def update_feed(
    request_options: BeeRequestOptions,
    signer: AccountAPI,
    topic: Union[Topic, str],
    reference: Union[Reference, str, bytes],
    postage_batch_id: BatchId,
    options: Optional[FeedUpdateOptions] = None,
    index: str = "latest",
) -> Reference:
    """
    Updates a feed.

    :param request_options: The request options.
    :type request_options: BeeRequestOptions
    :param signer: The signer.
    :type signer: Signer
    :param topic: The topic.
    :type topic: Union[Topic,str]
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
    if isinstance(owner_hex, HexBytes):
        owner_hex = owner_hex.hex()
    if isinstance(topic, Topic):
        topic = topic.value
    next_index = index if index != "latest" else find_next_index(request_options, owner_hex, topic, options)

    identifier = make_feed_identifier(topic, next_index)  # type: ignore
    at = options.at if options and options.at else datetime.now(tz=timezone.utc).timestamp()
    timestamp = write_big_endian(int(at))
    if isinstance(reference, Reference):
        reference = reference.value
    if isinstance(reference, str):
        reference = reference.encode()
    payload_bytes = serialize_bytes(timestamp, reference)

    return upload_single_owner_chunk_data(request_options, signer, postage_batch_id, identifier, payload_bytes, options)  # type: ignore # noqa: 501


def get_feed_update_chunk_reference(
    owner: Union[AddressType, bytes, str], topic: Union[Topic, str], index: Index
) -> bytes:
    """
    Gets the feed update chunk reference.

    :param owner: The owner.
    :type owner: EthAddress
    :param topic: The topic.
    :type topic: Union[Topic,str]
    :param index: The index.
    :type index: Index
    :return: The feed update chunk reference.
    :rtype: PlainBytesReference
    """
    identifier = make_feed_identifier(topic, index)
    if not isinstance(owner, bytes):
        owner = hex_to_bytes(owner)

    return keccak256_hash(identifier, owner)


def download_feed_update(
    request_options: BeeRequestOptions, owner: Union[AddressType, bytes, str], topic: Union[Topic, str], index: Index
) -> FeedUpdate:
    """
    Downloads a feed update.

    :param request_options: The request options.
    :type request_options: BeeRequestOptions
    :param owner: The owner.
    :type owner: EthAddress
    :param topic: The topic.
    :type topic: Union[Topic,str]
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
    _type: Union[FeedType, str],
    topic: Union[Topic, str],
    owner: Union[AddressType, str],
    options: Optional[FeedUpdateOptions] = None,
) -> FeedReader:
    """
    Creates a new feed reader object.

    Args:
        request_options (BeeRequestOptions): The HTTP client instance for making requests to the Bee API.
        type (str): The type of feed.
        topic (bytes): The topic of the feed.
        owner (bytes): The owner of the feed.

    Returns:
        FeedReader: The feed reader object.
    """

    def __download(
        options: Optional[Union[FeedUpdateOptions, dict]] = None,
    ) -> FetchFeedUpdateResponse:
        if isinstance(options, dict):
            options = FeedUpdateOptions.model_validate(options)

        if not options or not options.index:
            # * if options exists but not options.index then keep other configs from options
            if not options:
                options = {}
            return fetch_latest_feed_update(request_options, owner, topic, {**options, "type": _type})  # type: ignore

        update = download_feed_update(request_options, owner, topic, options.index)

        return FetchFeedUpdateResponse(
            reference=bytes_to_hex(update.reference),
            feed_index=options.index,
            feed_index_next="",
        )

    # download_partial = partial(__download)

    return FeedReader(
        request_options=request_options,
        Type=_type,
        owner=owner,
        topic=topic,
        options=options,
        download=__download,
    )


def make_feed_writer(
    request_options: BeeRequestOptions,
    _type: Union[FeedType, str],
    topic: Union[Topic, str],
    signer: Union[AccountAPI, Signer],
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
    if isinstance(signer, Signer):
        signer = signer.signer

    def __upload(
        postage_batch_id: Union[BatchId, AddressType],
        reference: Union[Reference, str, bytes],
        options: Optional[FeedUpdateOptions] = {},  # type: ignore  # noqa: B006
    ) -> Reference:
        canonical_reference = make_bytes_reference(reference)
        return update_feed(
            request_options,
            signer,
            topic,
            canonical_reference,
            postage_batch_id,
            {**options, type: _type},  # type: ignore
        )

    return FeedWriter(
        request_options=request_options,
        Type=_type,
        topic=topic,
        signer=signer,
        upload=__upload,
    )
