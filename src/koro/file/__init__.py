from os import remove
from os.path import abspath, exists
from shutil import rmtree


class Location:
    __match_args__ = ("path",)
    __slots__ = ("_path",)

    _path: str

    def __init__(self, path: str, /) -> None:
        self._path = abspath(path)

    def __bool__(self) -> bool:
        """Whether this file location is accessible and exists."""
        return exists(self.path)

    def delete(self) -> None:
        try:
            remove(self.path)
        except IsADirectoryError:
            rmtree(self.path)

    def __eq__(self, other: object, /) -> bool:
        return (
            self.path == other.path if isinstance(other, Location) else NotImplemented
        )

    def __hash__(self) -> int:
        return hash(self.path)

    @property
    def path(self) -> str:
        return self._path

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.path!r})"
