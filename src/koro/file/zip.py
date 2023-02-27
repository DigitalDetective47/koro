from collections.abc import Iterable, Sequence
from itertools import filterfalse
from operator import index
from os.path import abspath
from re import fullmatch
from typing import Final, Optional, SupportsIndex, TypeGuard, overload
from zipfile import ZipFile, ZipInfo

from ..item.group import Group
from ..item.level import Level, LevelNotFoundError

from . import Location

__all__ = ["ZipGroup", "ZipLevel"]


def _id_to_fn(id: SupportsIndex, /) -> str:
    return f"{str(index(id) + 1).zfill(2)}.lvl"


class ZipLevelNotFoundError(KeyError, LevelNotFoundError):
    pass


class ZipLevel(Level):
    __match_args__ = ("path", "id")
    __slots__ = ("_id", "_path")

    _id: int
    _path: str

    def __init__(self, path: str, /, id: SupportsIndex) -> None:
        i: int = index(id)
        if 0 <= i < 20:
            self._id = i
            self._path = abspath(path)
        else:
            raise ValueError(id)

    def __bool__(self) -> bool:
        with ZipFile(self.path) as a:
            return self.fn in a.namelist()

    def delete(self) -> None:
        with ZipFile(self.path) as a:
            if self.fn not in a.namelist():
                raise ZipLevelNotFoundError
            contents: Final[dict[ZipInfo, bytes]] = {}
            for info in filterfalse(
                lambda info: info.filename == self.fn, a.infolist()
            ):
                contents[info] = a.read(info)
        with ZipFile(self.path, "w") as a:
            for x in contents.items():
                a.writestr(*x)

    def __eq__(self, other: object, /) -> bool:
        return (
            self.path == other.path and self.id == other.id
            if isinstance(other, ZipLevel)
            else NotImplemented
        )

    def __hash__(self) -> int:
        return hash((self.path, self.id))

    @property
    def fn(self) -> str:
        return _id_to_fn(self.id)

    @property
    def id(self) -> int:
        return self._id

    def __len__(self) -> int:
        try:
            with ZipFile(self.path) as a:
                return a.getinfo(self.fn).file_size
        except KeyError as e:
            raise ZipLevelNotFoundError(*e.args)

    @property
    def path(self) -> str:
        return self._path

    def read(self) -> bytes:
        try:
            with ZipFile(self.path) as a:
                return a.read(self.fn)
        except KeyError as e:
            raise ZipLevelNotFoundError(*e.args)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.path!r}, {self.id!r})"

    def write(self, new_content: bytes, /) -> None:
        contents: Final[dict[ZipInfo, bytes]] = {}
        with ZipFile(self.path, "a") as a:
            for info in filterfalse(
                lambda info: info.filename == self.fn, a.infolist()
            ):
                contents[info] = a.read(info)
        with ZipFile(self.path, "w") as a:
            for x in contents.items():
                a.writestr(*x)
            a.writestr(self.fn, new_content)


class ZipGroup(Group[ZipLevel], Location):
    __slots__ = ()

    def __contains__(self, value: object, /) -> TypeGuard[ZipLevel]:
        return isinstance(value, ZipLevel) and value.path == self.path

    def count(self, value: object) -> int:
        return int(value in self)

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> ZipLevel:
        pass

    @overload
    def __getitem__(self, indices: slice, /) -> Sequence[ZipLevel]:
        pass

    def __getitem__(
        self, key: SupportsIndex | slice, /
    ) -> ZipLevel | Sequence[ZipLevel]:
        if isinstance(key, slice):
            return tuple((self[i] for i in range(*key.indices(20))))
        elif -20 <= index(key) < 20:
            return ZipLevel(self.path, index(key) % 20)
        else:
            raise IndexError(key)

    def index(self, value: object, start: int = 0, stop: Optional[int] = None) -> int:
        if value in self and value.id in range(*slice(start, stop).indices(20)):
            return value.id
        else:
            raise ValueError

    def init(self) -> None:
        with ZipFile(self.path, "x") as a:
            pass

    def fill_mask(self) -> Sequence[bool]:
        with ZipFile(self.path) as a:
            return [_id_to_fn(i) in a.namelist() for i in range(20)]

    def read(self) -> Iterable[Optional[bytes]]:
        with ZipFile(self.path) as a:
            name_list: Final[list[str]] = a.namelist()
            return [
                a.read(fn) if fn in name_list else None
                for fn in map(_id_to_fn, range(20))
            ]

    def write(self, new_content: Iterable[Optional[bytes]], /) -> None:
        contents: Final[dict[ZipInfo, bytes]] = {}
        if self:
            with ZipFile(self.path) as a:
                for info in filterfalse(
                    lambda info: fullmatch(r"(0[1-9]|1\d|20)\.lvl", info.filename),
                    a.infolist(),
                ):
                    contents[info] = a.read(info)
        with ZipFile(self.path, "w") as a:
            for x in contents.items():
                a.writestr(*x)
            for id, content in filterfalse(
                lambda x: x[1] is None, enumerate(new_content)
            ):
                a.writestr(_id_to_fn(id), content)
