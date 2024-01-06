from bee_py.types.type import BeeRequestOptions
from bee_py.utils.http import http
from bee_py.utils.logging import logger


def check_connection(request_options: BeeRequestOptions) -> None:
    """
    Checks the connection to the Bee API by sending an HTTP GET request to the base Bee URL.

    Args:
        request_options (Any): The HTTP request options for connecting to the Bee API.

    Raises:
        HTTPError: If the connection to the Bee API fails.
    """
    config = {"url": "", "method": "GET"}
    response = http(request_options, config)

    if response.raise_for_status():  # type: ignore
        logger.error(response.raise_for_status())  # type: ignore
        return None  # type: ignore
