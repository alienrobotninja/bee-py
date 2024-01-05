from typing import Union

from ape.types import AddressType
from requests import HTTPError

from bee_py.feed.feed import get_feed_update_chunk_reference

# from bee_py.bee import Bee
from bee_py.modules.bytes import read_big_endian
from bee_py.types.type import BeeRequestOptions, Index, IndexBytes, Reference, Topic
from bee_py.utils.hex import bytes_to_hex


def make_numeric_index(index: Union[Index, IndexBytes]):
    """
    Converts an index to a numeric value.

    :param index: The index to convert.
    :type index: Union[Index,IndexBytes]: Union[int, Epoch, bytes, str]
    :return: The numeric index.
    :rtype: int
    :raises TypeError: If the type of the index is unknown.
    """
    if isinstance(index, bytes):
        return read_big_endian(index)

    if isinstance(index, str):
        return int(index)

    if isinstance(index, int):
        return index

    msg = "Unknown type of index!"
    raise TypeError(msg)


def is_chunk_retrievable(bee, ref: Reference, request_options: BeeRequestOptions) -> bool:
    """
    Checks whether a chunk is retrievable by attempting to download it.

    The `/stewardship/{reference}` endpoint does not support verifying chunks, only manifest references.

    Args:
        bee (Bee): The Bee client instance.
        ref (Reference): The chunk reference.
        request_options (BeeRequestOptions): The request options.

    Returns:
        bool: True if the chunk is retrievable, False otherwise.
    """

    try:
        bee.download_chunk(ref, request_options)
        return True
    except HTTPError as e:
        if e.response.status_code == 404:  # noqa: PLR2004
            return False
        raise e


def get_all_sequence_update_references(
    owner: Union[AddressType, str, bytes], topic: Union[Topic, str], index: Union[Index, IndexBytes]
) -> list[Reference]:
    """
    Creates a list of references for all sequence updates chunk up to the given index.

    Creates an array of references for all sequence updates up to the given index.

    Args:
        owner (AddressType): The owner of the feed.
        topic (Topic): The topic of the feed.
        index (Index): The index of the last sequence update to include.

    Returns:
        list[Reference]
    """
    num_index = make_numeric_index(index)
    update_references = [
        Reference(value=bytes_to_hex(get_feed_update_chunk_reference(owner, topic, i))) for i in range(num_index + 1)
    ]

    return update_references


def are_all_sequential_feeds_update_retrievable(
    bee,
    owner: Union[AddressType, bytes],
    topic: Union[Topic, str],
    index: Union[Index, IndexBytes],
    request_options: BeeRequestOptions,
) -> bool:
    """
    Checks whether all sequential feed updates up to the given index are retrievable.

    Args:
        bee (Bee): The Bee client instance.
        owner (AddressType): The owner of the feed.
        topic (Topic): The topic of the feed.
        index (Index): The index of the last sequence update to check.
        request_options (BeeRequestOptions): The request options.

    Returns:
        bool: True if all sequence updates are retrievable, False otherwise.
    """

    chunk_retrievable_promises = [
        is_chunk_retrievable(bee, ref, request_options)
        for ref in get_all_sequence_update_references(owner, topic, index)
    ]

    return all(chunk_retrievable_promises)
