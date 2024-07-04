from abc import ABC, abstractmethod
from os import remove
from os.path import isfile
from typing import TYPE_CHECKING, Any

from ..stage import Stage
from . import Slot

if TYPE_CHECKING:
    from _typeshed import StrOrBytesPath
else:
    StrOrBytesPath = Any


class FileSlot(Slot, ABC):
    __match_args__ = ("path",)
    __slots__ = ("_path",)

    _path: StrOrBytesPath

    def __init__(self, path: StrOrBytesPath, /) -> None:
        self._path = path

    def __bool__(self) -> bool:
        return isfile(self.path)

    @staticmethod
    @abstractmethod
    def deserialize(data: bytes, /) -> Stage:
        pass

    def __eq__(self, other: object, /) -> bool:
        if isinstance(other, FileSlot) and (
            isinstance(other, type(self)) or isinstance(self, type(other))
        ):
            return self.path == other.path
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.path)

    def load(self) -> Stage | None:
        try:
            with open(self.path, "rb") as f:
                return self.deserialize(f.read())
        except FileNotFoundError:
            return None

    @property
    def path(self) -> StrOrBytesPath:
        return self._path

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.path!r})"

    def save(self, data: Stage | None) -> None:
        if data is None:
            remove(self.path)
        else:
            with open(self.path, "wb") as f:
                f.write(self.serialize(data))

    @staticmethod
    @abstractmethod
    def serialize(stage: Stage, /) -> bytes:
        pass
