import codecs
import json
from typing import Optional, Union

from bee_py.types.type import (
    BatchId,
    BeeRequestOptions,
    FeedReader,
    FeedWriter,
    JsonFeedOptions,
    Reference,
    UploadOptions,
)


def serialize_json(data: dict) -> bytes:
    """
    Serializes JSON data to a UTF-8 encoded byte string.

    Args:
        data (AnyJson): JSON data to serialize.

    Returns:
        bytes: UTF-8 encoded byte string representing the serialized JSON data.
    """
    try:
        json_string = json.dumps(data)
        return codecs.encode(json_string, "utf-8")
    except Exception as e:
        e.args = (f"JsonFeed: {e.args[0]}",) + e.args[1:]
        raise


def get_json_data(bee, reader: FeedReader) -> dict:
    """
    Get JSON data from a feed.

    @param bee: Bee instance
    @param reader: FeedReader instance
    @return: JSON data
    """
    feed_update = reader.download()
    if not isinstance(feed_update, (bytes, str)):
        feed_update = feed_update.model_dump()

    retrieved_data = bee.download_data(feed_update)

    if not isinstance(retrieved_data, (bytes, str)):
        retrieved_data = retrieved_data.model_dump()
    if isinstance(retrieved_data, dict):
        return retrieved_data
    return json.loads(retrieved_data)


def set_json_data(
    bee,
    writer: FeedWriter,
    postage_batch_id: BatchId,
    data,
    options: Optional[Union[JsonFeedOptions, UploadOptions]] = None,
    request_options: Optional[BeeRequestOptions] = None,
) -> Reference:
    """
    Set JSON data to a feed.

    @param bee: Bee instance
    @param writer: FeedWriter instance
    @param postage_batch_id: Batch ID
    @param data: Any JSON data
    @param options: JSON feed options and upload options
    @param request_options: Bee request options
    @return: Reference
    """
    serialized_data = json.dumps(data)
    response = bee.upload_data(postage_batch_id, serialized_data, options, request_options)
    reference = response.reference
    return writer.upload(postage_batch_id, reference)
