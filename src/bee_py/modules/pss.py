from typing import Optional, Union

import websockets

from bee_py.types.type import BatchId, BeeRequestOptions
from bee_py.utils.headers import extract_upload_headers
from bee_py.utils.http import http
from bee_py.utils.logging import logger

PSS_ENDPOINT = "pss"


def send(
    request_options: BeeRequestOptions,
    topic: str,
    target: str,
    data: Union[str, bytes],
    postage_batch_id: BatchId,
    recipient: Optional[str] = None,
) -> None:
    """
    Sends data to a recipient or target using the Postal Service for Swarm.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        topic (str): Topic name.
        target (str): Target message address prefix.
        data (str | bytes): Data to send.
        postage_batch_id (BatchId): Postage Batch ID to be assigned to the sent message.
        recipient (Optional[str]): Optional recipient public key.

    Returns:
        None
    """

    headers = extract_upload_headers(postage_batch_id)

    if recipient:
        headers["recipient"] = recipient

    config = {
        "url": f"{PSS_ENDPOINT}/send/{topic}/{target}",
        "method": "POST",
        "data": data,
        "headers": headers,
    }
    response = http(request_options, config)

    if response.status_code != 201:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore


async def subscribe(url: str, topic: str) -> websockets.WebSocketClientProtocol:
    """
    Subscribes to messages on the given topic.

    Args:
        url (str): Bee node URL.
        topic (str): Topic name.

    Returns:
        websockets.WebSocketClientProtocol: WebSocket connection to the subscription endpoint.
    """
    ws_url = url.replace("http", "ws")
    ws_url = f"{ws_url}/{PSS_ENDPOINT}/subscribe/{topic}"
    return await websockets.connect(ws_url)
