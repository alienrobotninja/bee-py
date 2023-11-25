from typing import Optional

from bee_py.types.type import BeeRequestOptions, Reference, Tag
from bee_py.utils.http import http
from bee_py.utils.logging import logger

TAGS_ENDPOINT = "tags"


def create_tag(request_options: BeeRequestOptions, address: Optional[str]) -> Tag:
    """
    Creates a new tag in the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        Tag: The newly created tag.
    """
    if address:
        config = {"url": TAGS_ENDPOINT, "method": "POST", "params": {"address": address}}
    else:
        config = {
            "url": TAGS_ENDPOINT,
            "method": "POST",
        }
    response = http(request_options, config)

    if response.status_code != 201:  # noqa: PLR2004
        logger.info(response.json())
        logger.error(response.raise_for_status())

    tag_response = response.json()
    return Tag.parse_obj(tag_response)
