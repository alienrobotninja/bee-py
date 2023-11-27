from typing import Optional

from bee_py.types.type import BeeRequestOptions, NumberString, TransactionHash, TransactionInfo
from bee_py.utils.http import http
from bee_py.utils.logging import logger

TRANSACTIONS_ENDPOINT = "transactions"


def get_all_transactions(request_options: BeeRequestOptions) -> TransactionInfo:
    """
    Retrieves a list of all pending transactions from the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        TransactionInfo[]: List of pending transaction information.
    """

    config = {"url": TRANSACTIONS_ENDPOINT, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        logger.error(response.raise_for_status())

    transactions_response = response.json()

    pending_transactions = transactions_response["pendingTransactions"]

    return [TransactionInfo.parse_obj(transaction) for transaction in pending_transactions]


def get_transaction(request_options: BeeRequestOptions, transaction_hash: TransactionHash) -> TransactionInfo:
    """
    Retrieves information for a specific pending transaction based on its hash.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        transaction_hash (TransactionHash): Hash of the transaction to be retrieved.

    Returns:
        TransactionInfo: The retrieved transaction information.
    """

    config = {"url": f"{TRANSACTIONS_ENDPOINT}/{transaction_hash}", "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        logger.error(response.raise_for_status())

    transaction_response = response.json()
    return TransactionInfo.parse_obj(transaction_response)


def rebroadcast_transaction(request_options: BeeRequestOptions, transaction_hash: TransactionHash) -> TransactionHash:
    """
    Rebroadcasts an existing pending transaction.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        transaction_hash (TransactionHash): Hash of the transaction to be rebroadcasted.

    Returns:
        TransactionHash: Hash of the rebroadcasted transaction.
    """

    config = {"url": f"{TRANSACTIONS_ENDPOINT}/{transaction_hash}", "method": "POST"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        logger.error(response.raise_for_status())

    rebroadcasted_transaction_response = response.json()
    return rebroadcasted_transaction_response["transactionHash"]


def cancel_transaction(
    request_options: BeeRequestOptions, transaction_hash: TransactionHash, gas_price: Optional[NumberString] = None
) -> TransactionHash:
    """
    Cancels an existing pending transaction.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        transaction_hash (TransactionHash): Hash of the transaction to be canceled.
        gas_price (NumberString | None): Optional gas price for the cancellation transaction.

    Returns:
        TransactionHash: Hash of the canceled transaction.
    """

    headers = {}

    if gas_price:
        headers["gas-price"] = gas_price

    config = {"url": f"{TRANSACTIONS_ENDPOINT}/{transaction_hash}", "method": "DELETE", "headers": headers}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        logger.error(response.raise_for_status())

    canceled_transaction_response = response.json()
    return canceled_transaction_response["transactionHash"]