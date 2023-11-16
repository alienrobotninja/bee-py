import tarfile
from typing import Protocol


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


def make_tar(data: list[tuple[str, bytes]]) -> bytes:
    """Creates a tar archive from the given data.

    Args:
        data: A list of tuples, where the first element of each tuple is the path
            of the entry in the archive, and the second element is the data of the
            entry.

    Returns:
        A bytes object containing the tar archive.
    """

    tar = tarfile.open("w:gz")

    for _, entry in enumerate(data):
        path, data = entry
        tar.add(fix_unicode_path(path), data)

    tar.close()

    return tar.getvalue()
