from enum import Enum, unique
from io import BytesIO
from operator import index as ix
from os.path import basename, dirname, join
from typing import TYPE_CHECKING, Annotated, Any, Literal, SupportsIndex
from collections.abc import Mapping, Sequence

from ..stage import Stage

from . import Slot
from .xml import XmlSlot

if TYPE_CHECKING:
    from _typeshed import StrOrBytesPath
else:
    StrOrBytesPath = Any


__all__ = ["EditorPage", "get_slots", "SaveSlot"]


@unique
class EditorPage(Enum):
    ORIGINAL = 0
    FRIEND = 1
    HUDSON = 2


class SaveSlot(Slot):
    __match_args__ = ("path", "page", "index")
    __slots__ = ("_offset", "_path")

    _offset: Literal[8, 156392, 312776, 469160]
    _path: str | bytes

    def __init__(
        self,
        path: StrOrBytesPath,
        page: EditorPage,
        index: Annotated[
            SupportsIndex,
            Literal[
                1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20
            ],
        ],
    ) -> None:
        index = ix(index) - 1
        if index in range(0, 20):
            self._offset = 8 + 156864 * (index & 3)  # type: ignore[assignment]
            self._path = join(path, f"ed{(index >> 2) + 5 * page.value:02}.dat")  # type: ignore[arg-type]
        else:
            raise ValueError("index must be between 1 and 20")

    def __bool__(self) -> bool:
        try:
            with open(self._path, "rb") as f:
                f.seek(self._offset)
                return f.read(1) != b"\x00"
        except FileNotFoundError:
            return False

    def __eq__(self, other: Any, /) -> bool:
        if isinstance(other, SaveSlot):
            return self._path == other._path and self._offset == other._offset
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash((self._offset, self._path))

    @property
    def index(
        self,
    ) -> Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
        return (int(basename(self._path)[2:4]) % 5 >> 2 | self._offset // 156864) + 1  # type: ignore[return-value]

    def load(self) -> Stage | None:
        try:
            with open(self._path, "rb") as f:
                f.seek(self._offset)
                with BytesIO() as b:
                    block: bytearray = bytearray()
                    while True:
                        block.clear()
                        f.readinto1(block)
                        if len(b.getbuffer()) + len(block) > 156864:
                            del block[156864 - len(b.getbuffer()) :]
                        if block[-1]:
                            b.write(block)
                        else:
                            while block:
                                if block[len(block) >> 1]:
                                    b.write(block[: (len(block) >> 1) + 1])
                                    del block[: (len(block) >> 1) + 1]
                                else:
                                    del block[len(block) >> 1 :]
                            data: bytes = b.getvalue()
                            if data:
                                return XmlSlot.deserialize(data)
                            else:
                                return None
        except FileNotFoundError:
            return None

    @property
    def page(self) -> EditorPage:
        return EditorPage(int(basename(self._path)[2:4]) // 5)

    @property
    def path(self) -> StrOrBytesPath:
        return dirname(self._path)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.path!r}, {self.page!r}, {self.index!r})"

    def save(self, data: Stage | None) -> None:
        binary: bytes = b"" if data is None else XmlSlot.serialize(data)
        if len(binary) > 156864:
            raise ValueError("serialized stage data is too large to save")
        try:
            with open(self._path, "xb") as f:
                f.write(bytes(638976))
            if data is None:
                return
        except FileExistsError:
            pass
        with open(self._path, "r+b") as f:
            f.seek(self._offset)
            f.write(binary)
            f.write(bytes(156864 - len(binary)))


def get_slots(save: StrOrBytesPath, /) -> Mapping[EditorPage, Sequence[SaveSlot]]:
    return {
        page: tuple(SaveSlot(save, page, i) for i in range(1, 21))
        for page in EditorPage
    }
