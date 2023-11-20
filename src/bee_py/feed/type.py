from enum import Enum


class FeedType(Enum):
    """
    Enum class for feed types.

    Attributes:
        SEQUENCE: Sequential feed type.
        EPOCH: Epoch feed type.
    """

    SEQUENCE = "sequence"
    EPOCH = "epoch"


DEFAULT_FEED_TYPE = FeedType.SEQUENCE


def is_feed_type(feed_type: str) -> bool:
    """
    Checks if the given type is a valid feed type.

    Args:
        feed_type: The type to check.

    Returns:
        True if the type is a valid feed type, False otherwise.
    """
    return feed_type in [e.value for e in FeedType]


def assert_feed_type(feed_type: str):
    """
    Asserts that the given type is a valid feed type.

    Args:
        feed_type: The type to assert.

    Raises:
        TypeError: If the type is not a valid feed type.
    """
    if not is_feed_type(feed_type):
        msg = "invalid feed type"
        raise TypeError(msg)
