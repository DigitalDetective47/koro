from enum import Enum, auto, unique
from operator import index
from typing import Any, Final, Optional, SupportsIndex

__all__ = [
    "Ant",
    "BasePart",
    "BinSlot",
    "BlinkingTile",
    "Bumper",
    "Cannon",
    "ConveyorBelt",
    "DashTunnel",
    "DecorationModel",
    "DeviceModel",
    "Drawbridge",
    "EditUser",
    "EditorPage",
    "Fan",
    "FileSlot",
    "FileTrophyTable",
    "FixedSpeedDevice",
    "Gear",
    "Goal",
    "GreenCrystal",
    "KororinCapsule",
    "Magnet",
    "MagnetSegment",
    "MagnifyingGlass",
    "MelodyTile",
    "Model",
    "MovingCurve",
    "MovingTile",
    "Part",
    "PartModel",
    "Press",
    "ProgressMarker",
    "Punch",
    "SaveSlot",
    "Scissors",
    "SeesawBlock",
    "SizeTunnel",
    "SlidingTile",
    "Slot",
    "Spring",
    "Stage",
    "Start",
    "Theme",
    "Thorn",
    "TimedDevice",
    "ToyTrain",
    "TrainTrack",
    "TrophyRow",
    "TrophyTable",
    "Turntable",
    "UpsideDownBall",
    "UpsideDownStageDevice",
    "Walls",
    "Warp",
    "XmlSlot",
]


class StageID:
    @unique
    class Difficulty(Enum):
        EASY = auto()
        NORMAL = auto()
        HARD = auto()

    @unique
    class Region(Enum):
        THE_EMPTY_LOT = auto()
        NEIGHBORS_HOUSE = auto()
        SIZZLIN_DESERT = auto()
        CHILL_MOUNTAIN = auto()
        OCEAN_TREASURE = auto()
        SPACE_STATION = auto()
        STUMP_TEMPLE = auto()
        CANDY_ISLAND = auto()
        CANDY_ISLAND_2 = auto()
        HAUNTED_HOUSE = auto()
        HAUNTED_HOUSE_DARKNESS = auto()
        CITY = auto()
        NIGHT_CITY = auto()
        TUTORIAL = auto()
        WII_BALANCE_BOARD = auto()
        RANKING_STAGE = auto()
        HUDSON = auto()
        SURVIVAL = auto()

        @property
        def num_stages(self) -> int:
            return {
                type(self).THE_EMPTY_LOT: 11,
                type(self).NEIGHBORS_HOUSE: 11,
                type(self).SIZZLIN_DESERT: 11,
                type(self).CHILL_MOUNTAIN: 11,
                type(self).OCEAN_TREASURE: 11,
                type(self).SPACE_STATION: 11,
                type(self).STUMP_TEMPLE: 10,
                type(self).CANDY_ISLAND: 10,
                type(self).CANDY_ISLAND_2: 10,
                type(self).HAUNTED_HOUSE: 10,
                type(self).HAUNTED_HOUSE_DARKNESS: 10,
                type(self).CITY: 10,
                type(self).NIGHT_CITY: 10,
                type(self).TUTORIAL: 10,
                type(self).WII_BALANCE_BOARD: 100,
                type(self).RANKING_STAGE: 10,
                type(self).HUDSON: 20,
                type(self).SURVIVAL: 8,
            }[self]

    __slots__ = ("_difficulty", "_number", "_region")
    __match_args__ = ("region", "number", "difficulty")

    _difficulty: Optional[Difficulty]
    _number: int
    _region: Region

    def __init__(
        self,
        region: Region,
        number: SupportsIndex,
        difficulty: Optional[Difficulty] = None,
        /,
    ) -> None:
        difficulty_expected: Final[bool] = region in {
            self.Region.THE_EMPTY_LOT,
            self.Region.NEIGHBORS_HOUSE,
            self.Region.SIZZLIN_DESERT,
            self.Region.CHILL_MOUNTAIN,
            self.Region.OCEAN_TREASURE,
            self.Region.SPACE_STATION,
            self.Region.STUMP_TEMPLE,
            self.Region.SURVIVAL,
        }
        if difficulty_expected and difficulty is None:
            raise ValueError(f"{region} requires a difficulty")
        elif not difficulty_expected and difficulty is not None:
            raise ValueError(f"{region} does not support difficulties")
        number = index(number)
        if number <= 0:
            raise ValueError(f"stage number must be positive")
        elif number > region.num_stages:
            raise ValueError(
                f"{region} has only {region.num_stages} stages (stage {number} specified)"
            )
        self._difficulty = difficulty
        self._number = number
        self._region = region

    @property
    def difficulty(self) -> Optional[Difficulty]:
        return self._difficulty

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StageID):
            return NotImplemented
        return (
            self.region is other.region
            and self.number == other.number
            and self.difficulty is other.difficulty
        )

    def __hash__(self) -> int:
        return hash((self.region, self.number, self.difficulty))

    @property
    def number(self) -> int:
        return self._number

    @property
    def region(self) -> Region:
        return self._region

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.region!r}, {self.number!r}, {self.difficulty!r})"

    def __str__(self) -> str:
        difficulty_string: Final[str] = {
            self.Difficulty.EASY: " (Easy)",
            self.Difficulty.NORMAL: " (Normal)",
            self.Difficulty.HARD: " (Hard)",
            None: "",
        }[self.difficulty]
        region_name: str
        if self.region is self.Region.SURVIVAL:
            region_name = (
                "The Empty Lot",
                "Neighbor's House",
                "Sizzlin' Desert",
                "Chill Mountain",
                "Ocean Treasure",
                "Space Station",
                "Stump Temple",
                "All",
            )[self.number]
            return f"Survival: {region_name}{difficulty_string}"
        else:
            region_name = {
                self.Region.THE_EMPTY_LOT: "The Empty Lot",
                self.Region.NEIGHBORS_HOUSE: "Neighbor's House",
                self.Region.SIZZLIN_DESERT: "Sizzlin' Desert",
                self.Region.CHILL_MOUNTAIN: "Chill Mountain",
                self.Region.OCEAN_TREASURE: "Ocean Treasure",
                self.Region.SPACE_STATION: "Space Station",
                self.Region.STUMP_TEMPLE: "Stump Temple",
                self.Region.CANDY_ISLAND: "Candy Island",
                self.Region.CANDY_ISLAND_2: "Candy Island 2",
                self.Region.HAUNTED_HOUSE: "Haunted House",
                self.Region.HAUNTED_HOUSE_DARKNESS: "Haunted House Darkness",
                self.Region.CITY: "City",
                self.Region.NIGHT_CITY: "Night City",
                self.Region.TUTORIAL: "Tutorial",
                self.Region.WII_BALANCE_BOARD: "Wii Balance Board",
                self.Region.RANKING_STAGE: "Ranking Stage",
                self.Region.HUDSON: "Hudson",
            }[self.region]
            return f"{region_name} {self.number:02}{difficulty_string}"


from .slot import *
from .slot.bin import *
from .slot.file import *
from .slot.save import *
from .slot.xml import *
from .stage import *
from .stage.model import *
from .stage.part import *
from .trophytable import *
from .trophytable.file import *
