from os.path import getsize

from item.level import Level, LevelNotFoundError

from . import Location

__all__ = ["LvlLevel"]


class LvlLevelNotFoundError(FileNotFoundError, LevelNotFoundError):
    pass


class LvlLevel(Level, Location):
    __slots__ = ()

    def delete(self) -> None:
        try:
            return Location.delete(self)
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
