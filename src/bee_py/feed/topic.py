from typing import Union

from eth_utils import keccak

from bee_py.types.type import TOPIC_BYTES_LENGTH, TOPIC_HEX_LENGTH, Topic
from bee_py.utils.hex import assert_bytes, bytes_to_hex, make_hex_string


def make_topic(topic: Union[Topic, bytes, str]) -> Topic:
    """Converts a topic representation (string or bytes) into a Topic object."""
    if isinstance(topic, str):
        return Topic(value=make_hex_string(topic, TOPIC_HEX_LENGTH))
    elif isinstance(topic, bytes):
        assert_bytes(topic, TOPIC_BYTES_LENGTH)
        return Topic(value=bytes_to_hex(topic, TOPIC_HEX_LENGTH))
    elif isinstance(topic, Topic):
        return topic
    else:
        msg = "Invalid topic"
        raise TypeError(msg)


def make_topic_from_string(s: str) -> Topic:
    """Creates a Topic object from a string representation."""
    if not isinstance(s, str):
        msg = "Topic must be a string!"
        raise TypeError(msg)

    return Topic(value=bytes_to_hex(keccak(text=s), TOPIC_HEX_LENGTH))
