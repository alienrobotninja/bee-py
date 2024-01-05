import re

import pydantic
import pytest

from bee_py.bee_debug import BeeDebug
from bee_py.types.debug import NodeInfo
from bee_py.types.type import BatchId, BeeRequestOptions, CashoutOptions, PostageBatchOptions
from bee_py.utils.error import BeeArgumentError, BeeError

# * Global Variables
BLOCKCHAIN_TRANSACTION_TIMEOUT = 40_000
WAITING_USABLE_STAMP_TIMEOUT = 130_000


@pytest.mark.timeout(WAITING_USABLE_STAMP_TIMEOUT + BLOCKCHAIN_TRANSACTION_TIMEOUT)
def test_create_new_postage_batch_with_zero_amount(bee_debug_class):
    batch_id = bee_debug_class.create_postage_batch("10", 17)
    stamp = bee_debug_class.get_postage_batch(batch_id)

    assert stamp.batch_id

    all_batches = bee_debug_class.get_all_postage_batches()

    assert any(not batch.immutable_flag for batch in all_batches)


@pytest.mark.timeout(BLOCKCHAIN_TRANSACTION_TIMEOUT)
def test_not_wait_for_stamps_to_be_usable_if_specified(bee_debug_class):
    batch_id = bee_debug_class.create_postage_batch("1000", 17, {"waitForUsable": False})
    stamp = bee_debug_class.get_postage_batch(batch_id)

    assert stamp.usable is False


@pytest.mark.timeout(WAITING_USABLE_STAMP_TIMEOUT * 2 + BLOCKCHAIN_TRANSACTION_TIMEOUT * 4)
def immutable_true_and_false(bee_debug_class):
    bee_debug_class.create_postage_batch("1", 17, {"immutableFlag": True, "waitForUsable": True})
    bee_debug_class.create_postage_batch("1", 17, {"immutableFlag": False, "waitForUsable": True})

    all_batches = bee_debug_class.get_all_postage_batches()

    # Check if there is a batch with immutableFlag set to true
    assert any(batch.immutable_flag for batch in all_batches)

    # Check if there is a batch with immutableFlag set to false
    assert any(not batch.immutable_flag for batch in all_batches)


def test_all_properties(bee_debug_class):
    all_batches = bee_debug_class.get_all_postage_batches()

    assert len(all_batches) > 0

    for batch in all_batches:
        assert isinstance(batch.batch_id, str)
        assert isinstance(batch.utilization, (int, float))
        assert isinstance(batch.usable, bool)
        assert isinstance(batch.label, str)
        assert isinstance(batch.depth, (int, float))
        assert isinstance(batch.amount, str)
        assert isinstance(batch.bucket_depth, (int, float))
        assert isinstance(batch.block_number, int)
        assert isinstance(batch.immutable_flag, bool)
        assert isinstance(batch.batch_ttl, (int, float))
        assert isinstance(batch.exists, bool)


def test_buckets_all_properties(bee_debug_class):
    all_batches = bee_debug_class.get_all_postage_batches()

    assert len(all_batches) > 0

    batch_id = all_batches[0].batch_id
    buckets = bee_debug_class.get_postage_batch_buckets(batch_id)

    assert isinstance(buckets.depth, (int, float))
    assert isinstance(buckets.bucket_depth, (int, float))
    assert isinstance(buckets.bucket_upper_bound, (int, float))

    for bucket in buckets.buckets:
        assert isinstance(bucket.bucket_id, (int, float))
        assert isinstance(bucket.collisions, (int, float))


def test_error_with_negative_amount(bee_debug_class):
    with pytest.raises(ValueError):
        bee_debug_class.create_postage_batch("-1", 17)


def test_return_modes(bee_debug_class):
    # Get node info
    node_info = bee_debug_class.get_node_info()

    assert isinstance(node_info, NodeInfo)

    assert node_info.bee_mode
    assert node_info.chequebook_enabled
    assert node_info.swap_enabled

    my_regex = re.compile("^(dev|light|full)$")

    assert my_regex.match(node_info.bee_mode.value)

    # Check the types of 'chequebookEnabled' and 'swapEnabled'
    assert isinstance(node_info.chequebook_enabled, bool)
    assert isinstance(node_info.swap_enabled, bool)


def test_return_amount_staked(bee_debug_class):
    my_regex = re.compile("^[0-9]+$")

    assert my_regex.match(bee_debug_class.get_stake())


@pytest.mark.timeout(BLOCKCHAIN_TRANSACTION_TIMEOUT)
def test_deposit_staked(bee_debug_class):
    original_stake = bee_debug_class.get_stake()

    bee_debug_class.deposit_stake("100000000000000000")

    increased_stake = bee_debug_class.get_stake()

    assert int(increased_stake) - int(original_stake) == 10e16


def test_return_the_nodes_balances_and_other_data(bee_debug_class):
    node_info = bee_debug_class.get_node_info()

    assert isinstance(node_info.bee_mode.value, str)
    assert node_info.bee_mode.value in ["dev", "light", "full"]
    assert isinstance(node_info.chequebook_enabled, bool)
    assert isinstance(node_info.swap_enabled, bool)
