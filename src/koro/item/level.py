from abc import ABC, abstractmethod
from collections.abc import Sized
from dataclasses import dataclass
from enum import Enum, unique
from typing import Final


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
    TUTORIAL = 11
    HAUNTED_HOUSE_DARKNESS = 12
    NIGHT_CITY = 13

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
            None,
            "Tutorial",
            "Haunted House Darkness",
            "Night City",
        )[self.value]


@dataclass(frozen=True, match_args=False, kw_only=True, slots=True)
class LevelStatistics:
    crystals: int
    filesize: int
    theme: Theme


class LevelNotFoundError(LookupError):
    pass


class Level(ABC, Sized):
    __slots__ = ()

    def about(self) -> LevelStatistics:
        content: Final[bytes] = self.read()
        return LevelStatistics(
            crystals=content.count(b"<anmtype> 49 </anmtype>"),
            filesize=len(content),
            theme=Theme(int(content[87:89])),
        )

    @abstractmethod
    def __bool__(self) -> bool:
        """Return whether this level exists."""

    @abstractmethod
    def delete(self) -> None:
        """Delete this level if it exists, otherwise raise LevelNotFoundError."""
        pass

    def encode(self) -> bytes:
        """Return a bytes object that when written to a file can overwrite an official level."""
        data: Final[bytearray] = bytearray(self.read())
        header: Final[bytes] = (
            b"\x00\x00\x00\x01\x00\x00\x00\x08"
            + len(data).to_bytes(4, "big")
            + b"\x00\x00\x00\x01"
        )
        i: int = 0
        while i < len(data):
            data.insert(i, 255)
            i += 9
        return header + data + b"\x00"

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
