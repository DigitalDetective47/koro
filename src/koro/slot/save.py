from collections.abc import Mapping
from io import BytesIO
from os.path import basename, dirname, join
from re import Match, fullmatch
from typing import TYPE_CHECKING, Any, Final, Literal, Optional
from warnings import warn

from .. import StageID
from ..stage import Stage
from . import Slot
from .xml import XmlSlot

if TYPE_CHECKING:
    from _typeshed import StrOrBytesPath
else:
    StrOrBytesPath = Any


__all__ = ["SaveSlot"]

_REGION_OFFSETS: Final[Mapping[StageID.Region, int]] = {
    StageID.Region.ORIGINAL: 0,
    StageID.Region.FRIEND: 20,
    StageID.Region.HUDSON: 40,
}
_SIZE_LIMIT: Final[int] = 156864


class SaveSlot(Slot):
    __match_args__ = ("path", "page", "stage_id")
    __slots__ = ("_offset", "_path")

    _offset: Literal[8, 156872, 313736, 470600]
    _path: str | bytes

    def __init__(self, path: StrOrBytesPath, stage_id: StageID) -> None:
        if stage_id.region not in _REGION_OFFSETS.keys():
            raise ValueError(
                "SaveSlots only support regions ORIGINAL, FRIEND, and HUDSON."
            )
        if stage_id.region is stage_id.Region.HUDSON and stage_id.number <= 5:
            warn(
                "Modifications to Hudson 01-05 are ignored by the game. These stages are read from disc (/data/A19S00X.bin) and are empty by default when inspected with this library; writes made by this library will have no effect in-game.",
                RuntimeWarning,
            )
        self._offset = 8 + _SIZE_LIMIT * ((stage_id.number - 1) & 3)  # type: ignore[assignment]
        self._path = join(path, f"ed{((stage_id.number - 1) >> 2) + _REGION_OFFSETS[stage_id.region]:02}.dat")  # type: ignore[arg-type]

    def __bool__(self) -> bool:
        try:
            with open(self._path, "rb") as f:
                f.seek(self._offset)
                return f.read(1) != b"\x00"
        except FileNotFoundError:
            return False

    def __eq__(self, other: Any, /) -> bool:
        if isinstance(other, SaveSlot):
            return self._path == other._path and self._offset == other._offset
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash((self._offset, self._path))

    def load(self) -> Stage | None:
        try:
            with open(self._path, "rb") as f:
                f.seek(self._offset)
                with BytesIO() as b:
                    block: bytearray = bytearray()
                    while True:
                        block.clear()
                        block.extend(f.read1(_SIZE_LIMIT - len(b.getbuffer())))
                        if block and block[-1]:
                            b.write(block)
                        else:
                            while block:
                                if block[len(block) >> 1]:
                                    b.write(block[: (len(block) >> 1) + 1])
                                    del block[: (len(block) >> 1) + 1]
                                else:
                                    del block[len(block) >> 1 :]
                            data: bytes = b.getvalue()
                            if data:
                                return XmlSlot.deserialize(data)
                            else:
                                return None
        except FileNotFoundError:
            return None

    @property
    def path(self) -> StrOrBytesPath:
        return dirname(self._path)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.path!r}, {self.stage_id!r})"

    def save(self, data: Stage | None, /) -> None:
        binary: bytes = b"" if data is None else XmlSlot.serialize(data)
        if len(binary) > _SIZE_LIMIT:
            raise ValueError("serialized stage data is too large to save")
        try:
            with open(self._path, "xb") as f:
                f.write(
                    bytes(638976)
                )  # Weird. Would expect this to be 627464 (8 + 4 * (_SIZE_LIMIT))
            if data is None:
                return
        except FileExistsError:
            pass
        with open(self._path, "r+b") as f:
            f.seek(self._offset)
            f.write(binary)
            f.write(bytes(_SIZE_LIMIT - len(binary)))

    @property
    def stage_id(self) -> StageID:
        path: str
        if isinstance(self._path, str):
            path = self._path
        else:
            path = self._path.decode(errors="ignore")
        m: Final[Optional[Match]] = fullmatch(r"ed(\d{2})\.dat", basename(path))
        if m is None:
            raise ValueError(
                "Final path component somehow doesn't end in an editor data filename."
            )
        region_id: int
        file_id: int
        region_id, file_id = divmod(int(m.group(1)), 5)
        return StageID(
            tuple(_REGION_OFFSETS.keys())[region_id],
            file_id << 2 | self._offset // _SIZE_LIMIT + 1,
        )
