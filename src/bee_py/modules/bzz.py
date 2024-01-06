from typing import Optional, Union

from bee_py.types.type import (  # Reference,; UploadHeaders,; Data,; CollectionEntry,; CollectionUploadHeaders,; FileUploadHeaders,  # noqa: E501; FileHeaders,
    BatchId,
    BeeRequestOptions,
    Collection,
    CollectionUploadOptions,
    FileData,
    FileUploadOptions,
    Reference,
    ReferenceOrENS,
    UploadResult,
)
from bee_py.utils.bytes import wrap_bytes_with_helpers
from bee_py.utils.collection import assert_collection
from bee_py.utils.headers import extract_upload_headers, read_file_headers
from bee_py.utils.http import http
from bee_py.utils.logging import logger
from bee_py.utils.tar import make_tar
from bee_py.utils.type import make_tag_uid

BZZ_ENDPOINT = "bzz"


def extract_file_upload_headers(postage_batch_id: BatchId, options: Optional[FileUploadOptions] = None) -> dict:
    headers = extract_upload_headers(postage_batch_id, options)

    options = FileUploadOptions.model_validate(options)

    if options and options.size:
        headers["Content-Length"] = str(options.size)

    if options and options.content_type:
        headers["Content-Type"] = options.content_type

    return headers


def upload_file(
    request_options: BeeRequestOptions,
    data: Union[str, bytes],
    postage_batch_id: BatchId,
    name: Optional[str] = None,
    options: Optional[Union[FileUploadOptions, dict]] = None,
) -> UploadResult:
    """
    Uploads a single file to the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        data (str | bytes | Readable | ArrayBuffer): File data.
        postage_batch_id (BatchId): Postage Batch ID to be used for the upload.
        name (str | None): Optional name that will be attached to the uploaded file.
        options (FileUploadOptions | None): Optional file upload options, such as content length and content type.

    Returns:
        UploadResult: The result of the upload operation.
    """

    if options:
        if isinstance(options, dict):
            options = FileUploadOptions.model_validate(options)
            options.content_type = "application/octet-stream"
    else:
        options = FileUploadOptions()
        options.content_type = "application/octet-stream"

    headers = extract_file_upload_headers(postage_batch_id, options)

    config = {
        "url": BZZ_ENDPOINT,
        "method": "POST",
        "data": data,
        "headers": headers,
        "params": {"name": name},
    }
    response = http(request_options, config, False)

    if response.status_code != 201:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    upload_response = response.json()
    reference = Reference(value=upload_response["reference"])
    tag_uid = None

    tag_header = next((header for header in response.headers if header.lower() == "swarm-tag"), None)

    if tag_header:
        tag_uid = make_tag_uid(response.headers[tag_header])

    return UploadResult(reference=reference, tagUid=tag_uid)


def download_file(request_options: BeeRequestOptions, _hash: ReferenceOrENS, path: str = "") -> FileData:
    """
    Downloads a single file from a Bee node as a buffer.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        _hash (ReferenceOrEns): Bee file or collection _hash.
        path (str): Optional path to a single file within a collection.

    Returns:
        FileData: Downloaded file data.
    """

    if isinstance(_hash, Reference):
        _hash = str(_hash)

    config = {"url": f"{BZZ_ENDPOINT}/{_hash}/{path}", "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore
    file_headers = read_file_headers(response.headers)  # type: ignore
    file_data = wrap_bytes_with_helpers(response.content)

    # print(f"response.headers --->{response.headers}")

    return FileData(headers=file_headers, data=file_data.data)


def download_file_readable(request_options: BeeRequestOptions, _hash: ReferenceOrENS, path: str = "") -> FileData:
    """
    Downloads a single file from a Bee node as a readable stream.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        _hash (ReferenceOrEns): Bee file or collection hash.
        path (str): Optional path to a single file within a collection.

    Returns:
        FileData[ReadableStream[Uint8Array]]: Downloaded file data.
    """

    config = {"url": f"{BZZ_ENDPOINT}/{_hash}/{path}", "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    file_headers = read_file_headers(response.headers)  # type: ignore
    file_data = response.content

    return FileData(headers=file_headers, data=file_data)


def extract_collection_upload_headers(
    postage_batch_id: BatchId,
    options: Optional[Union[CollectionUploadOptions, dict]] = None,
) -> dict[str, str]:
    """
    Extracts headers for collection upload requests.

    Args:
        postage_batch_id (BatchId): Postage Batch ID to be used for the upload.
        options (CollectionUploadOptions | dict | None): Optional collection upload options,
        such as index document and error document.

    Returns:
        dict[str, str]: Extracted collection upload headers.
    """

    headers = extract_upload_headers(postage_batch_id, options)

    if isinstance(options, dict):
        options = CollectionUploadOptions.model_validate(options)

    if options and options.index_document:
        headers["swarm-index-document"] = options.index_document

    if options and options.error_document:
        headers["swarm-error-document"] = options.error_document

    return headers


def upload_collection(
    request_options: BeeRequestOptions,
    collection: Union[Collection, list],
    postage_batch_id: BatchId,
    options: Optional[Union[CollectionUploadOptions, dict]] = None,
) -> UploadResult:
    """
    Uploads a collection of data to the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        collection (Collection | list): Collection of data to upload.
        postage_batch_id (BatchId): Postage Batch ID to be used for the upload.
        options (CollectionUploadOptions | None): Optional collection upload options,
        such as index document and error document.

    Returns:
        UploadResult: The result of the upload operation.
    """

    assert_collection(collection)

    tar_data = make_tar(collection)

    headers = {
        "Content-Type": "application/x-tar",
        "swarm-collection": "true",
        **extract_collection_upload_headers(postage_batch_id, options),
    }

    config = {
        "url": BZZ_ENDPOINT,
        "method": "POST",
        "data": tar_data,
        "headers": headers,
    }
    response = http(request_options, config)

    if response.status_code != 201:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    upload_response = response.json()
    reference = Reference(value=upload_response["reference"])
    tag_uid = None

    if "Swarm-Tag" in response.headers:
        tag_uid = make_tag_uid(response.headers["Swarm-Tag"])

    return UploadResult(reference=reference, tagUid=tag_uid)
