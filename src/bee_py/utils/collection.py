# from bee_py.types.type import Collection
# from bee_py.utils.error import BeeArgumentError
from typing import Any


def is_collection(data: Any):
    if not isinstance(data, list):
        return False

    return all(
        isinstance(entry, dict) and "data" in entry and "path" in entry and isinstance(entry["data"], bytes)
        for entry in data
    )


def assert_collection(data: Any):
    if not is_collection(data):
        msg = "invalid collection"
        raise ValueError(msg)
