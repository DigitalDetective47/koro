from os.path import getsize
from warnings import warn

from ..level import Level, LevelNotFoundError
from . import Location

__all__ = ["LvlLevel", "LvlLevelNotFoundError"]


class LvlLevelNotFoundError(FileNotFoundError, LevelNotFoundError):
    pass


class LvlLevel(Location, Level):
    __slots__ = ()

    def __init__(self, path: str, /) -> None:
        super().__init__(path)
        warn(
            FutureWarning(
                "The LVL format for storing level data is deprecated. Level data should be converted to the BIN format using BinLevel for better compression and compatibility."
            )
        )

    def delete(self) -> None:
        try:
            return super().delete()
        except FileNotFoundError as e:
            raise LvlLevelNotFoundError(*e.args)

    def __len__(self) -> int:
        return getsize(self.path)

    def read(self) -> bytes:
        with open(self.path, "rb") as f:
            return f.read()

    def write(self, new_content: bytes, /) -> None:
        with open(self.path, "wb") as f:
            f.write(new_content)
