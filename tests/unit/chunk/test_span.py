import pytest

from bee_py.chunk.span import make_span
from bee_py.utils.error import BeeArgumentError


@pytest.mark.parametrize(
    "length, expected_bytes",
    [
        (2**0, b"\x01\x00\x00\x00\x00\x00\x00\x00"),
        (2**4, b"\x10\x00\x00\x00\x00\x00\x00\x00"),
        (2**8, b"\x00\x01\x00\x00\x00\x00\x00\x00"),
        (2**16, b"\x00\x00\x01\x00\x00\x00\x00\x00"),
        (2**24, b"\x00\x00\x00\x01\x00\x00\x00\x00"),
        (2**32 - 1, b"\xff\xff\xff\xff\x00\x00\x00\x00"),
    ],
)
def test_make_span(length, expected_bytes):
    result = make_span(length)
    assert result == expected_bytes


def test_make_span_negative_length():
    with pytest.raises(BeeArgumentError):
        make_span(-1)


def test_make_span_zero_length():
    with pytest.raises(BeeArgumentError):
        make_span(0)


def test_make_span_too_big_length():
    with pytest.raises(BeeArgumentError):
        make_span(2**32)
