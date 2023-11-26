import pytest
import requests

from bee_py.modules.bytes import download, download_readable, upload


def test_store_and_retrieve_data(bee_ky_options, get_debug_postage):
    data = "hello world"

    result = upload(bee_ky_options, data, get_debug_postage)
    downloaded_data = download(bee_ky_options, result.reference)

    assert downloaded_data.text() == data


def test_fail_retrieve_data(bee_ky_options):
    data = "hello world"
    invalid_postage = "fd9d9fbd6d1a65db4b40e1c410aeeadd1db227e51fc5af6da01e65eb1de2dd61"
    with pytest.raises(requests.exceptions.HTTPError):
        upload(bee_ky_options, data, invalid_postage)
