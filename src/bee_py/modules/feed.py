from typing import Optional

from eth_typing import ChecksumAddress as AddressType

from bee_py.feed.type import FeedType
from bee_py.types.type import BatchId, BeeRequestOptions, Reference, ReferenceResponse, Topic
from bee_py.utils.error import BeeError
from bee_py.utils.headers import extract_upload_headers
from bee_py.utils.http import http

FEED_ENDPOINT = "feeds"


class CreateFeedOptions:
    """
    Options for creating a feed.
    """

    def __init__(self, _type: Optional[FeedType] = None):
        """
        Constructor for CreateFeedOptions.

        :param type: The type of the feed.
        :_type type: Optional[FeedType]
        """
        self.type = _type


class FeedUpdateOptions:
    """
    Options for updating a feed.
    """

    def __init__(self, at: Optional[int] = None, _type: Optional[FeedType] = "sequence", index: Optional[str] = None):
        """
        Constructor for FeedUpdateOptions.

        :param at: The start date as a Unix timestamp.
        :type at: Optional[int]
        :param type: The type of the feed (default: 'sequence').
        :_type type: Optional[FeedType]
        :param index: Fetch a specific previous feed's update (default fetches the latest update).
        :type index: Optional[str]
        """
        self.at = at
        self.type = _type
        self.index = index


class FeedUpdateHeaders:
    """
    Headers for a feed update.
    """

    def __init__(self, feed_index: str, feed_index_next: str):
        """
        Constructor for FeedUpdateHeaders.

        :param feed_index: The current feed's index.
        :type feed_index: str
        :param feed_index_next: The feed's index for the next update.
        :type feed_index_next: str
        """
        self.feed_index = feed_index
        self.feed_index_next = feed_index_next


class FetchFeedUpdateResponse(ReferenceResponse, FeedUpdateHeaders):
    """
    Response for fetching a feed update.
    """

    pass


def create_feed_manifest(
    request_options: BeeRequestOptions,
    owner: AddressType,
    topic: Topic,
    postage_batch_id: BatchId,
    options: Optional[CreateFeedOptions] = None,
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
    config = {
        "method": "post",
        "url": f"{FEED_ENDPOINT}/{owner}/{topic}",
        "params": options,
        "headers": extract_upload_headers(postage_batch_id),
    }
    response = http(request_options, config)

    # *  Raises a HTTPError if the response status is 4xx, 5xx
    response.raise_for_status()

    return response.json()["reference"]


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

    return FeedUpdateHeaders(feed_index, feed_index_next)


def fetch_latest_feed_update(
    request_options: BeeRequestOptions,
    owner: AddressType,
    topic: Topic,
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

    response = http(
        request_options,
        {
            "url": f"{FEED_ENDPOINT}/{owner}/{topic}",
            "params": options,
        },
    )
    # * Raise exception for error code 4xx & 5xx
    response.raise_for_status()
    data = response.json()

    # Extract feed update headers from response headers
    headers = read_feed_update_headers(response.headers)

    return FetchFeedUpdateResponse(data["reference"], headers.feed_index, headers.feed_index_next)
