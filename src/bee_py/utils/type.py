from typing import Union

from bee_py.types.type import Tag


def assert_non_negative_integer(value: Union[int, str], name: str = "Value"):
    """
    Assert that the provided value is a non-negative integer.

    Args:
        value (Union[int, str]): The value to check.
        name (str, optional): The name of the value. Defaults to 'Value'.

    Raises:
        ValueError: If the value is not a non-negative integer.
    """
    if not isinstance(value, (int, str)):
        msg = f"{name} must be a number or a string representing a number"
        raise ValueError(msg)
    value = int(value) if isinstance(value, str) else value
    if value < 0:
        msg = f"{name} has to be bigger or equal to zero"
        raise ValueError(msg)


def make_tag_uid(tag_uid: Union[int, str, None]) -> int:
    """
    Utility function that returns Tag UID

    Args:
        tag_uid (Union[int, str, None]): The tag UID to check.

    Returns:
        int: The tag UID as an integer.

    Raises:
        TypeError: If the tag UID is not a non-negative integer.
    """
    if tag_uid is None:
        msg = "TagUid was expected but got null instead!"
        raise TypeError(msg)

    if isinstance(tag_uid, Tag):
        return tag_uid.uid
    elif isinstance(tag_uid, int):
        assert_non_negative_integer(tag_uid, "UID")
        return tag_uid
    elif isinstance(tag_uid, str):
        try:
            int_value = int(tag_uid)
            if int_value < 0:
                msg = f"TagUid was expected to be positive non-negative integer! Got {int_value}"
                raise TypeError(msg)
            return int_value
        except ValueError:
            msg = "Passed tagUid string is not valid integer!"
            raise TypeError(msg)  # noqa: B904
    msg = "tagUid has to be either Tag or a number (UID)!"
    raise TypeError(msg)
