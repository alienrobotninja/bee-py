from typing import Union

from bee_py.Exceptions import PinNotFoundError
from bee_py.types.type import BeeRequestOptions, GetAllPinResponse, Pin, Reference
from bee_py.utils.http import http
from bee_py.utils.logging import logger

PINNING_ENDPOINT = "pins"


def pin(request_options: Union[BeeRequestOptions, dict], reference: Union[Reference, str]) -> None:
    """
    Pins a piece of data with the given reference.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        reference (Reference): Bee data reference to pin.

    Returns:
        None
    """

    config = {"url": f"{PINNING_ENDPOINT}/{reference}", "method": "POST"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            if response.raise_for_status():  # type: ignore
                logger.error(response.raise_for_status())  # type: ignore
                return None  # type: ignore


def unpin(request_options: Union[BeeRequestOptions, dict], reference: Union[Reference, str]) -> None:
    """
    Unpins a piece of data with the given reference.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        reference (Reference): Bee data reference to unpin.

    Returns:
        None
    """

    config = {"url": f"{PINNING_ENDPOINT}/{reference}", "method": "DELETE"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore


def get_pin(request_options: Union[BeeRequestOptions, dict], reference: Union[Reference, str]) -> Pin:
    """
    Retrieves the pin status for a specific address.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        reference (Reference): Bee data reference to check pin status for.

    Raises:
        PinNotFoundError: If no pin information found for the given reference.

    Returns:
        Pin: Pin information for the specified reference.
    """

    config = {"url": f"{PINNING_ENDPOINT}/{reference}", "method": "GET"}
    response = http(request_options, config)

    if response.status_code == 404:  # noqa: PLR2004
        raise PinNotFoundError(reference)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    return Pin.model_validate(response.json())


def get_all_pins(request_options: Union[BeeRequestOptions, dict]) -> GetAllPinResponse:
    """
    Retrieves a list of all pinned references.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        Reference: List of pinned references.
    """

    config = {"url": PINNING_ENDPOINT, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    response_data = response.json()
    # print("Response data--->", response_data)
    references = response_data.get("references", [])
    references = [Reference(value=ref) for ref in references]

    return GetAllPinResponse(references=references)
