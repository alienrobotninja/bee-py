# from bee_py.utils.error import BeeArgumentError
import os
from pathlib import Path
from typing import Any, Union

from bee_py.types.type import Collection, CollectionEntry


def is_collection(data: Any):
    if not isinstance(data, list):
        if not isinstance(data, Collection):
            return False
    return True


def assert_collection(data: Any):
    if not is_collection(data):
        msg = "invalid collection"
        raise ValueError(msg)


def _make_filepath(file: Union[os.PathLike, str, Path]) -> str:
    """
    Extracts the filename from the provided file path.

    Args:
        file (Union[os.PathLike, str, Path]): The file path.

    Returns:
        str: The extracted filename.
    """
    if isinstance(file, str):
        file = Path(file)
    if file.is_file():
        return file.name

    msg = f"Invalid file path: {file}"
    raise TypeError(msg)


def make_collection_from_file_list(file_list: list[Union[os.PathLike, str]]) -> Collection:
    """
    Creates a collection of files from the provided file list.

    Args:
        file_list (list[Union[os.PathLike, str]]): A list of file paths.

    Returns:
        Collection: A list of dictionaries representing the files in the collection.
    """
    collection = []

    for file_path in file_list:
        if file_path:
            filename = _make_filepath(file_path)
            file_data = open(file_path, "rb").read()

            collection.append(
                CollectionEntry.model_validate(
                    {
                        "path": filename,
                        "data": bytearray(file_data),
                    }
                )
            )

    return collection


def get_collection_size(file_list: list[Union[os.PathLike, str]]) -> int:
    """
    Calculates the cumulative size of the files in the provided list.

    Args:
        file_list (List[Union[os.PathLike, str]]): A list of file paths.

    Returns:
        int: The cumulative size of the files in bytes.
    """
    total_size = 0

    for file_path in file_list:
        if file_path:
            try:
                file_size = os.path.getsize(file_path)
                total_size += file_size
            except OSError:
                pass  # Ignore invalid file paths or inaccessible files

    return total_size
