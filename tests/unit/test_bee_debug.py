from unittest.mock import patch

import pydantic
import pytest

from bee_py.bee_debug import BeeDebug
from bee_py.types.type import BatchId, BeeRequestOptions, CashoutOptions, PostageBatchOptions
from bee_py.utils.error import BeeArgumentError, BeeError
from bee_py.utils.type import (
    assert_address,
    assert_batch_id,
    assert_cashout_options,
    assert_non_negative_integer,
    assert_positive_integer,
    assert_postage_batch_options,
    assert_request_options,
    assert_transaction_hash,
    assert_transaction_options,
)

TRANSACTION_HASH = "36b7efd913ca4cf880b8eeac5093fa27b0825906c600685b6abdd6566e6cfe8f"

CASHOUT_RESPONSE = {"transactionHash": TRANSACTION_HASH}

MOCK_SERVER_URL = "http://localhost:12345/"

# * Endpoints
FEED_ENDPOINT = "/feeds"
BZZ_ENDPOINT = "/bzz"
BYTES_ENDPOINT = "/bytes"
POSTAGE_ENDPOINT = "/stamps"
CHEQUEBOOK_ENDPOINT = "/chequebook"

request_options_assertions: list[tuple] = [
    (1, TypeError),
    (True, TypeError),
    # ([], TypeError),
    (lambda: {}, TypeError),
    ("string", TypeError),
    ({"timeout": "plur"}, pydantic.ValidationError),
    ({"timeout": True}, pydantic.ValidationError),
    ({"timeout": {}}, pydantic.ValidationError),
    ({"timeout": []}, pydantic.ValidationError),
    ({"timeout": -1}, BeeArgumentError),
    ({"retry": "plur"}, pydantic.ValidationError),
    ({"retry": True}, pydantic.ValidationError),
    ({"retry": {}}, pydantic.ValidationError),
    ({"retry": []}, pydantic.ValidationError),
    ({"retry": -1}, BeeArgumentError),
]


test_address_assertions: list[tuple] = [
    (1, TypeError),
    (True, TypeError),
    ({}, TypeError),
    ([], TypeError),
    (None, TypeError),
    ("ZZZfb5a872396d9693e5c9f9d7233cfa93f395c093371017ff44aa9ae6564cdd", TypeError),
    ("4fb5a872396d9693e5c9f9d7233cfa93f395c093371017ff44aa9ae6564cdd", TypeError),
    # Bytes length mismatch
    (b"\x00" * 19, TypeError),
    ("", TypeError),
]


@pytest.mark.parametrize(
    "url",
    [
        "",
        None,
        "some-invalid-url",
        "invalid:protocol",
        "javascript:console.log()",
        "ws://localhost:1633",
    ],
)
def test_bee_constructor(url):
    with pytest.raises(BeeArgumentError):
        BeeDebug(url)


def test_default_headers_and_use_them_if_specified(requests_mock):
    url = "http://localhost:12345/chequebook/deposit?amount=10"

    requests_mock.post(url, headers={"X-Awesome-Header": "123"}, json=CASHOUT_RESPONSE)

    bee = BeeDebug(MOCK_SERVER_URL, {"X-Awesome-Header": "123"})

    assert bee.deposit_tokens("10") == TRANSACTION_HASH


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_remove_peer(input_value, expected_error_type, test_chunk_hash_str):
    bee = BeeDebug(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.remove_peer(test_chunk_hash_str, input_value)


@pytest.mark.parametrize("input_value, expected_error_type", test_address_assertions)
def test_remove_peer_invalid_address(input_value, expected_error_type):
    with pytest.raises(expected_error_type):
        bee = BeeDebug(MOCK_SERVER_URL)
        bee.remove_peer(input_value)


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_ping_peer(input_value, expected_error_type, test_chunk_hash_str):
    bee = BeeDebug(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.ping_peer(test_chunk_hash_str, input_value)


@pytest.mark.parametrize("input_value, expected_error_type", test_address_assertions)
def test_ping_peer_invalid_address(input_value, expected_error_type):
    with pytest.raises(expected_error_type):
        bee = BeeDebug(MOCK_SERVER_URL)
        bee.ping_peer(input_value)


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_get_peer_balance(input_value, expected_error_type, test_chunk_hash_str):
    bee = BeeDebug(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.get_peer_balance(test_chunk_hash_str, input_value)


@pytest.mark.parametrize("input_value, expected_error_type", test_address_assertions)
def test_get_peer_balance_invalid_address(input_value, expected_error_type):
    with pytest.raises(expected_error_type):
        bee = BeeDebug(MOCK_SERVER_URL)
        bee.get_peer_balance(input_value)


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_get_past_due_consumption_peer_balance(input_value, expected_error_type, test_chunk_hash_str):
    bee = BeeDebug(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.get_past_due_consumption_peer_balance(test_chunk_hash_str, input_value)


@pytest.mark.parametrize("input_value, expected_error_type", test_address_assertions)
def test_get_past_due_consumption_peer_balance_invalid_address(input_value, expected_error_type):
    with pytest.raises(expected_error_type):
        bee = BeeDebug(MOCK_SERVER_URL)
        bee.get_past_due_consumption_peer_balance(input_value)


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_get_last_cheques_for_peer(input_value, expected_error_type, test_chunk_hash_str):
    bee = BeeDebug(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.get_last_cheques_for_peer(test_chunk_hash_str, input_value)


@pytest.mark.parametrize("input_value, expected_error_type", test_address_assertions)
def test_get_last_cheques_for_peer_invalid_address(input_value, expected_error_type):
    with pytest.raises(expected_error_type):
        bee = BeeDebug(MOCK_SERVER_URL)
        bee.get_last_cheques_for_peer(input_value)


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_get_last_cashout_action(input_value, expected_error_type, test_chunk_hash_str):
    bee = BeeDebug(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.get_last_cashout_action(test_chunk_hash_str, input_value)


@pytest.mark.parametrize("input_value, expected_error_type", test_address_assertions)
def test_get_last_cashout_action_invalid_address(input_value, expected_error_type):
    with pytest.raises(expected_error_type):
        bee = BeeDebug(MOCK_SERVER_URL)
        bee.get_last_cashout_action(input_value)


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_get_settlements(input_value, expected_error_type, test_chunk_hash_str):
    bee = BeeDebug(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.get_settlements(test_chunk_hash_str, input_value)


@pytest.mark.parametrize("input_value, expected_error_type", test_address_assertions)
def test_get_settlements_invalid_address(input_value, expected_error_type):
    with pytest.raises(expected_error_type):
        bee = BeeDebug(MOCK_SERVER_URL)
        bee.get_settlements(input_value)


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_cashout_last_cheque(input_value, expected_error_type, test_chunk_hash_str):
    bee = BeeDebug(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        bee.cashout_last_cheque(test_chunk_hash_str, input_value)


@pytest.mark.parametrize("input_value, expected_error_type", test_address_assertions)
def test_cashout_last_cheque_invalid_address(input_value, expected_error_type):
    with pytest.raises(expected_error_type):
        bee = BeeDebug(MOCK_SERVER_URL)
        bee.cashout_last_cheque(input_value)


def test_no_headers_if_no_gas_price_is_set(requests_mock, test_address):
    url = "http://localhost:12345/chequebook/cashout/ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"

    requests_mock.post(url, json=CASHOUT_RESPONSE)

    bee = BeeDebug(MOCK_SERVER_URL)

    assert bee.cashout_last_cheque(test_address) == TRANSACTION_HASH


def test_no_headers_if_gas_price_is_set(requests_mock, test_address):
    url = "http://localhost:12345/chequebook/cashout/ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"

    requests_mock.post(url, headers={"gas-price": "100000000000"}, json=CASHOUT_RESPONSE)

    bee = BeeDebug(MOCK_SERVER_URL)

    assert bee.cashout_last_cheque(test_address, {"gasPrice": "100000000000"}) == TRANSACTION_HASH


def test_no_headers_if_gas_limit_is_set(requests_mock, test_address):
    url = "http://localhost:12345/chequebook/cashout/ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"

    requests_mock.post(url, headers={"gas-limit": "100000000000"}, json=CASHOUT_RESPONSE)

    bee = BeeDebug(MOCK_SERVER_URL)

    assert bee.cashout_last_cheque(test_address, {"gasLimit": "100000000000"}) == TRANSACTION_HASH


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_withdraw_tokens(input_value, expected_error_type):
    with pytest.raises(expected_error_type):
        bee = BeeDebug(MOCK_SERVER_URL, input_value)
        bee.withdraw_tokens("1", "0", input_value)


def test_withdraw_tokens_no_headers_if_no_gas_price_is_set(requests_mock):
    url = "http://localhost:12345/chequebook/withdraw?amount=10"

    requests_mock.post(url, json=CASHOUT_RESPONSE)

    bee = BeeDebug(MOCK_SERVER_URL)

    assert bee.withdraw_tokens("10") == TRANSACTION_HASH


def test_withdraw_tokens_if_gas_price_is_set(requests_mock):
    url = "http://localhost:12345/chequebook/withdraw?amount=10"

    requests_mock.post(url, headers={"gas-price": "100000000000"}, json=CASHOUT_RESPONSE)

    bee = BeeDebug(MOCK_SERVER_URL)

    assert bee.withdraw_tokens("10", "100000000000") == TRANSACTION_HASH


def test_withdraw_tokens_if_gas_limit_is_set(requests_mock):
    url = "http://localhost:12345/chequebook/withdraw?amount=10"

    requests_mock.post(url, headers={"gas-limit": "100000000000"}, json=CASHOUT_RESPONSE)

    bee = BeeDebug(MOCK_SERVER_URL)

    assert bee.withdraw_tokens("10", "100000000000") == TRANSACTION_HASH


@pytest.mark.parametrize("input_value, expected_error_type", [(None, ValueError), ("", ValueError), (-1, ValueError)])
def test_withdraw_tokens_wrong_input(input_value, expected_error_type):
    bee = BeeDebug(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        assert bee.withdraw_tokens(input_value)


@pytest.mark.parametrize(
    "input_value, expected_error_type", [(True, ValueError), ("asd", ValueError), ("-1", ValueError)]
)
def test_withdraw_tokens_throw_error_if_passed_wrong_gas_price_as_input(input_value, expected_error_type):
    bee = BeeDebug(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        assert bee.withdraw_tokens("1", input_value)


@pytest.mark.parametrize("input_value, expected_error_type", request_options_assertions)
def test_deposit_tokens(input_value, expected_error_type):
    with pytest.raises(expected_error_type):
        bee = BeeDebug(MOCK_SERVER_URL, input_value)
        bee.deposit_tokens("1", "0", input_value)


def test_deposit_tokens_no_headers_if_no_gas_price_is_set(requests_mock):
    url = "http://localhost:12345/chequebook/deposit?amount=10"

    requests_mock.post(url, json=CASHOUT_RESPONSE)

    bee = BeeDebug(MOCK_SERVER_URL)

    assert bee.deposit_tokens("10") == TRANSACTION_HASH


def test_deposit_tokens_if_gas_price_is_set(requests_mock):
    url = "http://localhost:12345/chequebook/deposit?amount=10"

    requests_mock.post(url, headers={"gas-price": "100000000000"}, json=CASHOUT_RESPONSE)

    bee = BeeDebug(MOCK_SERVER_URL)

    assert bee.deposit_tokens("10", "100000000000") == TRANSACTION_HASH


def test_deposit_tokens_if_gas_limit_is_set(requests_mock):
    url = "http://localhost:12345/chequebook/deposit?amount=10"

    requests_mock.post(url, headers={"gas-limit": "100000000000"}, json=CASHOUT_RESPONSE)

    bee = BeeDebug(MOCK_SERVER_URL)

    assert bee.deposit_tokens("10", "100000000000") == TRANSACTION_HASH


@pytest.mark.parametrize("input_value, expected_error_type", [(None, ValueError), ("", ValueError), (-1, ValueError)])
def test_deposit_tokens_wrong_input(input_value, expected_error_type):
    bee = BeeDebug(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        assert bee.deposit_tokens(input_value)


@pytest.mark.parametrize(
    "input_value, expected_error_type", [(True, ValueError), ("asd", ValueError), ("-1", ValueError)]
)
def test_deposit_tokens_throw_error_if_passed_wrong_gas_price_as_input(input_value, expected_error_type):
    bee = BeeDebug(MOCK_SERVER_URL)
    with pytest.raises(expected_error_type):
        assert bee.deposit_tokens("1", input_value)
