import eth_utils
import pytest
from eth_account.messages import encode_defunct
from eth_utils import is_same_address
from hexbytes import HexBytes

from bee_py.chunk.signer import public_key_to_address, recover_address, sign


def test_make_private_key_signer(signer, expected_signature_hex):
    msg = "Hi from bee_py"
    signature = sign(data=msg, account=signer)

    assert signature.encode_vrs().hex() == expected_signature_hex


def test_make_private_key_signer_bytes_data(signer, expected_signature_hex):
    msg = "Hi from bee_py"
    data = encode_defunct(text=msg)
    signature = sign(data=data, account=signer)

    assert signature.encode_vrs().hex() == expected_signature_hex


def test_recover_address_from_signature(signer):
    msg = encode_defunct(text="Hi from bee_py")
    signature = sign(data=msg, account=signer)
    recovered_address = recover_address(msg, signature)

    assert recovered_address == signer.address


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
