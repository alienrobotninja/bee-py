from ape import accounts

from bee_py.chunk.cac import make_content_addressed_chunk
from bee_py.chunk.soc import make_single_owner_chunk
from bee_py.utils.hex import bytes_to_hex


def test_single_owner_chunk_creation():
    payload = bytes([1, 2, 3])
    soc_hash = "9d453ebb73b2fedaaf44ceddcf7a0aa37f3e3d6453fea5841c31f0ea6d61dc85"
    identifier = bytearray(32)

    cac = make_content_addressed_chunk(payload)

    signer = accounts.load("bee")
    signer.set_autosign(True, passphrase="a")

    soc = make_single_owner_chunk(cac, identifier, signer)

    soc_address = bytes_to_hex(soc.address)
    owner = soc.owner

    # * Remove the 0x
    assert soc_address[2:] == soc_hash
    assert owner == signer.address
