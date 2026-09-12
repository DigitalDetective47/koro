from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from ..stage import Stage
from . import Slot

if TYPE_CHECKING:
    from _typeshed import StrPath
else:
    StrPath = Any


__all__ = ["FileSlot"]


class FileSlot(Slot, ABC):
    __match_args__ = ("path",)
    __slots__ = ("_path",)

    _path: Path

    def __init__(self, path: StrPath, /) -> None:
        parsed_path: Final[Path] = Path(path)
        if parsed_path.is_file():
            self._path = parsed_path.resolve(True)
        else:
            self._path = parsed_path.parent.resolve(True) / parsed_path.name

    def __bool__(self) -> bool:
        return self.path.is_file()

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
            return self.deserialize(self.path.read_bytes())
        except FileNotFoundError:
            return None

    @property
    def path(self) -> Path:
        return self._path

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.path!r})"

    def save(self, data: Stage | None, /) -> None:
        if data is None:
            self.path.unlink(True)
        else:
            self.path.write_bytes(self.serialize(data))

    @staticmethod
    @abstractmethod
    def serialize(stage: Stage, /) -> bytes:
        pass
