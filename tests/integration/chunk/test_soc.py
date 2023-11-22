from bee_py.chunk.cac import make_content_addressed_chunk
from bee_py.chunk.soc import make_single_owner_chunk, upload_single_owner_chunk
from bee_py.utils.hex import bytes_to_hex


# waiting for getPostageBatch
def test_upload_single_owner_chunk(
    signer, payload, soc_hash, bee_ky_options, get_postage_batch, try_delete_chunk_from_local_storage
):
    identifier = bytes([0] * 32)

    cac = make_content_addressed_chunk(payload)
    soc = make_single_owner_chunk(cac, identifier, signer)
    soc_address = bytes_to_hex(soc.get("address"))

    assert try_delete_chunk_from_local_storage(soc_hash)

    response = upload_single_owner_chunk(bee_ky_options, soc, get_postage_batch("bee_debug_url"))

    assert soc_address == response
