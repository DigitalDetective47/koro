from collections.abc import Iterable
from enum import Enum, unique

from .part import BasePart

__all__ = ["EditUser", "Level", "Theme"]


@unique
class EditUser(Enum):
    BEGINNER = 0
    INTERMEDIATE = 1
    EXPERT = 2
    PROTECTED = 3
    """A level with this edit user can only be opened in expert, and will open a blank level when doing so."""


@unique
class Theme(Enum):
    HAUNTED_HOUSE_DARKNESS = 12
    NIGHT_CITY = 10
    THE_EMPTY_LOT = 0
    NEIGHBORS_HOUSE = 1
    SIZZLIN_DESERT = 2
    CHILL_MOUNTAIN = 3
    OCEAN_TREASURE = 4
    SPACE_STATION = 5
    STUMP_TEMPLE = 6
    TUTORIAL = 11
    CANDY_ISLAND = 7
    HAUNTED_HOUSE = 8
    CITY = 9

    def decorations_available(self) -> int:
        return {
            Theme.HAUNTED_HOUSE_DARKNESS: 8,
            Theme.NIGHT_CITY: 7,
            Theme.THE_EMPTY_LOT: 10,
            Theme.NEIGHBORS_HOUSE: 5,
            Theme.SIZZLIN_DESERT: 8,
            Theme.CHILL_MOUNTAIN: 9,
            Theme.OCEAN_TREASURE: 9,
            Theme.SPACE_STATION: 7,
            Theme.STUMP_TEMPLE: 6,
            Theme.TUTORIAL: 12,
            Theme.CANDY_ISLAND: 4,
            Theme.HAUNTED_HOUSE: 8,
            Theme.CITY: 7,
        }[self]


class Level(set[BasePart]):
    __slots__ = ("_edit_user", "_theme", "_tilt_lock")

    _edit_user: EditUser
    _theme: Theme
    _tilt_lock: bool

    def __init__(
        self,
        iterable: Iterable[BasePart] = (),
        /,
        *,
        edit_user: EditUser = EditUser.EXPERT,
        theme: Theme,
        tilt_lock: bool = False,
    ) -> None:
        super().__init__(iterable)
        self.edit_user = edit_user
        self.theme = theme
        self.tilt_lock = tilt_lock

    @property
    def edit_user(self) -> EditUser:
        return self._edit_user

    @edit_user.setter
    def edit_user(self, value: EditUser, /) -> None:
        self._edit_user = value

    @property
    def theme(self) -> Theme:
        return self._theme

    @theme.setter
    def theme(self, value: Theme, /) -> None:
        self._theme = value

    @property
    def tilt_lock(self) -> bool:
        return self._tilt_lock

    @tilt_lock.setter
    def tilt_lock(self, value: bool, /) -> None:
        self._tilt_lock = value
