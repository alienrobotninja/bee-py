import pytest

from bee_py.types.type import BrandedString, Data, FlavoredType, HexString


def test_wrap_bytes_with_helpers_text(wrapped_bytes):
    assert wrapped_bytes.text() == "hello world"


def test_wrap_bytes_with_helpers_json(wrapped_bytes):
    assert wrapped_bytes.to_json() == {"hello": "world"}


def test_wrap_bytes_with_helpers_hex(wrapped_bytes):
    assert wrapped_bytes.hex() == "68656c6c6f20776f726c64"


def test_branded_string_tag():
    branded_string = BrandedString("hello world", "greeting")
    assert branded_string.tag == "greeting"


def test_flavored_type_tag():
    flavored_type = FlavoredType(int, "natural_number")
    assert flavored_type.tag == "natural_number"


def test_hex_string_length():
    with pytest.raises(ValueError):
        hex_string = HexString("0xabcdef0123456789", 19)
        assert hex_string.length == 19


def test_data_text():
    data = Data(data=b"hello world")
    assert data.text() == "hello world"


def test_data_json():
    data = Data(data=b'{"hello": "world"}')
    assert data.to_json() == {"hello": "world"}


def test_data_hex():
    data = Data(data=b"abcdef")
    assert data.hex() == "616263646566"


def test_data_str_json_output():
    data = Data(data="hello world")
    assert data.to_json() == {"hello": "world"}
