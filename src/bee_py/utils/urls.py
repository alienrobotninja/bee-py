import urllib
from typing import Any

from bee_py.utils.error import BeeArgumentError


def is_valid_bee_url(url: Any) -> bool:
    """Validates that passed string is valid URL of Bee.

    We support only HTTP and HTTPS protocols.

    Args:
      url: The URL to validate.

    Returns:
      True if the URL is valid, False otherwise.
    """

    if not isinstance(url, str):
        return False

    try:
        parsed_url = urllib.parse.urlparse(url)
    except ValueError:
        return False

    return parsed_url.scheme in ["http", "https"]


def assert_bee_url(url: Any):
    """Validates that passed string is valid URL of Bee, if not it throws BeeArgumentError.

    We support only HTTP and HTTPS protocols.

    Args:
      url: The URL to validate.

    Raises:
      BeeArgumentError: If the URL is not valid.
    """

    if not is_valid_bee_url(url):
        msg = "URL is not valid!"
        raise BeeArgumentError(msg, url)


def strip_last_slash(url: str) -> str:
    """Removes trailing slash out of the given string.

    Args:
      url: The string to remove the trailing slash from.

    Returns:
      The string without the trailing slash.
    """

    if url.endswith("/"):
        return url[:-1]
    else:
        return url
