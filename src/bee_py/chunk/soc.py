from typing import NewType, Optional, Union

from ape.managers.accounts import AccountAPI
from eth_pydantic_types import HexBytes
from eth_typing import ChecksumAddress as AddressType
from pydantic import BaseModel, Field

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
from bee_py.types.type import (
    BatchId,
    BeeRequestOptions,
    Data,
    FeedUpdateOptions,
    Reference,
    Signer,
    UploadOptions,
    assert_address,
)
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


class SingleOwnerChunkBase(BaseModel):
    """Abstract base class for Single Owner Chunks (SOCs).

    Represents a SOC, a type of chunk that allows a user to assign arbitrary data to an address
    and attest to the chunk's integrity with their digital signature. It defines the basic properties
    common to all SOCs.

    Attributes:
        identifier: The identifier of the SOC.
        signature: The signature of the SOC.
        owner: The owner of the SOC.
    """

    identifier: Union[str, bytes] = Field(..., description="The identifier of the SOC")
    signature: bytes = Field(..., description="The signature of the SOC")
    owner: str = Field(..., description="The owner of the SOC")


class SingleOwnerChunk(Chunk, SingleOwnerChunkBase):
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

    pass


def recover_chunk_owner(data: bytes) -> Union[AddressType, str]:
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


def make_single_owner_chunk_from_data(
    data: Union[Data, bytes], address: Union[AddressType, bytes, str]
) -> SingleOwnerChunk:
    """
    Verifies if the data is a valid single owner chunk.

    Args:
        data: The chunk data.
        address: The address of the single owner chunk.

    Returns:
        dict: A dictionary representing a single owner chunk.
    """
    if isinstance(data, Data):
        data = data.data
    owner_address = recover_chunk_owner(data)
    identifier = bytes_at_offset(data, SOC_IDENTIFIER_OFFSET, IDENTIFIER_SIZE)
    soc_address = keccak256_hash(identifier, hex_to_bytes(owner_address[2:]))

    if bytes_equal(address, soc_address):  # type: ignore
        msg = "SOC Data does not match given address!"
        raise BeeError(msg)

    def signature() -> bytes:
        return bytes_at_offset(data, SOC_SIGNATURE_OFFSET, SIGNATURE_SIZE)

    def span() -> bytes:
        return bytes_at_offset(data, SOC_SPAN_OFFSET, SPAN_SIZE)

    def payload() -> bytes:
        return flex_bytes_at_offset(data, SOC_PAYLOAD_OFFSET, MIN_PAYLOAD_SIZE, MAX_PAYLOAD_SIZE)

    return SingleOwnerChunk(
        data=data,
        identifier=identifier,
        signature=signature(),
        span=span(),
        payload=payload(),
        address=soc_address,
        owner=owner_address,
    )


def make_soc_address(identifier: Union[Identifier, bytes], address: Union[AddressType, bytes, HexBytes, str]) -> bytes:
    if not isinstance(address, bytes):
        address_bytes = hex_to_bytes(address)
    return keccak256_hash(identifier, address_bytes)


def make_single_owner_chunk(
    chunk: Chunk,
    identifier: Union[Identifier, bytes],
    signer: Union[AccountAPI, Signer],
) -> SingleOwnerChunk:
    """
    Creates a single owner chunk object.

    Args:
        chunk: A chunk object used for the span and payload.
        identifier|bytearray: The identifier of the chunk.
        signer: The signer interface for signing the chunk.
            signer can be a ape account API or a eth_account object.

    Returns:
        SingleOwnerChunk: SingleOwnerChunk object.
    """

    if isinstance(identifier, bytearray):
        # make it in raw bytes
        identifier = bytes(identifier)

    chunk_address = chunk.address
    assert_valid_chunk_data(chunk.data, chunk_address)

    digest = keccak256_hash(identifier, chunk_address)
    if isinstance(signer, Signer):
        signer = signer.signer

    signature = sign(data=digest, account=signer)

    if isinstance(signer, AccountAPI):
        encoded_signature = signature.encode_rsv()  # type: ignore
        data = serialize_bytes(identifier, encoded_signature, chunk.span, chunk.payload)
    else:
        encoded_signature = signature.signature.hex()
        encoded_signature_bytes = hex_to_bytes(encoded_signature)
        data = serialize_bytes(identifier, encoded_signature_bytes, chunk.span, chunk.payload)

    address = make_soc_address(identifier, signer.address)

    return SingleOwnerChunk(
        data=data,
        identifier=identifier,
        signature=encoded_signature,
        span=chunk.span,
        payload=chunk.payload,
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
    signer: Union[Signer, AccountAPI],
    postage_batch_id: BatchId,
    identifier: Union[Identifier, bytes],
    data: bytes,
    options: Optional[Union[FeedUpdateOptions, BeeRequestOptions, dict]] = None,
) -> Reference:
    """
    Helper function to create and upload SOC.

    Args:
      request_options: Ky Options for making requests.
      signer: The signer interface for signing the chunk.
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

    return upload_single_owner_chunk(request_options, soc, postage_batch_id, options)  # type: ignore


def download_single_owner_chunk(
    request_options: BeeRequestOptions,
    owner_address: Union[AddressType, bytes],
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
