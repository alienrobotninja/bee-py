from pydantic import ValidationError

from bee_py.types.type import BeeRequestOptions, ChainState, ReserveState, WalletBalance, WalletBalanceOLD
from bee_py.utils.http import http
from bee_py.utils.logging import logger

RESERVE_STATE_ENDPOINT = "reservestate"
WALLET_ENDPOINT = "wallet"
CHAIN_STATE_ENDPOINT = "chainstate"


def get_reserve_state(request_options: BeeRequestOptions) -> ReserveState:
    """
    Retrieves the current state of the reserve.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        ReserveState: The current state of the reserve.
    """

    config = {"url": RESERVE_STATE_ENDPOINT, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if logger.error(response.raise_for_status()):
            logger.error(response.raise_for_status())

    reserve_state_response = response.json()
    return ReserveState.parse_obj(reserve_state_response)


def get_chain_state(request_options: BeeRequestOptions) -> ChainState:
    """
    Retrieves the current state of the chain.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        ChainState: The current state of the chain.
    """

    config = {"url": CHAIN_STATE_ENDPOINT, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if logger.error(response.raise_for_status()):
            logger.error(response.raise_for_status())

    chain_state_response = response.json()
    return ChainState.parse_obj(chain_state_response)


# * Maps deprecated properties to new WalletBalance object
def map_wallet_properties(data: WalletBalance) -> WalletBalance:
    """
    Maps wallet properties for backward compatibility.

    Args:
        data (WalletBalance): The wallet balance data.

    Returns:
        WalletBalance: The modified wallet balance data.
    """

    data_dict = data
    data_dict["bzz_balance"] = data_dict.pop("bzz")
    data_dict["native_token_balance"] = data_dict.pop("xDai")
    data_dict["chequebook_contract_address"] = data_dict.pop("contractAddress")

    return WalletBalance.parse_obj(data_dict)


def get_wallet_balance(request_options: BeeRequestOptions) -> WalletBalance:
    """
    Retrieves the wallet balances for xDai and BZZ of the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        WalletBalance: The wallet balances for xDai and BZZ.
    """

    config = {"url": WALLET_ENDPOINT, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if logger.error(response.raise_for_status()):
            logger.error(response.raise_for_status())

    wallet_balance_response = response.json()

    if (
        "bzz" in wallet_balance_response
        and "xDai" in wallet_balance_response
        and "contractAddress" in wallet_balance_response
    ):
        try:
            return WalletBalanceOLD.parse_obj(wallet_balance_response)
        except ValidationError:
            return map_wallet_properties(WalletBalance.parse_obj(wallet_balance_response))
    else:
        return WalletBalance.parse_obj(wallet_balance_response)
