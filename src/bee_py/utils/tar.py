import io
import tarfile
from typing import Callable, Union

from pydantic import BaseModel

from bee_py.types.type import Collection, CollectionEntry


class StringLike(BaseModel):
    length: int

    char_code_at: Callable


def fix_unicode_path(path: str) -> StringLike:
    """Converts a string to utf8 Uint8Array and returns it as a string-like
    object that tar.append accepts as path
    """

    codes = path.encode("utf-8")

    return StringLike(length=len(codes), char_code_at=lambda index: codes[index])


def make_tar(data: Union[Collection, list[dict]]) -> bytes:
    """Creates a tar archive from the given data.

    Args:
        data: A list of tuples, where the first element of each tuple is the path
            of the entry in the archive, and the second element is the data of the
            entry.

    Returns:
        A bytes object containing the tar archive.
    """

    if isinstance(data, list):
        if not isinstance(data[0], CollectionEntry):
            # * Convert the list of dictionaries to a list of CollectionEntry objects
            entries = [CollectionEntry(**entry) for entry in data]
        else:
            entries = data
        # * Create a Collection object from the list of CollectionEntry objects
        data = Collection(entries=entries)

    tar_buffer = io.BytesIO()

    with tarfile.open(mode="w", fileobj=tar_buffer) as tar:
        for entry in data.entries:
            entry_path = entry.path
            entry_data = entry.data
            if not isinstance(entry_data, bytes):
                entry_data = entry_data.encode()

            info = tarfile.TarInfo(name=entry_path)
            info.size = len(entry_data)
            tar.addfile(info, io.BytesIO(entry_data))

    return tar_buffer.getvalue()
