from typing import Optional, Union

from eth_typing import ChecksumAddress as AddressType

from bee_py.types.type import (
    BeeRequestOptions,
    CreateFeedOptions,
    FeedUpdateHeaders,
    FeedUpdateOptions,
    FetchFeedUpdateResponse,
    Reference,
    Topic,
)
from bee_py.utils.error import BeeError
from bee_py.utils.headers import extract_upload_headers
from bee_py.utils.http import http

FEED_ENDPOINT = "feeds"


def create_feed_manifest(
    request_options: BeeRequestOptions,
    owner: Union[AddressType, str],
    topic: Union[Topic, str],
    postage_batch_id: str,
    options: Optional[Union[CreateFeedOptions, dict]] = None,
) -> Reference:
    """
    Create an initial feed root manifest.

    Args:
        request_options: BeeRequestOptions instance.
        owner: Owner's ethereum address in hex.
        topic: Topic in hex.
        postage_batch_id: Postage BatchId to be used to create the Feed Manifest.
        options: Additional options, like type (default: 'sequence').

    Returns:
        Reference: The reference of the created feed.
    """
    if isinstance(topic, Topic):
        topic = str(topic)

    config = {
        "method": "post",
        "url": f"{FEED_ENDPOINT}/{owner}/{topic}",
        "params": options,
        "headers": extract_upload_headers(postage_batch_id),
    }
    response = http(request_options, config)

    # *  Raises a HTTPError if the response status is 4xx, 5xx
    response.raise_for_status()

    return Reference(value=response.json()["reference"])


def read_feed_update_headers(headers: dict[str, str]) -> FeedUpdateHeaders:
    """
    Reads feed update headers from a response.

    Args:
        headers: A dictionary of headers from a response.

    Returns:
        FeedUpdateHeaders: The feed update headers.

    Raises:
        BeeError: If the headers do not contain the expected swarm-feed-index or swarm-feed-index-next.
    """
    feed_index = headers.get("swarm-feed-index")
    feed_index_next = headers.get("swarm-feed-index-next")

    if not feed_index:
        msg = "Response did not contain expected swarm-feed-index!"
        raise BeeError(msg)

    if not feed_index_next:
        msg = "Response did not contain expected swarm-feed-index-next!"
        raise BeeError(msg)

    return FeedUpdateHeaders(feed_index=feed_index, feed_index_next=feed_index_next)


def fetch_latest_feed_update(
    request_options: BeeRequestOptions,
    owner: Union[AddressType, str],
    topic: Union[Topic, str],
    options: Optional[FeedUpdateOptions] = None,
) -> FetchFeedUpdateResponse:
    """Finds and retrieves the latest feed update.

    Args:
        request_options: BeeRequestOptions instance containing the Bee node connection details.
        owner: The owner's Ethereum address in hex format.
        topic: The topic in hex format.
        options: Optional FeedUpdateOptions instance containing additional options, like index, at, type.

    Returns:
        A FetchFeedUpdateResponse object containing the feed update reference, index, and next index.
    """
    if isinstance(topic, Topic):
        topic = topic.value

    response = http(
        request_options,
        {
            "url": f"{FEED_ENDPOINT}/{owner}/{topic}",
            "params": options,
            "method": "GET",
        },
    )
    # * Raise exception for error code 4xx & 5xx
    response.raise_for_status()
    data = response.json()

    # Extract feed update headers from response headers
    headers = read_feed_update_headers(response.headers)  # type: ignore

    return FetchFeedUpdateResponse(
        reference=data["reference"],
        feed_index=headers.feed_index,
        feed_index_next=headers.feed_index_next,
    )
