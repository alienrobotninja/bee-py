from bee_py.types.type import AllSettlements, BeeRequestOptions, Settlements
from bee_py.utils.http import http
from bee_py.utils.logging import logger

SETTLEMENTS_ENDPOINT = "settlements"


def get_settlements(request_options: BeeRequestOptions, peer: str) -> Settlements:
    """
    Get settlements with a specific peer.

    Args:
        request_options (BeeRequestOptions): The request options for making the HTTP request.
        peer (str): The Swarm address of the peer.

    Returns:
        Settlements: The settlements data returned from the HTTP request.
    """
    config = {
        "url": f"{SETTLEMENTS_ENDPOINT}/{peer}",
        "method": "GET",
    }
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        logger.error(response.raise_for_status())

    settlements_response = response.json()
    return Settlements.parse_obj(settlements_response)


def get_all_settlements(request_options: BeeRequestOptions) -> AllSettlements:
    """
    Get settlements with all known peers and total amount sent or received.

    Args:
        request_options (BeeRequestOptions): The request options for making the HTTP request.

    Returns:
        AllSettlements: The settlements data returned from the HTTP request.
    """
    config = {
        "url": SETTLEMENTS_ENDPOINT,
        "method": "get",
    }
    response = http(request_options, config)
    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        logger.error(response.raise_for_status())

    all_settlements_response = response.json()

    return AllSettlements.parse_obj(all_settlements_response)
