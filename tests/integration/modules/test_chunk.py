import pytest
import requests

from bee_py.modules.chunk import download, upload


def test_store_retreive_data(bee_ky_options, get_debug_postage):
    payload = bytes([1, 2, 3])
    span = bytes([len(payload), 0, 0, 0, 0, 0, 0, 0])
    data = bytes([*span, *payload])

    reference = "ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"
    # the hash is hardcoded because we would need the bmt hasher otherwise
    response = upload(bee_ky_options, data, get_debug_postage)

    assert str(response) == reference

    downloaded_data = download(bee_ky_options, response)

    assert downloaded_data.hex() == data.hex()


def test_fail_downalding_data(bee_debug_ky_options):
    invalid_reference = "0000000000000000000000000000000000000000000000000000000000000000"

    with pytest.raises(requests.exceptions.HTTPError):
        download(bee_debug_ky_options, invalid_reference)
