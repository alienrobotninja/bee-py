from typing import Optional

from bee_py.types.type import BatchId, BeeRequestOptions, Data, Reference, ReferenceOrENS, UploadOptions
from bee_py.utils.bytes import wrap_bytes_with_helpers
from bee_py.utils.headers import extract_upload_headers
from bee_py.utils.http import http

ENDPOINT = "chunks"


def upload(
    request_options: BeeRequestOptions, data: bytes, postage_batch_id: BatchId, options: Optional[UploadOptions] = None
) -> Reference:
    """Uploads a chunk of data to a Bee node.

    Args:
        request_options: BeeRequestOptions instance containing the Bee node connection details.
        data: The chunk data to be uploaded.
        postage_batch_id: The postage batch ID to be assigned to the uploaded data.
        options: Optional UploadOptions instance containing additional upload options like tag, encryption, and pinning.

    Returns:
        The reference of the uploaded data.
    """

    config = {
        "url": f"/{ENDPOINT}",
        "method": "post",
        "data": data,
        "headers": {**extract_upload_headers(postage_batch_id, options)},
    }

    response = http(request_options, config)

    # *  Raises a HTTPError if the response status is 4xx, 5xx
    response.raise_for_status()

    return response.json()["reference"]


def download(request_options: BeeRequestOptions, _hash: ReferenceOrENS) -> Data:
    config = {
        "url": f"/{ENDPOINT}/{_hash}",
        "method": "get",
    }
    response = http(request_options, config)

    # * Raises a HTTPError if the response status is 4xx, 5xx
    response.raise_for_status()
    return wrap_bytes_with_helpers(response.content)
