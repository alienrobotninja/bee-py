from bee_py.Exceptions import PinNotFoundError
from bee_py.types.type import BeeRequestOptions, Pin, Reference
from bee_py.utils.http import http
from bee_py.utils.logging import logger

PINNING_ENDPOINT = "pins"


def pin(request_options: BeeRequestOptions, reference: Reference) -> None:
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
        if response.raise_for_status():
            if response.raise_for_status():
                logger.error(response.raise_for_status())


def unpin(request_options: BeeRequestOptions, reference: Reference) -> None:
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
        if response.raise_for_status():
            logger.error(response.raise_for_status())


def get_pin(request_options: BeeRequestOptions, reference: Reference) -> Pin:
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
        if response.raise_for_status():
            logger.error(response.raise_for_status())

    return Pin.model_validate(response.json())


def get_all_pins(request_options: BeeRequestOptions) -> Reference:
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
        if response.raise_for_status():
            logger.error(response.raise_for_status())

    response_data = response.data
    references = response_data.get("references", [])

    print("REFERENCE FROM PINNING: ", references)
    return Reference(value=references)
