from typing import NewType, Union

from pydantic import BaseModel

from bee_py.chunk.serialize import serialize_bytes
from bee_py.chunk.signer import sign
from bee_py.chunk.soc import download_single_owner_chunk, upload_single_owner_chunk_data
from bee_py.feed.identifiers import make_feed_identifier
from bee_py.feed.type import FeedType
from bee_py.modules.chunk import *
from bee_py.types.type import (  # Reference,
    BatchId,
    BeeRequestOptions,
    FeedReader,
    FeedType,
    FeedUpdateOptions,
    FeedWriter,
    JsonFeedOptions,
    UploadOptions,
)
from bee_py.utils.collection import assert_collection, make_collection
from bee_py.utils.hash import keccak_hash
from bee_py.utils.hex import bytes_to_hex, hex_to_bytes, make_hex_string
from bee_py.utils.reference import make_bytes_reference

TIMESTAMP_PAYLOAD_SIZE = 8
TIMESTAMP_PAYLOAD_SIZE_HEX = 16
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
