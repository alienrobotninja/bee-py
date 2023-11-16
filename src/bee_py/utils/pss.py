from bee_py.types.type import PSS_TARGET_HEX_LENGTH_MAX, AddressPrefix


def make_max_target(target: str) -> AddressPrefix:
    """Returns the most specific target that a Bee node will accept.

    Args:
      target: The non-prefixed hex string of the Bee address.

    Returns:
      The most specific target that a Bee node will accept.
    """

    if not isinstance(target, str):
        msg = "Target must be a string!"
        raise TypeError(msg)

    return target[:PSS_TARGET_HEX_LENGTH_MAX]
