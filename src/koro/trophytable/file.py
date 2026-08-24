from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from .. import StageID
from . import TrophyRow, TrophyTable

if TYPE_CHECKING:
    from _typeshed import StrOrBytesPath
else:
    StrOrBytesPath = Any


__all__ = ["FileTrophyTable"]


class FileTrophyTable(TrophyTable, ABC):
    __match_args__ = ("path",)
    __slots__ = ("_path",)

    _path: StrOrBytesPath

    def __init__(self, path: StrOrBytesPath, /) -> None:
        self._path = path

    @staticmethod
    @abstractmethod
    def deserialize(data: bytes, /) -> Mapping[StageID, TrophyRow]:
        pass

    def __eq__(self, other: object, /) -> bool:
        if isinstance(other, FileTrophyTable) and (
            isinstance(other, type(self)) or isinstance(self, type(other))
        ):
            return self.path == other.path
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.path)

    def load(self) -> Mapping[StageID, TrophyRow]:
        with open(self.path, "rb") as f:
            return self.deserialize(f.read())

    @property
    def path(self) -> StrOrBytesPath:
        return self._path

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.path!r})"

    def save(self, data: Mapping[StageID, TrophyRow], /) -> None:
        with open(self.path, "wb") as f:
            f.write(self.serialize(data))

    @staticmethod
    @abstractmethod
    def serialize(stage: Mapping[StageID, TrophyRow], /) -> bytes:
        pass
