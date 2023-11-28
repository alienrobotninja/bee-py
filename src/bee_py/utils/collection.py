# from bee_py.utils.error import BeeArgumentError
from typing import Any

from bee_py.types.type import Collection


def is_collection(data: Any):
    if not isinstance(data, list):
        if not isinstance(data, Collection):
            return False
    return True


def assert_collection(data: Any):
    if not is_collection(data):
        msg = "invalid collection"
        raise ValueError(msg)
