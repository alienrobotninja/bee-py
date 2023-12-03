from typing import Optional, Union

from bee_py.types.type import (
    BeeRequestOptions,
    ChequebookAddressResponse,
    ChequebookBalanceResponse,
    LastCashoutActionResponse,
    LastChequesForPeerResponse,
    LastChequesResponse,
    TransactionHash,
)
from bee_py.types.type import TransactionOptions as CashoutOptions
from bee_py.utils.http import http
from bee_py.utils.logging import logger

CHEQUEBOOK_ENDPOINT = "chequebook"


def get_chequebook_address(request_options: BeeRequestOptions) -> ChequebookAddressResponse:
    """
    Retrieves the address of the chequebook contract used.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        ChequebookAddressResponse: The chequebook address response.
    """

    url = f"{CHEQUEBOOK_ENDPOINT}/address"
    config = {"url": url, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():
            logger.error(response.raise_for_status())

    chequebook_address_response = response.json()
    return ChequebookAddressResponse.parse_obj(chequebook_address_response)


def get_chequebook_balance(request_options: BeeRequestOptions) -> ChequebookBalanceResponse:
    """
    Retrieves the balance of the chequebook.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        ChequebookBalanceResponse: The chequebook balance response.
    """

    url = f"{CHEQUEBOOK_ENDPOINT}/balance"
    config = {"url": url, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():
            logger.error(response.raise_for_status())

    chequebook_balance_response = response.json()
    return ChequebookBalanceResponse.parse_obj(chequebook_balance_response)


def get_last_cashout_action(
    request_options: BeeRequestOptions,
    peer: str,
) -> LastCashoutActionResponse:
    """
    Retrieves the last cashout action for the specified peer.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        peer (str): Swarm address of the peer.

    Returns:
        LastCashoutActionResponse: The last cashout action response.
    """

    url = f"{CHEQUEBOOK_ENDPOINT}/cashout/{peer}"
    config = {"url": url, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():
            logger.error(response.raise_for_status())

    last_cashout_action_response = response.json()
    return LastCashoutActionResponse.parse_obj(last_cashout_action_response)


def cashout_last_cheque(
    request_options: BeeRequestOptions,
    peer: str,
    options: Optional[Union[CashoutOptions, dict]] = None,
) -> TransactionHash:
    """
    Cashes out the last cheque for the specified peer.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        peer (str): Swarm address of the peer.
        options (CashoutOptions, optional): Optional cashout options. Defaults to None.

    Returns:
        TransactionHash: The transaction hash.
    """

    headers = {}

    if isinstance(options, dict):
        if options and "gasPrice" in options:
            headers["gas-price"] = str(options["gasPrice"])

        if options and "gasLimit" in options:
            headers["gas-limit"] = str(options["gasLimit"])
    else:
        if options and options.gas_price:
            headers["gas-price"] = options.gas_price

        if options and options.gas_limit:
            headers["gas-limit"] = options.gas_limit

    url = f"{CHEQUEBOOK_ENDPOINT}/cashout/{peer}"
    config = {"url": url, "method": "POST", "headers": headers}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():
            logger.error(response.raise_for_status())

    transaction_response = response.json()
    return transaction_response["transactionHash"]


def get_last_cheques_for_peer(
    request_options: BeeRequestOptions,
    peer: str,
) -> LastChequesForPeerResponse:
    """
    Retrieves the last cheques for the specified peer.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        peer (str): Swarm address of the peer.

    Returns:
        LastChequesForPeerResponse: The last cheques for peer response.
    """

    url = f"{CHEQUEBOOK_ENDPOINT}/cheque/{peer}"
    config = {"url": url, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():
            logger.error(response.raise_for_status())

    last_cheques_for_peer_response = response.json()
    return LastChequesForPeerResponse.parse_obj(last_cheques_for_peer_response)


def get_last_cheques(request_options: BeeRequestOptions) -> LastChequesResponse:
    """
    Retrieves the last cheques for all peers.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        LastChequesResponse: The last cheques response.
    """

    url = f"{CHEQUEBOOK_ENDPOINT}/cheque"
    config = {"url": url, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():
            logger.error(response.raise_for_status())

    last_cheques_response = response.json()
    return LastChequesResponse.parse_obj(last_cheques_response)


def deposit_tokens(
    request_options: BeeRequestOptions,
    amount: Union[int, str],
    gas_price: Optional[str] = None,
) -> TransactionHash:
    """
    Deposits tokens from the overlay address into the chequebook.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        amount (int | str): Amount of tokens to deposit.
        gas_price (str, optional): Gas price in WEI for the transaction call. Defaults to None.

    Returns:
        TransactionHash: The transaction hash.
    """

    headers = {}

    if gas_price:
        headers["gas-price"] = gas_price

    url = f"{CHEQUEBOOK_ENDPOINT}/deposit"
    config = {
        "url": url,
        "method": "POST",
        "params": {"amount": str(amount)},
        "headers": headers,
    }
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():
            logger.error(response.raise_for_status())

    transaction_response = response.json()
    return transaction_response["transactionHash"]


def withdraw_tokens(
    request_options: BeeRequestOptions,
    amount: Union[int, str],
    gas_price: Optional[str] = None,
) -> TransactionHash:
    """
    Withdraws tokens from the chequebook to the overlay address.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        amount (int | str): Amount of tokens to withdraw.
        gas_price (str, optional): Gas price in WEI for the transaction call. Defaults to None.

    Returns:
        TransactionHash: The transaction hash.
    """

    headers = {}

    if gas_price:
        headers["gas-price"] = gas_price

    url = f"{CHEQUEBOOK_ENDPOINT}/withdraw"
    config = {
        "url": url,
        "method": "POST",
        "params": {"amount": str(amount)},
        "headers": headers,
    }
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():
            logger.error(response.raise_for_status())

    transaction_response = response.json()
    return transaction_response["transactionHash"]
