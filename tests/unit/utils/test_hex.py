import pytest

from bee_py.utils.hex import bytes_to_hex, hex_to_bytes, int_to_hex, is_hex_string, make_hex_string


def test_make_hex_string(test_data):
    test_bytes, test_hex = test_data
    assert make_hex_string("0xC0fFEE") == "C0fFEE"
    assert make_hex_string("C0FFEE") == "C0FFEE"
    with pytest.raises(ValueError):
        make_hex_string("")
        make_hex_string("COFFEE")
    assert make_hex_string("C0fFEE", 6) == "C0fFEE"
    assert make_hex_string("0xC0fFEE", 6) == "C0fFEE"
    with pytest.raises(ValueError):
        make_hex_string("C0fFEE", 5)
        make_hex_string("0xC0fFEE", 7)


@pytest.mark.parametrize(
    "input_value, expected_result",
    [
        ("C0FFEE", True),
        ("123C0FFEE", True),
        ("ZACOFFEE", False),
        ("", False),
        (None, False),
        (1, False),
        ({}, False),
        ([], False),
    ],
)
def test_is_hex_string(input_value, expected_result):
    assert is_hex_string(input_value) == expected_result


@pytest.mark.parametrize(
    "input_value, length, expected_result",
    [
        ("C0FFEE", 6, True),
        ("C0FFEE", 7, False),
    ],
)
def test_is_hex_string_with_length(input_value, length, expected_result):
    assert is_hex_string(input_value, length) == expected_result


def test_hex_to_bytes(test_data):
    _, test_hex = test_data
    assert hex_to_bytes(test_hex).hex() == test_hex


def test_bytes_to_hex(test_data):
    test_bytes, _ = test_data
    assert bytes_to_hex(test_bytes) == test_bytes.hex()


@pytest.mark.parametrize(
    "value, result, length, exception",
    [
        (1, "1", None, None),
        (1, "1", 1, None),
        (15, None, 2, ValueError),
        (16, "10", 2, None),
        (16, "10", None, None),
        (124, "7c", None, None),
        (28721856816, "6aff4c130", None, None),
        ("max_int", "1fffffffffffff", None, None),
        (124.1, None, None, TypeError),
        ("a", None, None, TypeError),
        ("0", None, None, TypeError),
        (-1, None, None, ValueError),
    ],
)
def test_int_to_hex(value, result, length, exception, request):
    if value == "max_int":
        value = request.getfixturevalue("max_int")

    if exception:
        with pytest.raises(exception):
            int_to_hex(value, length)
    else:
        assert int_to_hex(value, length) == result
