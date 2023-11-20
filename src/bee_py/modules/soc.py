from typing import Optional

from bee_py.types.type import BatchId, BeeRequestOptions, Reference, UploadOptions
from bee_py.utils.headers import extract_upload_headers
from bee_py.utils.http import http

SOC_ENDPOINT = "soc"


def upload(
    request_options: BeeRequestOptions,
    owner: str,
    identifier: str,
    signature: str,
    data: bytes,
    postage_batch_id: BatchId,
    options: Optional[UploadOptions] = None,
) -> Reference:
    """
    Uploads a single owner chunk (SOC) to a Bee node.

    Args:
        request_options: BeeRequestOptions instance.
        owner: Owner's ethereum address in hex.
        identifier: Arbitrary identifier in hex.
        signature: Signature in hex.
        data: Content addressed chunk data to be uploaded.
        postage_batch_id: Postage BatchId that will be assigned to uploaded data.
        options: Additional options like tag, encryption, pinning.

    Returns:
        Reference: The reference of the uploaded chunk.
    """
    config = {
        "method": "post",
        "url": f"{SOC_ENDPOINT}/{owner}/{identifier}",
        "data": data,
        "headers": {
            "content-type": "application/octet-stream",
            **extract_upload_headers(postage_batch_id, options),
        },
        "responseType": "json",
        "params": {"sig": signature},
    }
    response = http(request_options, config)
    response.raise_for_status()

    return response.json()["reference"]
