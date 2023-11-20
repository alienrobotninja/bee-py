from typing import Any

from bee_py.chunk.soc import Identifier
from bee_py.feed.feed import Index, IndexBytes
from bee_py.types.type import FEED_INDEX_HEX_LENGTH, Topic
from bee_py.utils.hash import keccak256_hash
from bee_py.utils.hex import hex_to_bytes, make_hex_string, to_big_endian


def is_epoch(epoch: Any) -> bool:
    """Checks whether the given object represents a valid epoch."""
    return isinstance(epoch, dict) and epoch is not None and "time" in epoch and "level" in epoch


def hash_feed_identifier(topic: Topic, index: IndexBytes) -> Identifier:
    keccak256_hash(hex_to_bytes(topic), index)


def make_sequential_feed_identifier(topic: Topic, index: int) -> Identifier:
    # * convert index into big endian
    index_bytes = to_big_endian(index)
    return hash_feed_identifier(topic, index_bytes)


def make_feed_index_bytes(s: str) -> IndexBytes:
    """
    Converts a string into a byte array.

    Args:
        s: The string to convert.

    Returns:
        A byte array.
    """
    hex_string = make_hex_string(s, FEED_INDEX_HEX_LENGTH)
    return hex_to_bytes(hex_string)


def make_feed_identifier(topic: Topic, index: Index) -> Identifier:
    """
    Converts a topic and an index into a feed identifier.

    Args:
        topic: The topic to convert.
        index: The index to convert.

    Returns:
        A feed identifier.
    """
    if isinstance(index, int):
        return make_sequential_feed_identifier(topic, index)
    elif isinstance(index, str):
        index_bytes = make_feed_index_bytes(index)
        return hash_feed_identifier(topic, index_bytes)
    elif is_epoch(index):
        msg = "epoch is not yet implemented"
        raise TypeError(msg)

    return hash_feed_identifier(topic, index)
