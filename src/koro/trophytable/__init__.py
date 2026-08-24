from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping
from datetime import timedelta
from typing import Any, Literal

from .. import StageID

__all__ = ["TrophyRow", "TrophyTable"]


class TrophyRow:
    __slots__ = ("_bronze", "_gold", "_platinum", "_silver")
    __match_args__ = ("platinum", "gold", "silver", "bronze")

    _bronze: timedelta
    _gold: timedelta
    _platinum: timedelta
    _silver: timedelta

    def __init__(
        self,
        platinum: timedelta,
        gold: timedelta,
        silver: timedelta,
        bronze: timedelta,
        /,
    ) -> None:
        if not platinum <= gold <= silver <= bronze:
            raise ValueError("TrophyRow times must be ascending")
        elif platinum < timedelta():
            raise ValueError("TrophyRow does not support negative times")
        elif bronze > timedelta(minutes=99, seconds=59, milliseconds=990):
            raise ValueError(
                f"TrophyRow does not support times longer than {timedelta(minutes=99, seconds=59, milliseconds=990)}"
            )
        self._bronze = bronze
        self._gold = gold
        self._platinum = platinum
        self._silver = silver

    @property
    def bronze(self) -> timedelta:
        return self._bronze

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TrophyRow):
            return NotImplemented
        return (
            self.platinum == other.platinum
            and self.gold == other.gold
            and self.silver == other.silver
            and self.bronze == other.bronze
        )

    @property
    def gold(self) -> timedelta:
        return self._gold

    def __hash__(self) -> int:
        return hash((self.platinum, self.gold, self.silver, self.bronze))

    def __iter__(self) -> Iterator[timedelta]:
        yield self.platinum
        yield self.gold
        yield self.silver
        yield self.bronze

    def __len__(self) -> Literal[4]:
        return 4

    @property
    def platinum(self) -> timedelta:
        return self._platinum

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.platinum!r}, {self.gold!r}, {self.silver!r}, {self.bronze!r})"

    @property
    def silver(self) -> timedelta:
        return self._silver


class TrophyTable(ABC):
    __slots__ = ()

    @abstractmethod
    def load(self) -> Mapping[StageID, TrophyRow]:
        pass

    @abstractmethod
    def save(self, data: Mapping[StageID, TrophyRow], /) -> None:
        pass
