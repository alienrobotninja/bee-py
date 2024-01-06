from typing import Optional, Union

from bee_py.types.type import BeeRequestOptions, Reference, Tag
from bee_py.utils.http import http
from bee_py.utils.logging import logger

TAGS_ENDPOINT = "tags"


def create_tag(request_options: Union[BeeRequestOptions, dict], address: Optional[str] = None) -> Tag:
    """
    Creates a new tag in the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        Tag: The newly created tag.
    """
    if address:
        config = {
            "url": TAGS_ENDPOINT,
            "method": "POST",
            "params": {"address": address},
        }
    else:
        config = {
            "url": TAGS_ENDPOINT,
            "method": "POST",
        }
    response = http(request_options, config)

    if response.status_code != 201:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    tag_response = response.json()
    return Tag.model_validate(tag_response)


def retrieve_tag(request_options: Union[BeeRequestOptions, dict], uid: int) -> Tag:
    """
    Retrieves tag information from Bee node

    Args:
        request_options (BeeRequestOptions): Bee Ky Options for making requests.
        uid (int): UID of tag to be retrieved

    Returns:
        Tag: The retrieved tag.
    """
    config = {
        "url": f"{TAGS_ENDPOINT}/{uid}",
        "method": "GET",
    }
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    tag_response = response.json()
    return Tag.model_validate(tag_response)


def get_all_tags(request_options: Union[BeeRequestOptions, dict], offset: int = 0, limit: int = 10) -> list[Tag]:
    """
    Fetches a limited list of tags from the Bee node.

    This function retrieves a paginated list of tags from the Bee node, using the
    specified `offset` and `limit` parameters.

    Args:
        request_options (BeeRequestOptions): Options that affect the request behavior.
        offset (int, optional): The offset to use for pagination. Defaults to 0.
        limit (int, optional): The limit of tags to return per page. Defaults to 10.

    Raises:
        HTTPXError: If an HTTP error occurs during the request.

    Returns:
        list[Tag]: The list of tags retrieved from the Bee node.
    """

    config = {
        "url": f"{TAGS_ENDPOINT}",
        "method": "GET",
        "params": {
            "offset": offset,
            "limit": limit,
        },
    }
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    tag_response = response.json()["tags"]

    return [Tag.model_validate(tag) for tag in tag_response]


def delete_tag(request_options: BeeRequestOptions, uid: int) -> None:
    """
    Removes a tag from the Bee node.

    This function deletes the specified tag from the Bee node.

    Args:
        request_options (BeeRequestOptions): Options that affect the request behavior.
        uid (int): The ID of the tag to be deleted.

    Raises:
        HTTPXError: If an HTTP error occurs during the request.
    """
    url = f"{TAGS_ENDPOINT}/{uid}"

    config = {"url": url, "method": "DELETE"}

    response = http(request_options, config)

    if response.status_code != 204:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore


def update_tag(request_options: Union[BeeRequestOptions, dict], uid: int, reference: Union[Reference, str]) -> None:
    """
    Updates a tag on the Bee node.

    This function updates the specified tag with the provided reference.

    Args:
        request_options (BeeRequestOptions): Options that affect the request behavior.
        uid (int): The ID of the tag to be updated.
        reference (Reference): The new reference for the tag.

    Raises:
        HTTPXError: If an HTTP error occurs during the request.
    """

    url = f"{TAGS_ENDPOINT}/{uid}"
    config = {"url": url, "method": "PATCH", "data": reference}

    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore
