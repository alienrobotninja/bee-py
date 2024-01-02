from unittest.mock import patch

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
