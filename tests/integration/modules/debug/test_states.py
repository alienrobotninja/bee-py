from bee_py.modules.debug.states import (
    WALLET_ENDPOINT,
    WalletBalance,
    WalletBalanceOLD,
    get_chain_state,
    get_reserve_state,
    get_wallet_balance,
)
from bee_py.types.type import ChainState, ReserveState


def test_get_chain_state(bee_debug_ky_options):
    state = get_chain_state(bee_debug_ky_options)
    assert isinstance(state, ChainState)
    assert isinstance(state.block, int)
    assert isinstance(state.total_amount, str)
    assert isinstance(state.current_price, str)
    assert isinstance(state.current_price, str)
    assert isinstance(state.current_price, str)


def test_get_reserve_state(bee_debug_ky_options):
    state = get_reserve_state(bee_debug_ky_options)
    assert isinstance(state, ReserveState)
    assert isinstance(state.radius, int)
    assert isinstance(state.commitment, int)
    assert isinstance(state.storage_radius, int)


def test_get_wallet_balance_old_version(requests_mock, bee_debug_url, bee_debug_ky_options):
    # Mock the response data
    response_data = {
        "bzz": "bzz_value",
        "contractAddress": "contract_address_value",
        "xDai": "x_dai_value",
    }

    # Mock the requests.get call
    requests_mock.get(bee_debug_url + "/" + WALLET_ENDPOINT, json=response_data)

    # Call the function
    result = get_wallet_balance(bee_debug_ky_options)

    # Check if the function returned the correct model
    assert isinstance(result, WalletBalanceOLD)


def test_get_wallet_balance_new_version(requests_mock, bee_debug_url, bee_debug_ky_options):
    # Mock the response data
    response_data = {
        "bzzBalance": "1000000000000000000",
        "nativeTokenBalance": "1000000000000000000",
        "chainID": 0,
        "chequebookContractAddress": "36b7efd913ca4cf880b8eeac5093fa27b0825906",
        "walletAddress": "36b7efd913ca4cf880b8eeac5093fa27b0825906",
    }

    # Mock the requests.get call
    requests_mock.get(bee_debug_url + "/" + WALLET_ENDPOINT, json=response_data)

    # Call the function
    result = get_wallet_balance(bee_debug_ky_options)

    # Check if the function returned the correct model
    assert isinstance(result, WalletBalance)
