from ape import accounts

from bee_py.chunk.cac import make_content_addressed_chunk
from bee_py.chunk.signer import sign
from bee_py.chunk.soc import make_single_owner_chunk
from bee_py.modules.soc import upload
from bee_py.utils.hex import bytes_to_hex, hex_to_bytes


def test_single_owner_chunk_creation():
    payload = bytes([1, 2, 3])
    soc_hash = "9d453ebb73b2fedaaf44ceddcf7a0aa37f3e3d6453fea5841c31f0ea6d61dc85"
    identifier = bytearray(32)

    cac = make_content_addressed_chunk(payload)
    print(bytes_to_hex(cac.data))

    signer = accounts.load("bee")
    signer.set_autosign(True, passphrase="a")

    soc = make_single_owner_chunk(cac, identifier, signer)
    print(bytes_to_hex(soc.data))

    soc_address = bytes_to_hex(soc.address)
    owner = soc.owner

    assert soc_address == soc_hash
    assert owner == signer.address
