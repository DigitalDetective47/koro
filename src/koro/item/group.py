from abc import ABC
from collections.abc import Iterable, Sequence
from itertools import filterfalse
from typing import Final, Generic, Optional, TypeVar

from .level import Level, LevelNotFoundError

_L = TypeVar("_L", bound=Level)


class Group(ABC, Generic[_L], Sequence[_L]):
    """A group of 20 levels.
    Note that levels are 0-indexed within this interface, but 1-indexed in-game.
    """

    __slots__ = ()

    def fill_mask(self) -> Sequence[bool]:
        """Return which level IDs within this set exist."""
        return [bool(l) for l in self]

    def __len__(self) -> int:
        return 20

    def read(self) -> Iterable[Optional[bytes]]:
        """Read all of the levels within this Group. Empty slots yield None."""
        content: Optional[bytes]
        result: Final[list[Optional[bytes]]] = []
        for level in self:
            try:
                content = level.read()
            except LevelNotFoundError:
                content = None
            result.append(content)
        return result

    def write(self, new_content: Iterable[Optional[bytes]], /) -> None:
        """Replace the contents of this Group with the specified new content. None values will empty the slot they correspond to."""
        for src, dest in filterfalse(
            lambda x: x[0] is None, zip(new_content, self, strict=True)
        ):
            dest.write(src)
