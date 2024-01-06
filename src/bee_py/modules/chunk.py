from typing import Optional

from bee_py.types.type import BatchId, BeeRequestOptions, Data, Reference, ReferenceOrENS, UploadOptions
from bee_py.utils.bytes import wrap_bytes_with_helpers
from bee_py.utils.headers import extract_upload_headers
from bee_py.utils.http import http
from bee_py.utils.logging import logger

ENDPOINT = "chunks"


def upload(
    request_options: BeeRequestOptions,
    data: bytes,
    postage_batch_id: BatchId,
    options: Optional[UploadOptions] = None,
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
    response = http(request_options, config, False)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    return Reference(value=response.json()["reference"])


def download(request_options: BeeRequestOptions, _hash: ReferenceOrENS) -> Data:
    config = {
        "url": f"/{ENDPOINT}/{_hash}",
        "method": "GET",
    }

    response = http(request_options, config, False)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore
    return wrap_bytes_with_helpers(response.content)
