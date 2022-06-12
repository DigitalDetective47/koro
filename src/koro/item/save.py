from abc import ABC
from collections.abc import Iterator, Mapping
from enum import Enum, unique
from typing import Generic, TypeGuard, TypeVar

from item.group import Group

_G = TypeVar("_G", bound=Group)


@unique
class Page(Enum):
    ORIGINAL = 0
    FRIEND = 1


class Save(ABC, Generic[_G], Mapping[Page, _G]):
    __slots__ = ()

    def __contains__(self, key: object, /) -> TypeGuard[Page]:
        return isinstance(key, Page)

    def __iter__(self) -> Iterator[Page]:
        return iter(Page)

    def __len__(self) -> int:
        return 2
