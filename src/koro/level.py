from abc import ABC, abstractmethod
from collections.abc import Sized
from enum import Enum, unique

__all__ = ["Level", "LevelNotFoundError", "LevelStatistics", "Theme"]


@unique
class Theme(Enum):
    THE_EMPTY_LOT = 0
    NEIGHBORS_HOUSE = 1
    SIZZLIN_DESERT = 2
    CHILL_MOUNTAIN = 3
    OCEAN_TREASURE = 4
    SPACE_STATION = 5
    STUMP_TEMPLE = 6
    CANDY_ISLAND = 7
    HAUNTED_HOUSE = 8
    CITY = 9
    NIGHT_CITY = 10
    TUTORIAL = 11
    HAUNTED_HOUSE_DARKNESS = 12

    def __str__(self) -> str:
        return (
            "The Empty Lot",
            "Neighbor's House",
            "Sizzlin' Desert",
            "Chill Mountain",
            "Ocean Treasure",
            "Space Station",
            "Stump Temple",
            "Candy Island",
            "Haunted House",
            "City",
            "Night City",
            "Tutorial",
            "Haunted House Darkness",
        )[self.value]


class LevelNotFoundError(LookupError):
    pass


class Level(ABC, Sized):
    __slots__ = ()

    @abstractmethod
    def __bool__(self) -> bool:
        """Return whether this level exists."""

    @abstractmethod
    def delete(self) -> None:
        """Delete this level if it exists, otherwise raise LevelNotFoundError."""
        pass

    def __len__(self) -> int:
        """The file size of this level."""
        return len(self.read())

    @abstractmethod
    def read(self) -> bytes:
        """Return the contents of this level if it exists, otherwise raise LevelNotFoundError."""
        pass

    @abstractmethod
    def write(self, new_content: bytes, /) -> None:
        """Replace the contents of this level, or create it if it doesn't exist."""
        pass
