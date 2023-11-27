import io
import tarfile
from typing import Protocol

from bee_py.types.type import Collection


class StringLike(Protocol):
    length: int

    def char_code_at(self, index: int) -> int:
        ...


def fix_unicode_path(path: str) -> StringLike:
    """Converts a string to utf8 Uint8Array and returns it as a string-like
    object that tar.append accepts as path
    """

    codes = path.encode("utf-8")

    return StringLike(length=len(codes), char_code_at=lambda index: codes[index])


def make_tar(data: Collection) -> bytes:
    """Creates a tar archive from the given data.

    Args:
        data: A list of tuples, where the first element of each tuple is the path
            of the entry in the archive, and the second element is the data of the
            entry.

    Returns:
        A bytes object containing the tar archive.
    """

    tar_io = io.BytesIO()
    with tarfile.open(fileobj=tar_io, mode="w") as tar:
        for entry in data:
            tar.addfile(tarfile.TarInfo(name=entry["path"]), io.BytesIO(entry["data"]))
    return tar_io.getvalue()
