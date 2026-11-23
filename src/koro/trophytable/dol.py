from collections.abc import Mapping, MutableMapping, Sequence
from datetime import timedelta
from itertools import chain, product
from pathlib import Path
from struct import iter_unpack, pack_into
from typing import TYPE_CHECKING, Any, Final

from .. import StageID
from . import TrophyRow, TrophyTable

if TYPE_CHECKING:
    from _typeshed import StrPath
else:
    StrPath = Any


__all__ = ["DolTrophyTable"]


class DolTrophyTable(TrophyTable):
    main_segment: Final[Sequence[StageID]] = tuple(
        chain(
            (
                StageID(region, number, StageID.Difficulty.NORMAL)
                for region, number in chain(
                    product(
                        (
                            StageID.Region.THE_EMPTY_LOT,
                            StageID.Region.NEIGHBORS_HOUSE,
                            StageID.Region.SIZZLIN_DESERT,
                            StageID.Region.CHILL_MOUNTAIN,
                            StageID.Region.OCEAN_TREASURE,
                            StageID.Region.SPACE_STATION,
                        ),
                        range(1, 12),
                    ),
                    ((StageID.Region.STUMP_TEMPLE, number) for number in range(1, 11)),
                )
            ),
            (
                StageID(region, number)
                for region, number in product(
                    (
                        StageID.Region.CANDY_ISLAND,
                        StageID.Region.HAUNTED_HOUSE,
                        StageID.Region.HAUNTED_HOUSE_DARKNESS,
                        StageID.Region.CITY,
                        StageID.Region.NIGHT_CITY,
                    ),
                    range(1, 11),
                )
            ),
            (
                StageID(region, number, difficulty)
                for difficulty, (region, number) in product(
                    (StageID.Difficulty.EASY, StageID.Difficulty.HARD),
                    chain(
                        product(
                            (
                                StageID.Region.THE_EMPTY_LOT,
                                StageID.Region.NEIGHBORS_HOUSE,
                                StageID.Region.SIZZLIN_DESERT,
                                StageID.Region.CHILL_MOUNTAIN,
                                StageID.Region.OCEAN_TREASURE,
                                StageID.Region.SPACE_STATION,
                            ),
                            range(1, 12),
                        ),
                        (
                            (StageID.Region.STUMP_TEMPLE, number)
                            for number in range(1, 11)
                        ),
                    ),
                )
            ),
            (StageID(StageID.Region.CANDY_ISLAND_2, number) for number in range(1, 11)),
        )
    )
    survival_segment: Final[Sequence[StageID]] = tuple(
        StageID(StageID.Region.SURVIVAL, number, difficulty)
        for difficulty, number in product(
            (
                StageID.Difficulty.NORMAL,
                StageID.Difficulty.EASY,
                StageID.Difficulty.HARD,
            ),
            range(1, 9),
        )
    )
    pal_addresses: Final[Mapping[int, Sequence[StageID]]] = {
        0x3EB9C8: main_segment,
        0x3EF968: survival_segment,
        0x3F1AA8: tuple(
            StageID(StageID.Region.WII_BALANCE_BOARD, number)
            for number in range(1, 101)
        ),
    }
    ntsc_addresses: Final[Mapping[int, Sequence[StageID]]] = {
        0x3EB728: main_segment,
        0x3EF6C8: survival_segment,
        0x3F1808: tuple(
            StageID(StageID.Region.WII_BALANCE_BOARD, number) for number in range(1, 31)
        ),
    }

    __match_args__ = ("path",)
    __slots__ = ("_path",)

    _path: Path

    def __init__(self, path: StrPath, /) -> None:
        self._path = Path(path).resolve(True)
        if not self.path.is_file():
            raise IsADirectoryError()

    @classmethod
    def deserialize(cls, data: bytes, /) -> Mapping[StageID, TrophyRow]:
        addresses: Mapping[int, Sequence[StageID]]
        match len(data):
            case 4664896:
                addresses = cls.pal_addresses
            case 4643840:
                addresses = cls.ntsc_addresses
            case _:
                ValueError("Could not recognize DOL region.")
        ret: MutableMapping[StageID, TrophyRow] = {}
        for address, rows in addresses.items():
            ret.update(
                {
                    stage_id: TrophyRow(
                        *(timedelta(milliseconds=time) for time in reversed(data))
                    )
                    for stage_id, data in zip(
                        rows,
                        iter_unpack(">IIII", data[address : address + len(rows) * 16]),
                        strict=True,
                    )
                }
            )
        return ret

    def __eq__(self, other: object, /) -> bool:
        if isinstance(other, DolTrophyTable):
            return self.path == other.path
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.path)

    def load(self) -> Mapping[StageID, TrophyRow]:
        addresses: Mapping[int, Sequence[StageID]]
        match self.path.stat().st_size:
            case 4664896:
                addresses = self.pal_addresses
            case 4643840:
                addresses = self.ntsc_addresses
            case _:
                ValueError("Could not recognize DOL region.")
        with open(self.path, "rb") as f:
            ret: MutableMapping[StageID, TrophyRow] = {}
            for address, rows in addresses.items():
                f.seek(address)
                ret.update(
                    {
                        stage_id: TrophyRow(
                            *(timedelta(milliseconds=time) for time in reversed(data))
                        )
                        for stage_id, data in zip(
                            rows,
                            iter_unpack(">IIII", f.read(len(rows) * 16)),
                            strict=True,
                        )
                    }
                )
            return ret

    @property
    def path(self) -> Path:
        return self._path

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.path!r})"

    def save(self, data: Mapping[StageID, TrophyRow], /) -> None:
        addresses: Mapping[int, Sequence[StageID]]
        match self.path.stat().st_size:
            case 4664896:
                addresses = self.pal_addresses
            case 4643840:
                addresses = self.ntsc_addresses
            case _:
                ValueError("Could not recognize DOL region.")
        with open(self.path, "r+b") as f:
            for address, rows in addresses.items():
                segment: bytearray
                if data.keys() >= frozenset(rows):
                    segment = bytearray(len(rows) * 16)
                else:
                    f.seek(address)
                    segment = bytearray(f.read(len(rows) * 16))
                for i, row in enumerate(rows):
                    content: TrophyRow
                    try:
                        content = data[row]
                    except KeyError:
                        continue
                    pack_into(
                        ">IIII",
                        segment,
                        i * 16,
                        *(
                            time // timedelta(milliseconds=1)
                            for time in reversed(content)
                        ),
                    )
                f.seek(address)
                f.write(segment)
