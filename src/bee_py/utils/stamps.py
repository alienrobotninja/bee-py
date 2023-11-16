import math


def get_stamp_usage(utilization: float, depth: int, bucket_depth: int) -> float:
    """Calculates the usage of a postage batch based on its utilization, depth, and bucket depth.

    Args:
      utilization: The utilization of the postage batch.
      depth: The depth of the postage batch.
      bucket_depth: The depth of the bucket.

    Returns:
      A number between 0 and 1 representing the usage of the postage batch.
    """

    return utilization / math.pow(2, depth - bucket_depth)


def get_stamp_maximum_capacity_bytes(depth: int) -> int:
    """Calculates the theoretical maximum capacity of a postage batch based on its depth.

    Args:
      depth: The depth of the postage batch.

    Returns:
      The maximum capacity of the postage batch in bytes.
    """

    return 2**depth * 4096


def get_stamp_cost_in_plur(depth: int, amount: int) -> int:
    """Calculates the cost of a postage batch based on its depth and amount.

    Args:
      depth: The depth of the postage batch.
      amount: The amount of the postage batch.

    Returns:
      The cost of the postage batch in PLUR (10000000000000000 [1e16] PLUR = 1 BZZ)
    """

    return 2**depth * amount


def get_stamp_cost_in_bzz(depth: int, amount: int) -> float:
    """Calculates the cost of a postage batch based on its depth and amount.

    Args:
      depth: The depth of the postage batch.
      amount: The amount of the postage batch.

    Returns:
      The cost of the postage batch in BZZ (1 BZZ = 10000000000000000 [1e16] PLUR)
    """

    BZZ_UNIT = 10**16  # noqa: N806

    return get_stamp_cost_in_plur(depth, amount) / BZZ_UNIT


def get_stamp_ttl_seconds(amount: int, price_per_block: int = 24_000, block_time: int = 5) -> float:
    """Calculates the TTL of a postage batch based on its amount, price per block, and block time.

    Args:
      amount: The amount of the postage batch.
      price_per_block: The price per block in PLUR.
      block_time: The block time in seconds.

    Returns:
      The TTL of the postage batch in seconds.
    """

    return (amount * block_time) / price_per_block
