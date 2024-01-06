from typing import Optional, Union

from bee_py.types.type import BatchId, BeeRequestOptions, PostageBatch, PostageBatchBuckets, PostageBatchOptions
from bee_py.utils.http import http
from bee_py.utils.logging import logger

STAMPS_ENDPOINT = "stamps"
BATCHES_ENDPOINT = "batches"


def parse_postage_batch(response_json: dict) -> list[PostageBatch]:
    postage_batches = response_json.get("stamps", [])
    parsed_batches = []

    for batch_data in postage_batches:
        parsed_batches.append(PostageBatch.model_validate(batch_data))

    return parsed_batches


def get_global_postage_batches(request_options: BeeRequestOptions) -> list[PostageBatch]:
    """Retrieves all globally available postage batches.

    Args:
        request_options: Request options for making the API call.

    Returns:
        A list of all globally available postage batches.

    Raises:
        HTTPError: If the API request fails.
    """
    config = {"url": BATCHES_ENDPOINT, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    return parse_postage_batch(response.json())


def get_all_postage_batches(request_options: BeeRequestOptions) -> list[PostageBatch]:
    """
    Retrieves all postage batches from the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        PostageBatch: The list of postage batches.
    """

    config = {"url": STAMPS_ENDPOINT, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    return parse_postage_batch(response.json())


def get_postage_batch(
    request_options: BeeRequestOptions,
    postage_batch_id: BatchId,
) -> PostageBatch:
    """
    Retrieves a specific postage batch from the Bee node based on its ID.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        postage_batch_id (BatchId): The ID of the postage batch to retrieve.

    Returns:
        PostageBatch: The retrieved postage batch.
    """

    config = {"url": f"{STAMPS_ENDPOINT}/{postage_batch_id}", "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    return PostageBatch.model_validate(response.json())


def get_postage_batch_buckets(
    request_options: BeeRequestOptions,
    postage_batch_id: BatchId,
) -> PostageBatchBuckets:
    """
    Retrieves the buckets associated with a specific postage batch from the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        postage_batch_id (BatchId): The ID of the postage batch to retrieve buckets for.

    Returns:
        PostageBatchBuckets: The retrieved postage batch buckets.
    """

    config = {"url": f"{STAMPS_ENDPOINT}/{postage_batch_id}/buckets", "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    postage_batch_buckets = response.json()
    return PostageBatchBuckets.model_validate(postage_batch_buckets)


def create_postage_batch(
    request_options: BeeRequestOptions,
    amount: Union[int, str],
    depth: int,
    options: Optional[Union[PostageBatchOptions, dict]] = None,
) -> BatchId:
    """
    Creates a new postage batch with the specified amount, depth, and optional options.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        amount (int | str): The amount of postage to create.
        depth (int): The postage batch depth.
        options (PostageBatchOptions, optional): Optional postage batch options. Defaults to None.

    Returns:
        BatchId: The ID of the newly created postage batch.
    """

    headers = {}

    if isinstance(options, dict):
        if options and "gasPrice" in options:
            headers["gas-price"] = str(options["gasPrice"])

        if options and "immutableFlag" in options:
            headers["immutable"] = str(options["immutableFlag"])
    else:
        if options and options.gas_price:
            headers["gas-price"] = str(options.gas_price)

        if options and options.immutable_flag is not None:
            headers["immutable"] = str(options.immutable_flag)

    config = {
        "url": f"{STAMPS_ENDPOINT}/{amount}/{depth}",
        "method": "POST",
        "params": {"label": options.label if options else None},  # type: ignore
        "headers": headers,
    }
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    stamp_response = response.json()
    return stamp_response["batchID"]


def top_up_batch(
    request_options: BeeRequestOptions,
    _id: str,
    amount: Union[int, str],
) -> BatchId:
    """
    Tops up an existing postage batch with the specified amount.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        _id (str): The ID of the postage batch to top up.
        amount (int | str): The amount to add to the postage batch.

    Returns:
        BatchId: The ID of the postage batch after topping up.
    """

    url = f"{STAMPS_ENDPOINT}/topup/{_id}/{amount}"
    config = {"url": url, "method": "PATCH"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    stamp_response = response.json()
    return stamp_response["batchID"]


def dilute_batch(
    request_options: BeeRequestOptions,
    _id: str,
    depth: int,
) -> BatchId:
    """
    Dilutes an existing postage batch with the specified depth.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        _id (str): The ID of the postage batch to dilute.
        depth (int): The new depth for the postage batch.

    Returns:
        BatchId: The ID of the postage batch after diluting.
    """

    url = f"{STAMPS_ENDPOINT}/dilute/{_id}/{depth}"
    config = {"url": url, "method": "PATCH"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    stamp_response = response.json()
    return stamp_response["batchID"]
