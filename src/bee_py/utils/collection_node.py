from pathlib import Path
from typing import Union

from bee_py.types.type import Collection, CollectionEntry


def make_collection_from_fs(directory: Union[str, Path]) -> Collection:
    if isinstance(directory, str):
        directory = Path(directory)
    if not isinstance(directory, Path):
        msg = "directory has to be a string or a Path object!"
        raise TypeError(msg)
    if directory.name == "":
        msg = "Directory must not be empty!"
        raise TypeError(msg)

    return build_collection_relative(directory, Path(""))


def build_collection_relative(directory: Path, relative_path: Path) -> Collection:
    dirname = directory / relative_path
    collection = Collection(entries=[])

    for entry in dirname.iterdir():
        full_path = directory / relative_path / entry.name
        entry_path = relative_path / entry.name

        if entry.is_file():
            with open(full_path, "rb") as f:
                data = f.read()
            collection.entries.append(CollectionEntry(path=str(entry_path), data=data))
        elif entry.is_dir():
            collection.entries += build_collection_relative(directory, entry_path).entries

    return collection
