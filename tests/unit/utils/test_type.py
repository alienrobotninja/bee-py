import pytest


def is_integer(value):
    return isinstance(value, int)


@pytest.mark.parametrize(
    "value, expected",
    [
        # Wrong values
        (lambda: {}, False),
        (5.000000000000001, False),
        ("False", False),
        ("True", False),
        (float("inf"), False),
        (float("nan"), False),
        ([1], False),
        # Correct values
        (5, True),
        (0, True),
        (10, True),
        (-1, True),
    ],
)
def test_is_integer(value, expected):
    assert is_integer(value) == expected
