from typing import NewType, Optional, Union

from ape.managers.accounts import AccountAPI
from eth_account import Account
from eth_typing import ChecksumAddress as AddressType
from hexbytes import HexBytes
from pydantic.dataclasses import dataclass

from bee_py.chunk.bmt import bmt_hash
from bee_py.chunk.cac import (
    MAX_PAYLOAD_SIZE,
    MIN_PAYLOAD_SIZE,
    Chunk,
    assert_valid_chunk_data,
    make_content_addressed_chunk,
)
from bee_py.chunk.serialize import serialize_bytes
from bee_py.chunk.signer import recover_address, sign
from bee_py.chunk.span import SPAN_SIZE
from bee_py.modules.chunk import download
from bee_py.modules.soc import upload
from bee_py.types.type import BatchId, BeeRequestOptions, Reference, UploadOptions, assert_address
from bee_py.utils.bytes import bytes_at_offset, bytes_equal, flex_bytes_at_offset
from bee_py.utils.error import BeeError
from bee_py.utils.hash import keccak256_hash
from bee_py.utils.hex import bytes_to_hex, hex_to_bytes

# * Global variables
IDENTIFIER_SIZE = 32
SIGNATURE_SIZE = 65

SOC_IDENTIFIER_OFFSET = 0
SOC_SIGNATURE_OFFSET = SOC_IDENTIFIER_OFFSET + IDENTIFIER_SIZE
SOC_SPAN_OFFSET = SOC_SIGNATURE_OFFSET + SIGNATURE_SIZE
SOC_PAYLOAD_OFFSET = SOC_SPAN_OFFSET + SPAN_SIZE

# Define a new type for Identifier
Identifier = NewType("Identifier", bytes)


@dataclass
class SingleOwnerChunkBase:
    """Abstract base class for Single Owner Chunks (SOCs).

    Represents a SOC, a type of chunk that allows a user to assign arbitrary data to an address
    and attest to the chunk's integrity with their digital signature. It defines the basic properties
    common to all SOCs.

    Attributes:
        identifier: The identifier of the SOC.
        signature: The signature of the SOC.
        owner: The owner of the SOC.
    """

    identifier: Identifier
    signature: bytes
    owner: AddressType


class SingleOwnerChunk(SingleOwnerChunkBase, Chunk):
    """Represents a Single Owner Chunk (SOC).

    A concrete implementation of the SingleOwnerChunkBase class. It represents a SOC
    with all its properties and behaviors defined.

    Attributes:
        data: The data contained in the SOC.
        identifier: The identifier of the SOC.
        signature: The signature of the SOC.
        span: The span of the SOC.
        payload: The payload of the SOC.
        address: The address of the SOC.
        owner: The owner of the SOC.
    """

    def __init__(
        self,
        data: bytes,
        identifier: Identifier,
        signature: bytes,
        span: bytes,
        payload: bytes,
        address: HexBytes,
        owner: AddressType,
    ):
        SingleOwnerChunkBase.__init__(self, identifier, signature, owner)
        self.data = data
        self.span = span
        self.payload = payload
        self.address = address


def recover_chunk_owner(data: bytes) -> AddressType:
    """Recovers the owner's Ethereum address from a single owner chunk (SOC).

    Args:
        data: The byte array representing the SOC data.

    Returns:
        The Ethereum address of the SOC's owner.
    """
    cac_data = data[SOC_SPAN_OFFSET:]
    chunk_address = bmt_hash(cac_data)
    signature = bytes_at_offset(data, SOC_SIGNATURE_OFFSET, SIGNATURE_SIZE)
    identifier = bytes_at_offset(data, SOC_IDENTIFIER_OFFSET, IDENTIFIER_SIZE)
    digest = keccak256_hash(identifier, chunk_address)
    owner_address = recover_address(signature, digest)

    return owner_address


def make_single_owner_chunk_from_data(data: bytes, address: AddressType) -> SingleOwnerChunk:
    """
    Verifies if the data is a valid single owner chunk.

    Args:
        data: The chunk data.
        address: The address of the single owner chunk.

    Returns:
        dict: A dictionary representing a single owner chunk.
    """
    owner_address = recover_chunk_owner(data)
    identifier = bytes_at_offset(data, SOC_IDENTIFIER_OFFSET, IDENTIFIER_SIZE)
    soc_address = keccak256_hash(identifier, owner_address)

    if bytes_equal(address, soc_address):
        msg = "SOC Data does not match given address!"
        raise BeeError(msg)

    def signature():
        return bytes_at_offset(data, SOC_SIGNATURE_OFFSET, SIGNATURE_SIZE)

    def span():
        return bytes_at_offset(data, SOC_SPAN_OFFSET, SPAN_SIZE)

    def payload():
        return flex_bytes_at_offset(data, SOC_PAYLOAD_OFFSET, MIN_PAYLOAD_SIZE, MAX_PAYLOAD_SIZE)

    # return {
    #     "data": data,
    #     "identifier": identifier,
    #     "signature": signature(),
    #     "span": span(),
    #     "payload": payload(),
    #     "address": soc_address,
    #     "owner": owner_address,
    # }
    return SingleOwnerChunk(
        data=data,
        identifier=identifier,
        signature=signature(),
        span=span(),
        payload=payload,
        address=soc_address,
        owner=owner_address,
    )


def make_soc_address(identifier: Identifier, address: AddressType) -> bytes:
    address_bytes = hex_to_bytes(address)
    return keccak256_hash(identifier, address_bytes)


def make_single_owner_chunk(
    chunk: Chunk,
    identifier: Identifier,
    signer: Union[AccountAPI, Account],
) -> SingleOwnerChunk:
    """
    Creates a single owner chunk object.

    Args:
        chunk: A chunk object used for the span and payload.
        identifier: The identifier of the chunk.
        signer: The singer interface for signing the chunk.
            signer can be a ape account API or a eth_account object.

    Returns:
        SingleOwnerChunk: SingleOwnerChunk object.
    """
    chunk_address = chunk.address()
    assert_valid_chunk_data(chunk.data, chunk_address)

    digest = keccak256_hash(identifier, chunk_address)
    signature = sign(account=signer, data=digest)

    if isinstance(signer, AccountAPI):
        encoded_signature = signature.encode_vrs()
        data = serialize_bytes(identifier, encoded_signature, chunk.span, chunk.payload())
    else:
        encoded_signature = signature.signature.hex()
        encoded_signature_bytes = hex_to_bytes(encoded_signature)
        data = serialize_bytes(identifier, encoded_signature_bytes, chunk.span, chunk.payload())

    address = make_soc_address(identifier, signer.address)

    # return {
    #     "data": data,
    #     "identifier": identifier,
    #     "signature": signature,
    #     "span": chunk.span,
    #     "payload": chunk.payload(),
    #     "address": address,
    #     "owner": signer.address,
    # }

    return SingleOwnerChunk(
        data=data,
        identifier=identifier,
        signature=encoded_signature,
        span=chunk.span,
        payload=chunk.payload(),
        address=address,
        owner=signer.address,
    )


def upload_single_owner_chunk(
    request_options: BeeRequestOptions,
    chunk: SingleOwnerChunk,
    postage_batch_id: BatchId,
    options: Optional[UploadOptions] = None,
) -> Reference:
    """Uploads a Single Owner Chunk (SOC) to the Bee network.

    Args:
        request_options: BeeRequestOptions for making requests.
        chunk: The SOC object to be uploaded.
        postage_batch_id: The Postage BatchId to be assigned to the uploaded data.
        options: Upload options for controlling the upload process.

    Returns:
        A Reference object representing the uploaded chunk.
    """
    # * Convert the owner, identifier, and signature to hexadecimal strings
    if isinstance(chunk.owner, bytes):
        owner = bytes_to_hex(chunk.owner)
    else:
        owner = chunk.owner
    identifier = bytes_to_hex(chunk.identifier)
    signature = bytes_to_hex(chunk.signature)

    # Serialize the chunk data, including the span and payload
    data = serialize_bytes(chunk.span, chunk.payload)

    # Upload the SOC data using the SOC API's upload method
    return upload(request_options, owner, identifier, signature, data, postage_batch_id, options)


def upload_single_owner_chunk_data(
    request_options: BeeRequestOptions,
    signer: dict,
    postage_batch_id: BatchId,
    identifier: Identifier,
    data: bytes,
    options: Optional[dict] = None,
) -> Reference:
    """
    Helper function to create and upload SOC.

    Args:
      request_options: Ky Options for making requests.
      signer: The singer interface for signing the chunk.
      postage_batch_id: Postage BatchId that will be assigned to uploaded data.
      identifier: The identifier of the chunk.
      data: The chunk data.
      options: Upload options.

    Returns:
      str: The reference of the uploaded chunk.
    """
    assert_address(postage_batch_id)
    cac = make_content_addressed_chunk(data)
    soc = make_single_owner_chunk(cac, identifier, signer)

    return upload_single_owner_chunk(request_options, soc, postage_batch_id, options)


def download_single_owner_chunk(
    request_options: BeeRequestOptions,
    owner_address: AddressType,
    identifier: Identifier,
) -> SingleOwnerChunk:
    """Downloads a Single Owner Chunk (SOC) from the Bee network.

    Args:
        request_options: BeeRequestOptions for making requests.
        owner_address: The Ethereum address of the SOC's owner.
        identifier: The identifier of the SOC.

    Returns:
        The downloaded SOC object.
    """

    # Compute the SOC address using the identifier and owner's address
    soc_address = make_soc_address(identifier, owner_address)

    # Download the SOC data from the Bee network using the provided URL
    data = download(request_options, bytes_to_hex(soc_address))

    # Construct the SOC object from the downloaded data and address
    return make_single_owner_chunk_from_data(data, soc_address)
