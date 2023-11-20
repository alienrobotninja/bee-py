from typing import Optional

from bee_py.types.type import BatchId, BeeRequestOptions, Data, Reference, ReferenceOrENS, UploadOptions
from bee_py.utils.bytes import wrap_bytes_with_helpers
from bee_py.utils.headers import extract_upload_headers
from bee_py.utils.http import http

ENDPOINT = "bytes"
