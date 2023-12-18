from bee_py.chunk.cac import make_content_addressed_chunk
from bee_py.chunk.soc import make_single_owner_chunk, upload_single_owner_chunk
from bee_py.utils.hex import bytes_to_hex

payload = bytes([1, 2, 3])
identifier = bytearray(32)
soc_hash = "8976a1ed19644f9b7d0e654dc427fd7b902f7b13f337ea05794f96fd6a2014eb"


def test_upload_single_owner_chunk(
    signer,
    payload,
    bee_ky_options,
    get_debug_postage,
    try_delete_chunk_from_local_storage,
):
    cac = make_content_addressed_chunk(payload)

    # * import the account first by doing
    # * ape accounts import 634fb5a872396d9693e5c9f9d7233cfa93f395c093371017ff44aa9ae6564cdd
    # * Don't need this for intergration tests
    # signer = accounts.load("bee")
    # signer.set_autosign(True, passphrase="a")

    cac = make_content_addressed_chunk(payload)
    soc = make_single_owner_chunk(cac, identifier, signer)
    soc_address = bytes_to_hex(soc.address)

    assert try_delete_chunk_from_local_storage(soc_hash)

    response = upload_single_owner_chunk(bee_ky_options, soc, get_debug_postage)

    assert soc_address == response
