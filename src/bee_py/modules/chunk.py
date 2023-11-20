from typing import Optional

from bee_py.types.type import BatchId, BeeRequestOptions, Data, Reference, ReferenceOrENS, UploadOptions
from bee_py.utils.bytes import wrap_bytes_with_helpers
from bee_py.utils.headers import extract_upload_headers
from bee_py.utils.http import http

ENDPOINT = "chunk"


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
    headers = extract_upload_headers(postage_batch_id, options)

    config = {
        "url": request_options["url"] + f"/{ENDPOINT}",
        "method": "post",
        "data": data,
        "headers": headers,
        "responseType": "json",
    }

    response = http(request_options, config)

    # *  Raises a HTTPError if the response status is 4xx, 5xx
    response.raise_for_status()

    return response.json()["reference"]


def downalod(request_options: BeeRequestOptions, _hash: ReferenceOrENS) -> Data:
    config = {
        "url": f"{request_options['url']}/{ENDPOINT}/{_hash}",
        "method": "get",
        "responseType": "arraybuffer",
    }
    response = http(request_options, config)

    # * Raises a HTTPError if the response status is 4xx, 5xx
    response.raise_for_status()
    return wrap_bytes_with_helpers(response.content)
