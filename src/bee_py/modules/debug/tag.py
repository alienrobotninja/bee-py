from bee_py.types.type import BeeRequestOptions, ExtendedTag
from bee_py.utils.http import http
from bee_py.utils.logging import logger

TAGS_ENDPOINT = "tags"


def retrieve_extended_tag(request_options: BeeRequestOptions, uid: int) -> ExtendedTag:
    """
    Retrieves extended tag information from the Bee node for the specified tag UID.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        uid (int): UID of the tag to be retrieved.

    Returns:
        ExtendedTag: The extended tag information.
    """
    config = {"url": f"{TAGS_ENDPOINT}/{uid}", "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    debug_status_response = response.json()
    return ExtendedTag.model_validate(debug_status_response)
