from pydantic import BaseModel

from bee_py.types.type import BeeRequestOptions, ReferenceOrENS
from bee_py.utils.http import http
from bee_py.utils.logging import logger

STEWARDSHIP_ENDPOINT = "stewardship"


class IsRetrievableResponse(BaseModel):
    is_retrievable: bool


def reupload(
    request_options: BeeRequestOptions,
    reference: ReferenceOrENS,
) -> None:
    """
    Reuploads locally pinned data.

    Args:
        request_options (AsyncClient): The HTTP client instance for making requests to the Bee API.
        reference (ReferenceOrEns): The reference or ENS name of the data to reupload.

    Raises:
        BeeResponseError: If the data is not locally pinned or is invalid.
    """

    config = {"url": f"{STEWARDSHIP_ENDPOINT}/{reference}", "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore


def is_retrievable(
    request_options: BeeRequestOptions,
    reference: ReferenceOrENS,
) -> IsRetrievableResponse:
    """
    Checks whether the data at the given reference is retrievable.

    Args:
        request_options (AsyncClient): The HTTP client instance for making requests to the Bee API.
        reference (ReferenceOrEns): The reference or ENS name of the data to check.

    Returns:
        bool: True if the data is retrievable, False otherwise.
    """

    config = {"url": f"{STEWARDSHIP_ENDPOINT}/{reference}", "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    return IsRetrievableResponse(is_retrievable=response.json()["isRetrievable"])
