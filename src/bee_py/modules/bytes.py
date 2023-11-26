from typing import Optional, Union

from bee_py.types.type import BatchId, BeeRequestOptions, Data, Reference, ReferenceOrENS, UploadOptions, UploadResult
from bee_py.utils.bytes import wrap_bytes_with_helpers
from bee_py.utils.headers import extract_upload_headers
from bee_py.utils.http import http
from bee_py.utils.logging import logger
from bee_py.utils.type import make_tag_uid

BYTES_ENDPOINT = "bytes"


def upload(
    request_options: BeeRequestOptions,
    data: Union[str, bytes],
    postage_batch_id: BatchId,
    options: Optional[UploadOptions] = None,
):
    """
    Uploads data to a Bee node using the specified postage batch ID and options.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        data (str | bytes): Data to be uploaded.
        postage_batch_id (BatchId): Postage Batch ID to be used for the upload.
        options (Optional[UploadOptions]): Optional upload options, such as tag, encryption, and pinning.

    Returns:
        UploadResult: The result of the upload operation.
    """

    headers = {
        "content-type": "application/octet-stream",
        **extract_upload_headers(postage_batch_id, options),
    }

    config = {"url": BYTES_ENDPOINT, "method": "POST", "data": data, "headers": headers}
    response = http(request_options, config)

    if response.status_code != 201:  # noqa: PLR2004
        logger.info(response.json())
        logger.error(response.raise_for_status())

    upload_response = response.json()
    reference = Reference(upload_response["reference"])
    tag_uid = None

    if "swarm-tag" in response.headers:
        tag_uid = make_tag_uid(response.headers["swarm-tag"])
    return UploadResult(reference=reference, tag_uid=tag_uid)


def download(request_options: BeeRequestOptions, _hash: ReferenceOrENS) -> Data:
    """
    Downloads data from the Bee node as a byte array.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        hash (ReferenceOrEns): Bee content reference or ENS domain to be downloaded.

    Returns:
        Data: Downloaded data as a byte array.
    """

    config = {"url": f"{BYTES_ENDPOINT}/{_hash}", "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        logger.error(response.raise_for_status())

    return wrap_bytes_with_helpers(response.content)


def download_readable(request_options: BeeRequestOptions, _hash: ReferenceOrENS) -> bytes:
    """
    Downloads data from the Bee node as a readable stream.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        hash (ReferenceOrEns): Bee content reference or ENS domain to be downloaded.

    Returns:
        bytes: Readable stream of the downloaded data.
    """

    config = {"url": f"{BYTES_ENDPOINT}/{_hash}", "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        logger.error(response.raise_for_status())

    return response
