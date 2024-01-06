import json

from bee_py.types.type import BeeGenericResponse, BeeRequestOptions
from bee_py.utils.http import http

ENDPOINT = "chunks"


def check_if_chunk_exists_locally(
    request_options: BeeRequestOptions,
    address: str,
) -> BeeGenericResponse:
    """Checks if a chunk at the specified address exists locally.

    Args:
        request_options: BeeRequestOptions for making requests.
        address: The Swarm address of the chunk to check.

    Returns:
        A BeeGenericResponse object indicating whether the chunk exists or not.
    """

    response = http(
        request_options,
        {
            "url": f"{ENDPOINT}/{address}",
        },
    )
    status_code = response.status_code
    if status_code >= 400:  # noqa: PLR2004
        msg = f"Failed to check chunk existence: {status_code}"
        raise Exception(msg)

    return BeeGenericResponse(message=json.loads(response.text), code=status_code)


def delete_chunk_from_local_storage(
    request_options: BeeRequestOptions,
    address: str,
) -> BeeGenericResponse:
    """Deletes a chunk from local storage.

    Args:
        request_options: BeeRequestOptions for making requests.
        address: The Swarm address of the chunk to delete.

    Returns:
        A BeeGenericResponse object indicating whether the chunk was deleted or not.
    """

    response = http(
        request_options,
        {
            "method": "delete",
            "url": f"{ENDPOINT}/{address}",
        },
    )
    status_code = response.status_code
    if status_code >= 400:  # noqa: PLR2004
        msg = f"Failed to delete chunk: {status_code}"
        raise ValueError(msg)

    return BeeGenericResponse.model_validate_json(response.text)
