import pytest
import requests

from bee_py.modules.chunk import download, upload


def test_store_retreive_data(bee_ky_options):
    payload = bytes([1, 2, 3])
    span = bytes([len(payload), 0, 0, 0, 0, 0, 0, 0])
    data = bytes([*span, *payload])

    get_debug_postage = "17b325d7ad88098eb2065ebfd505134fb61ee6b4fb2b44f9a44d97067f8c741d"

    reference = "ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"
    # the hash is hardcoded because we would need the bmt hasher otherwise
    response = upload(bee_ky_options, data, get_debug_postage)

    assert response == reference

    downaloded_data = download(bee_ky_options, response)

    assert downaloded_data.hex() == f"0x{data.hex()}"


def test_fail_downalding_data(bee_debug_ky_options):
    invalid_reference = "0000000000000000000000000000000000000000000000000000000000000000"

    with pytest.raises(requests.exceptions.HTTPError):
        download(bee_debug_ky_options, invalid_reference)
