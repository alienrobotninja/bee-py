import codecs
import json

# from bee_py.feed.type import FeedType
# from bee_py.types.type import (
#     BatchId,
#     BeeRequestOptions,
#     FeedReader,
#     FeedWriter,
#     JsonFeedOptions,
#     Reference,
#     UploadOptions,
# )


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
