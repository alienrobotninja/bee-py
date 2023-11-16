import re
from typing import Optional, Union

from bee_py.types.type import BatchId, FileHeaders, UploadOptions
from bee_py.utils.error import BeeError


def read_content_disposition_filename(header: Union[str, None]) -> str:
    """Reads the filename from the content-disposition header.

    See https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition

    Args:
      header: The content-disposition header value.

    Returns:
      The filename.
    """

    if not header:
        msg = "missing content-disposition header"
        raise BeeError(msg)

    # Regex was found here

    # https://stackoverflow.com/questions/23054475/javascript-regex-for-extracting-filename-from-content-disposition-header
    disposition_match = re.match(r"filename[^;\n]*=(UTF-\d['\"]*)?((['\"])(.*?[.])\4|[^;\n]*)", header, re.I)

    if disposition_match and len(disposition_match.groups()) > 0:
        return disposition_match.group(1)
    msg = "invalid content-disposition header"
    raise BeeError(msg)


def read_tag_uid(header: Union[str, None]) -> Union[int, None]:
    """Reads the tag UID from the header.

    Args:
      header: The header value.

    Returns:
      The tag UID, or None if the header is not present or is invalid.
    """

    if not header:
        return None

    try:
        return int(header, 10)
    except ValueError:
        return None


def read_file_headers(headers: dict[str, str]) -> FileHeaders:
    """Reads the file headers from the given HTTP headers.

    Args:
      headers: The HTTP headers.

    Returns:
      The file headers.
    """

    name = read_content_disposition_filename(headers.get("content-disposition"))
    tag_uid = read_tag_uid(headers.get("swarm-tag-uid"))
    content_type = headers.get("content-type")

    return FileHeaders(name, tag_uid, content_type)


def extract_upload_headers(postage_batch_id: BatchId, options: Optional[UploadOptions] = None) -> dict[str, str]:
    """Extracts the upload headers from the given postage batch ID and options.

    Args:
      postage_batch_id: The postage batch ID.
      options: The upload options.

    Returns:
      A dictionary of upload headers.
    """

    if not postage_batch_id:
        msg = "Postage BatchID has to be specified!"
        raise BeeError(msg)

    headers: dict[str, str] = {
        "swarm-postage-batch-id": postage_batch_id,
    }

    if options is not None:
        if options.pin:
            headers["swarm-pin"] = str(options.pin)
        if options.encrypt:
            headers["swarm-encrypt"] = str(options.encrypt)
        if options.tag:
            headers["swarm-tag"] = str(options.tag)
        if options.deferred is not None:
            headers["swarm-deferred-upload"] = str(options.deferred)

    return headers