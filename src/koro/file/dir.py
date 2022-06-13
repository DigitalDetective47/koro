from collections.abc import Sequence
from operator import index
from os import SEEK_CUR
from os.path import abspath, dirname, isfile, join
from typing import Final, Optional, SupportsIndex, TypeGuard, overload

from ..item.group import Group
from ..item.level import Level, LevelNotFoundError
from ..item.save import Page, Save

from . import Location

_BLOCK_SIZE: Final[int] = 2048
_EMPTY_BLOCK: Final[bytes] = b"\x00" * _BLOCK_SIZE
_LEVEL_ALLOCATION_SIZE: Final[int] = 156864


class DirLevel(Level):
    __match_args__ = ("path", "page", "id")
    __slots__ = ("_offset", "_path")

    _offset: int
    _path: str

    def __init__(self, path: str, /, page: Page, id: SupportsIndex) -> None:
        i = index(id)
        if 0 <= i < 20:
            self._offset = 8 + _LEVEL_ALLOCATION_SIZE * (i & 3)
            self._path = join(abspath(path), f"ed0{(id >> 2) + 5 * page.value}.dat")
        else:
            raise ValueError(id)

    def __bool__(self) -> bool:
        with open(self._path, "rb") as f:
            f.seek(self._offset)
            return f.read(1) != b"\x00"

    def delete(self) -> None:
        with open(self._path, "rb") as f:
            f.seek(self._offset)
            more: bool = f.read(1) != b"\x00"
            if more:
                while more:
                    f.seek(-1, SEEK_CUR)
                    f.write(_EMPTY_BLOCK)
                    more = f.read(1) != b"\x00"
            else:
                raise LevelNotFoundError

    def __eq__(self, other: object, /) -> bool:
        return (
            self._offset == other._offset and self._path == other._path
            if isinstance(other, DirLevel)
            else NotImplemented
        )

    def __hash__(self) -> int:
        return hash((self._offset, self._path))

    @property
    def id(self) -> int:
        return int(self._path[-5]) % 5 << 2 | self._offset // _LEVEL_ALLOCATION_SIZE

    def __len__(self) -> int:
        with open(self._path, "rb") as f:
            f.seek(self._offset)
            block: Final[bytearray] = bytearray(f.read(_BLOCK_SIZE))
            block_offset: int = 0
            while block[-1]:
                f.readinto(block)
                block_offset += _BLOCK_SIZE
            hi: int = _BLOCK_SIZE - 1
            lo: int = 0
            test: int
            while hi != lo:
                test = (hi - lo >> 1) + lo
                if block[test]:
                    lo = test + 1
                else:
                    hi = test
            return block_offset + hi

    @property
    def page(self) -> Page:
        return Page(ord(self._path[-5]) > 52)

    @property
    def path(self) -> str:
        return dirname(self._path)

    def read(self) -> bytes:
        with open(self._path, "rb") as f:
            f.seek(self._offset)
            block: Final[bytearray] = bytearray(f.read(_BLOCK_SIZE))
            if block[0]:
                result: Final[bytearray] = bytearray()
                while block[-1]:
                    result.extend(block)
                    f.readinto(block)
                hi: int = _BLOCK_SIZE - 1
                lo: int = 0
                test: int
                while hi != lo:
                    test = (hi - lo >> 1) + lo
                    if block[test]:
                        lo = test + 1
                    else:
                        hi = test
                return bytes(result + block[:hi])
            else:
                raise LevelNotFoundError

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.path!r}, {self.page!r}, {self.id!r})"

    def write(self, new_content: bytes, /) -> None:
        with open(self._path, "r+b") as f:
            f.seek(self._offset)
            f.write(new_content)
            while f.read(1) != b"\x00":
                f.seek(-1, SEEK_CUR)
                f.write(_EMPTY_BLOCK)


class DirGroup(Group[DirLevel]):
    __match_args__ = ("path", "page")
    __slots__ = ("_page", "_path")

    _page: Page
    _path: str

    def __init__(self, path: str, /, page: Page) -> None:
        self._page = page
        self._path = abspath(path)

    def __contains__(self, value: object, /) -> TypeGuard[DirLevel]:
        return (
            isinstance(value, DirLevel)
            and value.path == self.path
            and value.page is self.page
        )

    def count(self, value: object) -> int:
        return int(value in self)

    def __eq__(self, other: object, /) -> bool:
        return (
            self.page == other.page and self.path == other.path
            if isinstance(other, DirGroup)
            else NotImplemented
        )

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> DirLevel:
        pass

    @overload
    def __getitem__(self, indices: slice, /) -> Sequence[DirLevel]:
        pass

    def __getitem__(
        self, key: SupportsIndex | slice, /
    ) -> DirLevel | Sequence[DirLevel]:
        if isinstance(key, slice):
            return tuple((self[i] for i in range(*key.indices(20))))
        else:
            i: int = index(key)
            if -20 <= i < 20:
                return DirLevel(self.path, self.page, i % 20)
            else:
                raise IndexError(key)

    def __hash__(self) -> int:
        return hash((self.path, self.page))

    def index(self, value: object, start: int = 0, stop: Optional[int] = None) -> int:
        if value in self and value.id in range(*slice(start, stop).indices(20)):
            return value.id
        else:
            raise ValueError

    @property
    def page(self) -> Page:
        return self._page

    @property
    def path(self) -> str:
        return self._path

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.path!r}, {self.page!r})"


class DirSave(Location, Save[DirGroup]):
    __slots__ = ()

    def __bool__(self) -> bool:
        return all((isfile(join(self.path, f"ed0{i}.dat")) for i in range(10)))

    def __getitem__(self, key: Page, /) -> DirGroup:
        if isinstance(key, Page):
            return DirGroup(self.path, key)
        else:
            raise KeyError(key)
