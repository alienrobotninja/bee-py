from bee_py.chunk.cac import make_content_addressed_chunk
from bee_py.chunk.soc import make_single_owner_chunk
from bee_py.utils.hex import bytes_to_hex


def test_single_owner_chunk_creation(signer):
    payload = bytes([1, 2, 3])
    soc_hash = "8976a1ed19644f9b7d0e654dc427fd7b902f7b13f337ea05794f96fd6a2014eb"
    identifier = bytearray(32)

    cac = make_content_addressed_chunk(payload)

    soc = make_single_owner_chunk(cac, identifier, signer)

    soc_address = bytes_to_hex(soc.address)
    owner = soc.owner

    assert soc_address == soc_hash
    assert owner == signer.address
