import pytest
from eth_pydantic_types import HexBytes

from bee_py.utils.eth import (
    assert_eth_address,
    assert_swarm_network_id,
    eth_to_swarm_address,
    is_eth_addr_case_ins,
    is_hex_eth_address,
    is_valid_checksum_eth_address,
    make_ethereum_wallet_signer,
)


@pytest.mark.parametrize(
    "address, expected",
    [
        ("0xc6d9d2cd449a754c494264e1809c50e34d64562b", True),
        ("C6D9D2CD449A754C494264E1809C50E34D64562B", True),
        ("0xE247A45c287191d435A8a5D72A7C8dc030451E9F", False),
    ],
)
def test_is_eth_addr_case_ins(address, expected):
    assert is_eth_addr_case_ins(address) == expected


@pytest.mark.parametrize(
    "address, expected",
    [
        ("0x1815cac638d1525b47f848daf02b7953e4edd15c", False),
        ("0xE247A45c287191d435A8a5D72A7C8dc030451E9F", True),
        ("E247A45c287191d435A8a5D72A7C8dc030451E9F", False),
    ],
)
def test_is_valid_checksum_eth_address(address, expected):
    assert is_valid_checksum_eth_address(address) == expected


@pytest.mark.parametrize(
    "address, expected",
    [
        ("0xc6d9d2cd449a754c494264e1809c50e34d64562b", True),
        ("C6D9D2CD449A754C494264E1809C50E34D64562B", True),
        ("0x1815pac638d1525b47f848daf02b7953e4edd15c", False),
    ],
)
def test_is_hex_eth_address(address, expected):
    assert is_hex_eth_address(address) == expected


@pytest.mark.parametrize(
    "address, expected",
    [
        ("0xc6d9d2cd449a754c494264e1809c50e34d64562b", True),
        ("0xE247A45c287j91d435A8a5D72A7C8dc030451E9F", False),
    ],
)
def test_assert_eth_address(address, expected):
    if expected:
        assert assert_eth_address(address)
    else:
        with pytest.raises(ValueError):
            assert_eth_address(address)


@pytest.mark.parametrize(
    "network_id, expected",
    [
        (1, None),
        (0, TypeError),
        (-1, TypeError),
    ],
)
def test_assert_swarm_network_id(network_id, expected):
    if expected is None:
        assert not assert_swarm_network_id(network_id)
    else:
        with pytest.raises(expected):
            assert_swarm_network_id(network_id)


@pytest.mark.parametrize(
    "eth_address, network_id, nonce, expected",
    [
        (
            "1815cac638d1525b47f848daf02b7953e4edd15c",
            1,
            1,
            "0xa38f7a814d4b249ae9d3821e9b898019c78ac9abe248fff171782c32a3849a17",
        ),
        (
            "0x1815cac638d1525b47f848daf02b7953e4edd15c",
            1,
            1,
            "0xa38f7a814d4b249ae9d3821e9b898019c78ac9abe248fff171782c32a3849a17",
        ),
        (
            "d26bc1715e933bd5f8fad16310042f13abc16159",
            2,
            1,
            "0x9f421f9149b8e31e238cfbdc6e5e833bacf1e42f77f60874d49291292858968e",
        ),
        (
            "0xac485e3c63dcf9b4cda9f007628bb0b6fed1c063",
            1,
            0,
            "0xfe3a6d582c577404fb19df64a44e00d3a3b71230a8464c0dd34af3f0791b45f2",
        ),
        # failed tests
        ("0xE247A45c287191d435A8a5D72A7C8dc030451E9F", 1, -1, ValueError),
        ("0xE247A45c287191d435A8a5D72A7C8dc030451E9F", 1, "", TypeError),
    ],
)
def test_eth_to_swarm_address(eth_address, network_id, nonce, expected):
    if isinstance(expected, str):
        assert eth_to_swarm_address(eth_address, network_id, nonce).hex() == expected
    else:
        with pytest.raises(expected):
            eth_to_swarm_address(eth_address, network_id, nonce)


def test_make_ethereum_wallet_signer(alice):
    singer = make_ethereum_wallet_signer(account=alice, address=alice.address)
    message = "Hi from Bee"
    signed_msg = singer.sign(message)

    assert isinstance(signed_msg, HexBytes)

    assert (
        signed_msg.hex()
        == "0x1cf9026dbf03a852f8d83fdd33c995b37c6bd50c3b031c47a7ae4afec3f65eb1d7045f0fd0453e7fddd159ec81c60a50e815e57084022bed041f3ee99dbf9e0cb6"  # noqa: E501
    )


# This test will fail as we are using test accounts
def test_fail_make_ethereum_wallet_signer_address_only(alice):
    with pytest.raises(TypeError):
        make_ethereum_wallet_signer(address=alice.address)
