from eth_pydantic_types import HexBytes
from eth_utils import keccak

MAX_CHUNK_PAYLOAD_SIZE = 4096
SEGMENT_SIZE = 32
SEGMENT_PAIR_SIZE = 2 * SEGMENT_SIZE
HASH_SIZE = 32


def bmt_root_hash(payload: bytes) -> bytes:
    """
    Calculates the root hash of a Binary Merkle Tree (BMT) built on the given payload.

    The BMT root hash is a cryptographic hash that represents the integrity of the entire BMT
    structure. It is calculated by iteratively hashing pairs of segments until a single hash
    value remains. The BMT root hash is used to verify the authenticity of data retrieved
    from a BMT-based data store.

    Args:
        payload (bytes): The data to be used to construct the BMT.

    Returns:
        bytes: The root hash of the BMT.
    """
    # Check if the payload length exceeds the maximum allowed size
    if len(payload) > MAX_CHUNK_PAYLOAD_SIZE:
        msg = "Invalid data length"
        raise ValueError(msg)

    # Pad the payload with zeros to reach the maximum chunk size
    padded_payload = payload + bytes(MAX_CHUNK_PAYLOAD_SIZE - len(payload))

    # Initialize the input buffer with the padded payload
    inp = padded_payload

    # Iteratively hash pairs of segments until the root hash is obtained
    while len(inp) != HASH_SIZE:
        output = bytearray(len(inp) // 2)

        # Apply the hashing function to each segment pair
        for offset in range(0, len(inp), SEGMENT_PAIR_SIZE):
            hash_numbers = keccak(inp[offset : offset + SEGMENT_PAIR_SIZE])
            output[offset // 2 : (offset + SEGMENT_PAIR_SIZE) // 2] = hash_numbers

        # Update the input buffer with the intermediate hash values
        inp = output

    return HexBytes(inp)


def bmt_hash(chunk_content: bytes) -> HexBytes:
    """
    Calculates the Binary Merkle Tree (BMT) hash for a given chunk of data.

    The BMT hash is a cryptographic hash that combines the chunk's span (an 8-byte identifier)
    with the root hash of a BMT built on the chunk's payload. The BMT hash is used to identify
    chunks within a BMT-based data store.

    Args:
        chunk_content (bytes): The chunk data, including the span and payload.

    Returns:
        bytes: The BMT hash of the chunk data.
    more info: https://www.ethswarm.org/The-Book-of-Swarm.pdf Page 55
    """
    # Extract the span and payload from the chunk content
    span = chunk_content[0:8]
    payload = chunk_content[8:]

    # Calculate the BMT root hash of the payload
    root_hash = bmt_root_hash(payload)

    # Create a chunk hash inp by combining the span and root hash
    chunk_hash_inp = bytearray(span + root_hash)

    # compute the keccak256 hash of the chunk hash input to obtain the BMT hash
    chunk_hash = keccak(chunk_hash_inp)

    return HexBytes(chunk_hash)
