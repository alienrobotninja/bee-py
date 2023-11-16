import pytest

# from bee_py.utils.stamps import *


@pytest.mark.parametrize(
    "utilization, depth, bucket_depth, expected",
    [
        (4, 18, 16, 1),
    ],
)
def test_get_stamp_usage(stamp_usage, utilization, depth, bucket_depth, expected):  # noqa: ARG001
    assert stamp_usage == expected


@pytest.mark.parametrize(
    "depth, expected",
    [
        (20, 4 * 1024 * 1024 * 1024),
    ],
)
def test_get_stamp_maximum_capacity_bytes(stamp_maximum_capacity_bytes, depth, expected):  # noqa: ARG001
    assert stamp_maximum_capacity_bytes == expected


@pytest.mark.parametrize(
    "amount, price_per_block, block_time, expected",
    [
        (20_000_000_000, 24_000, 5, 4166666.6666666665),
    ],
)
def test_get_stamp_ttl_seconds(stamp_ttl_seconds, amount, price_per_block, block_time, expected):  # noqa: ARG001
    assert stamp_ttl_seconds == expected


@pytest.mark.parametrize(
    "depth, amount, expected",
    [
        (20, 20_000_000_000, 2.097152),
    ],
)
def test_get_stamp_cost_in_bzz(stamp_cost_in_bzz, depth, amount, expected):  # noqa: ARG001
    assert stamp_cost_in_bzz == expected


@pytest.mark.parametrize(
    "depth, amount, expected",
    [
        (20, 20_000_000_000, 20971520000000000),
    ],
)
def test_get_stamp_cost_in_plur(stamp_cost_in_plur, depth, amount, expected):
    assert stamp_cost_in_plur == expected
