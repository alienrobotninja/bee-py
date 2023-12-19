from bee_py.chunk.cac import make_content_addressed_chunk
from bee_py.chunk.soc import make_single_owner_chunk
from bee_py.utils.hex import bytes_to_hex


def test_single_owner_chunk_creation(signer):
    payload = bytes([1, 2, 3])
    soc_hash = "6618137d8b33329d36ffa00cb97c130f871cbfe6f406ac63e7a30ae6a56a350f"
    identifier = bytearray(32)

    cac = make_content_addressed_chunk(payload)

    soc = make_single_owner_chunk(cac, identifier, signer)

    soc_address = bytes_to_hex(soc.address)
    owner = soc.owner

    assert soc_address == soc_hash
    assert owner == signer.address
