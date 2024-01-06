from eth_typing import ChecksumAddress as AddressType

from bee_py.types.type import BalanceResponse, BeeRequestOptions, PeerBalance
from bee_py.utils.http import http
from bee_py.utils.logging import logger

BALANCES_END_POINT = "balances"
CONSUMED_ENDPOINT = "consumed"


def get_all_balances(request_options: BeeRequestOptions) -> BalanceResponse:
    """Retrieves balance information for all known peers, including prepaid services.

    Args:
        request_options: BeeRequestOptions object containing Bee API request options.

    Returns:
        BalanceResponse object containing a list of peer balances.
    """
    config = {"url": BALANCES_END_POINT, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    balances_response = response.json()
    return BalanceResponse.model_validate(balances_response)


def get_peer_balance(request_options: BeeRequestOptions, address: AddressType) -> PeerBalance:
    """Retrieves balance information for a specific peer, including prepaid services.

    Args:
        request_options: BeeRequestOptions object containing Bee API request options.
        address: Swarm address of the peer.

    Returns:
        PeerBalance object containing the peer's balance information.
    """

    config = {"url": f"{BALANCES_END_POINT}/{address}", "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore
    balances_response = response.json()

    return PeerBalance.model_validate(balances_response)


def get_past_due_consumption_balances(
    request_options: BeeRequestOptions,
) -> BalanceResponse:
    """Retrieves past due consumption balances for all known peers.

    Args:
        request_options: BeeRequestOptions object containing Bee API request options.

    Returns:
        BalanceResponse object containing a list of peer balances.
    """
    config = {"url": CONSUMED_ENDPOINT, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    balances_response = response.json()
    return BalanceResponse.model_validate(balances_response)


def get_past_due_consumption_peer_balance(request_options: BeeRequestOptions, address: AddressType) -> PeerBalance:
    """Retrieves past due consumption balance for a specific peer.

    Args:
        request_options: BeeRequestOptions object containing Bee API request options.
        address: Swarm address of the peer.

    Returns:
        PeerBalance object containing the peer's past due consumption balance information.
    """
    config = {"url": f"{CONSUMED_ENDPOINT}/{address}", "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    balances_response = response.json()
    return PeerBalance.model_validate(balances_response)
