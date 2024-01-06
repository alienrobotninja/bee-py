from typing import Optional

from bee_py.types.type import BatchId, BeeRequestOptions, Reference, UploadOptions
from bee_py.utils.headers import extract_upload_headers
from bee_py.utils.hex import remove_0x_prefix
from bee_py.utils.http import http
from bee_py.utils.logging import logger

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
    # * https://docs.ethswarm.org/api/#tag/Single-owner-chunk
    owner = remove_0x_prefix(owner)
    identifier = remove_0x_prefix(identifier)
    signature = remove_0x_prefix(signature)

    config = {
        "method": "post",
        "url": f"{SOC_ENDPOINT}/{owner}/{identifier}",
        "data": data,
        "headers": {
            "Content-Type": "application/octet-stream",
            **extract_upload_headers(postage_batch_id, options),
        },
        "params": {"sig": signature},
    }
    logger.debug(f"\n***********Config***********\n{config}")

    response = http(request_options, config, False)  # Don't sanitise
    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    return Reference(value=response.json()["reference"])
