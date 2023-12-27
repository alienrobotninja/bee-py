import eth_utils
import pytest
from eth_account.messages import encode_defunct
from eth_pydantic_types import HexBytes
from eth_utils import is_same_address

from bee_py.chunk.signer import public_key_to_address, sign

expected_signature_hex = "1bf05d437c1146b84b2cd410a25b70d300abdd54f4df17256472b2402849c07b5c240387a4ab5dfdc49c150997f435a7e66d0d001ba59b87600423a583f50ed0d0"  # noqa: E501


def test_make_private_key_signer(signer):
    msg = "Hi from bee_py"
    signature = sign(data=msg, account=signer)

    assert signature.encode_vrs().hex() == expected_signature_hex  # type: ignore


def test_make_private_key_signer_bytes_data(signer):
    msg = "Hi from bee_py"
    data = encode_defunct(text=msg)
    signature = sign(data=data, account=signer)

    assert signature.encode_vrs().hex() == expected_signature_hex  # type: ignore


def test_public_key_str_to_address(signer, public_key_str):
    address = public_key_to_address(public_key_str)
    assert address == HexBytes(signer.address)


def test_public_key_bytes_to_address(signer, public_key_bytes):
    address = public_key_to_address(public_key_bytes)
    assert is_same_address(address.hex(), signer.address)


def test_public_key_publickey_object_to_address(signer, public_key):
    address = public_key_to_address(public_key)
    assert is_same_address(address.hex(), signer.address)


@pytest.mark.parametrize("pub_key", ["0x1234", "1234", "asd", 1, [], {}])
def test_fail_public_key_to_address(pub_key):
    if pub_key in ["0x1234", "1234"]:
        with pytest.raises(eth_utils.exceptions.ValidationError):
            public_key_to_address(pub_key)
    else:
        with pytest.raises(ValueError):
            public_key_to_address(pub_key)
