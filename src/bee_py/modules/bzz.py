from typing import Optional, Union

from bee_py.types.type import (  # Reference, UploadHeaders, Data,
    BatchId,
    BeeRequestOptions,
    Collection,
    CollectionUploadHeaders,
    CollectionUploadOptions,
    FileData,
    FileHeaders,
    FileUploadHeaders,
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


def extract_file_upload_headers(
    postage_batch_id: BatchId, options: Optional[FileUploadOptions] = None
) -> FileUploadHeaders:
    headers = extract_upload_headers(postage_batch_id, options)

    if options and options.size:
        headers.content_length = str(options.size)

    if options and options.content_type:
        headers.content_type = options.content_type

    return headers


def upload_file(
    request_options: BeeRequestOptions,
    data: Union[str, bytes],
    postage_batch_id: BatchId,
    name: Optional[str] = None,
    options: Optional[FileUploadOptions] = None,
):
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

    if options.content_type:
        options = options or {}
        options.content_type = "application/octet-stream"

    headers = extract_file_upload_headers(postage_batch_id, options)

    config = {
        "url": BZZ_ENDPOINT,
        "method": "POST",
        "data": data,
        "headers": headers,
        "params": {"name": name},
    }
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

    config = {"url": f"{BZZ_ENDPOINT}/{_hash}/{path}", "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        logger.error(response.raise_for_status())

    file_headers = FileHeaders.parse_obj(read_file_headers(response.headers))
    file_data = wrap_bytes_with_helpers(response.content).text()

    return FileData(headers=file_headers, data=file_data)


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
        logger.error(response.raise_for_status())

    file_headers = read_file_headers(response.headers)
    file_data = response.data

    return FileData(file_headers, file_data)


def extract_collection_upload_headers(
    postage_batch_id: BatchId, options: Optional[CollectionUploadOptions] = None
) -> CollectionUploadHeaders:
    """
    Extracts headers for collection upload requests.

    Args:
        postage_batch_id (BatchId): Postage Batch ID to be used for the upload.
        options (CollectionUploadOptions | None): Optional collection upload options,
        such as index document and error document.

    Returns:
        CollectionUploadHeaders: Extracted collection upload headers.
    """

    headers = extract_upload_headers(postage_batch_id, options)

    if options and options.index_document:
        headers.swarm_index_document = options.index_document

    if options and options.error_document:
        headers.swarm_error_document = options.error_document

    return headers


def upload_collection(
    request_options: BeeRequestOptions,
    collection: Collection,
    postage_batch_id: BatchId,
    options: Optional[CollectionUploadOptions] = None,
) -> UploadResult:
    """
    Uploads a collection of data to the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        collection (Collection[Uint8Array]): Collection of data to upload.
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
        logger.error(response.raise_for_status())

    upload_response = response.json()
    reference = Reference(upload_response["reference"])
    tag_uid = None

    if "swarm-tag" in response.headers:
        tag_uid = make_tag_uid(response.headers["swarm-tag"])

    return UploadResult(reference=reference, tag_uid=tag_uid)