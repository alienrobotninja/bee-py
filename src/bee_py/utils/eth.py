import re
import struct
from typing import Any, Optional, Union

from ape import accounts
from ape.managers.accounts import AccountAPI
from eth_account.messages import encode_defunct
from eth_pydantic_types import HexBytes
from eth_typing import ChecksumAddress as AddressType
from eth_utils import (
    is_address,
    is_checksum_address,
    keccak,
    to_checksum_address,  # ValidationError,
    to_normalized_address,
)

from bee_py.Exceptions import AccountNotFoundError
from bee_py.utils.hex import hex_to_bytes, str_to_hex

ETH_ADDR_BYTES_LENGTH = 20
ETH_ADDR_HEX_LENGTH = 40


class EthereumSigner:
    def __init__(self, account):
        self.account = account

    def sign(self, data: Union[bytes, str]) -> HexBytes:
        if isinstance(data, bytes):
            msg = encode_defunct(primitive=data)
        elif isinstance(data, str):
            msg = encode_defunct(text=data)
        # * for now returning only vrs encoded signature
        return HexBytes(self.account.sign_message(msg).encode_vrs())


def make_eth_address(address: Union[str, AddressType, Any]) -> Union[AddressType, bytes]:
    """
    Converts an Ethereum address to a 20-byte array.

    Args:
        address: The address to convert.

    Returns:
        The address as a 20-byte array.

    Raises:
        ValueError: If the address is invalid.
    """
    if isinstance(address, str):
        if not is_address(address):
            msg = "Invalid Ethereum address"
            raise ValueError(msg)
        return to_normalized_address(address)  # type: ignore

    if isinstance(address, bytes):
        if len(address) != ETH_ADDR_BYTES_LENGTH:
            msg = f"Invalid Ethereum address length: {len(address)} "
            raise ValueError(msg)
        return to_checksum_address(address)

    msg = "Invalid Ethereum address"
    raise ValueError(msg)


def make_hex_eth_address(address: Union[str, AddressType, Any]) -> Union[HexBytes, str]:
    """Converts an Ethereum address to a hexadecimal string.

    Args:
        address: The Ethereum address to convert. Can be a string, bytes, or bytearray.

    Returns:
        A hexadecimal string representing the Ethereum address.

    Raises:
        TypeError: If the address is not a valid Ethereum address.
    """
    if isinstance(address, bytes):
        return address.hex()
    try:
        # Convert the address to a bytes object.
        address_bytes = make_eth_address(address)

        # Convert the bytes object to a hexadecimal string.
        # hex_address = bytes_to_hex(address_bytes)

        return HexBytes(address_bytes)

    except TypeError as e:
        # * Wrap the error message to indicate that the address is an invalid hexadecimal Ethereum address.
        msg = f"Invalid HexEthAddress: {address}"
        raise TypeError(msg) from e


def is_eth_addr_case_ins(address: Union[str, bytes]) -> bool:
    """
    Check if this is all caps or small caps eth address (=address without checksum)
    @param address Ethereum address as hex string
    """
    if isinstance(address, str):
        return bool(re.match(r"^(0x|0X)?[0-9a-f]{40}$", address) or re.match(r"^(0x|0X)?[0-9A-F]{40}$", address))
    elif isinstance(address, bytes):
        return bool(re.match(rb"^(0x|0X)?[0-9a-f]{40}$", address) or re.match(rb"^(0x|0X)?[0-9A-F]{40}$", address))
    else:
        return False


def is_valid_checksum_eth_address(address: Union[str, bytes, HexBytes, AddressType]) -> bool:
    try:
        return is_checksum_address(address)
    except Exception as e:
        raise e


def is_hex_eth_address(address: Union[str, HexBytes, AddressType]) -> bool:
    """
    Check if is valid ethereum address
    @param address  Ethereum address as hex string
    @return True if is valid eth address
    """
    return is_eth_addr_case_ins(address) or is_valid_checksum_eth_address(address)


def assert_eth_address(address: Union[str, HexBytes, AddressType]) -> None:
    """Asserts if the address is a valid ethereum address"""
    if not is_address(address):
        msg = "Invalid Ethereum address"
        raise ValueError(msg)


def assert_swarm_network_id(network_id: int) -> None:
    """Asserts that a Swarm network ID is a valid positive integer.

    Args:
        network_id: The Swarm network ID to check.

    Raises:
        TypeError: If the network ID is not a valid positive integer.
    """

    if not isinstance(network_id, int) or network_id <= 0 or network_id >= 2**63:
        msg = "Swarm network ID must be a positive integer"
        raise TypeError(msg)


def eth_to_swarm_address(
    eth_address: Union[str, HexBytes, AddressType],
    network_id: Optional[int] = 1,
    nonce: Optional[Union[int, bytes]] = None,
) -> HexBytes:
    """Computes the Swarm overlay address from a public Ethereum address and Swarm network ID.

    Args:
        eth_address: The public Ethereum address.
        network_id: The Swarm network ID.
        nonce: The nonce as bytes or int.

    Returns:
        The Swarm overlay address.

    Raises:
        ValidationError: If the Ethereum address or network ID is invalid.
    """

    if not is_address(eth_address):
        msg = f"Invalid address: {eth_address!r}"
        raise ValueError(msg)
    if isinstance(network_id, int):
        if network_id < 0:
            msg = f"network_id can't be negative: {network_id}"
            raise ValueError(msg)

    if isinstance(nonce, int):
        if nonce < 0:
            msg = f"nonce can't be negative: {nonce}"
            raise ValueError(msg)

    if isinstance(eth_address, str):
        eth_address = str_to_hex(eth_address)

    if isinstance(nonce, str):
        if nonce.startswith("0x"):
            nonce = nonce[2:]
            nonce = bytes.fromhex(nonce)

    assert_swarm_network_id(network_id)  # type: ignore

    ethereum_address_bytes = hex_to_bytes(eth_address)

    # Prepare network ID and nonce bytes
    network_id_bytes = network_id.to_bytes(32, byteorder="little")  # type: ignore
    nonce_bytes = None
    if nonce is not None:
        if isinstance(nonce, int):
            # Pack nonce as big-endian 8-byte integer
            nonce_bytes = struct.pack(">Q", nonce)
        elif isinstance(nonce, bytes):
            nonce_bytes = nonce
        else:
            msg = "Invalid nonce type"
            raise TypeError(msg)

    # Combine bytes for address, network ID, and nonce
    combined_bytes = ethereum_address_bytes + network_id_bytes
    if nonce_bytes is not None:
        combined_bytes += nonce_bytes

    # Calculate and return the Swarm overlay address
    overlay_address = keccak(combined_bytes)

    return HexBytes(overlay_address)


# for now we are forcing to use ape
def make_ethereum_wallet_signer(
    account: Optional[AccountAPI],
    address: Optional[Union[str, HexBytes, AddressType]],
    auto_sign: Optional[bool] = False,  # noqa: FBT002
) -> EthereumSigner:
    """Creates a Signer instance that uses the `personal_sign` method to sign requested data.

    Args:
        address: The Ethereum address of the account to use for signing.
        If not specified, the first account setup in ape will be used.
        account: The account to use for signing

    Returns:
        A Signer instance.
    """
    if not account:
        if not address:
            account = accounts[0]
            address = account.address
        else:
            # * normalise the address
            address = to_normalized_address(address)
            if not is_address(address):
                msg = f"Invalid address: {address}"
                raise ValueError(msg)

            # * get the account from address to use for signing
            account_list = [a.address for a in accounts]
            account_index = account_list.index(address)  # type: ignore
            if not account_index:
                msg = f"Account with address '{address}' not found"
                raise AccountNotFoundError(msg)
            account = accounts[account_index]

    if auto_sign:
        # you have to set password as env variable
        # more info here: https://docs.apeworx.io/ape/stable/userguides/accounts.html#keyfile-passphrase-environment-variable-more-secure # noqa: E501
        account.set_autosign(True)  # type: ignore

    return EthereumSigner(account)
