from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, MutableSequence
from enum import Enum, unique, Flag
from operator import index
from sys import maxsize
from typing import Any, Final, Iterator, Literal, Self, SupportsIndex, overload

from .model import DecorationModel, DeviceModel, PartModel


__all__ = [
    "Ant",
    "BasePart",
    "BlinkingTile",
    "Bumper",
    "Cannon",
    "ConveyorBelt",
    "DashTunnel",
    "Drawbridge",
    "Fan",
    "FixedSpeedDevice",
    "Gear",
    "Goal",
    "GreenCrystal",
    "KororinCapsule",
    "Magnet",
    "MagnetSegment",
    "MagnifyingGlass",
    "MelodyTile",
    "MovingCurve",
    "MovingTile",
    "Part",
    "Press",
    "ProgressMarker",
    "Punch",
    "Scissors",
    "SeesawBlock",
    "SizeTunnel",
    "SlidingTile",
    "Spring",
    "Start",
    "Thorn",
    "TimedDevice",
    "ToyTrain",
    "TrainTrack",
    "Turntable",
    "UpsideDownBall",
    "UpsideDownStageDevice",
    "Walls",
    "Warp",
]


class BasePart(ABC):
    """Base class for all stage elements"""

    __match_args__ = ("x_pos", "y_pos", "z_pos", "x_rot", "y_rot", "z_rot")
    __slots__ = ("_x_pos", "_x_rot", "_y_pos", "_y_rot", "_z_pos", "_z_rot")

    _x_pos: float
    _x_rot: float
    _y_pos: float
    _y_rot: float
    _z_pos: float
    _z_rot: float

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
    ) -> None:
        self.x_pos = x_pos
        self.x_rot = x_rot
        self.y_pos = y_pos
        self.y_rot = y_rot
        self.z_pos = z_pos
        self.z_rot = z_rot

    @property
    @abstractmethod
    def cost(self) -> int:
        """The number of kororin points that this part costs to place."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r})"

    @property
    def x_pos(self) -> float:
        """Positive is right, negative is left"""
        return self._x_pos

    @x_pos.setter
    def x_pos(self, value: float, /) -> None:
        self._x_pos = value

    @property
    def x_rot(self) -> float:
        """Represented in degrees from 0 to 360
        Positive turns top face front, negative turns top face back
        """
        return self._x_rot

    @x_rot.setter
    def x_rot(self, value: float, /) -> None:
        self._x_rot = value % 360

    @property
    def y_pos(self) -> float:
        """Positive is up, negative is down"""
        return self._y_pos

    @y_pos.setter
    def y_pos(self, value: float, /) -> None:
        self._y_pos = value

    @property
    def y_rot(self) -> float:
        """Represented in degrees from 0 to 360
        Positive turns front face right, negative turns front face left
        """
        return self._y_rot

    @y_rot.setter
    def y_rot(self, value: float, /) -> None:
        self._y_rot = value % 360

    @property
    def z_pos(self) -> float:
        """Positive is front, negative is back"""
        return self._z_pos

    @z_pos.setter
    def z_pos(self, value: float, /) -> None:
        self._z_pos = value

    @property
    def z_rot(self) -> float:
        """Represented in degrees from 0 to 360
        Positive turns top face left, negative turns top face right
        """
        return self._z_rot

    @z_rot.setter
    def z_rot(self, value: float, /) -> None:
        self._z_rot = value % 360


class Part(BasePart):
    """(Usually) static model that has no behavior other than being solid."""

    __slots__ = ("_shape",)

    _shape: PartModel | DecorationModel

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        shape: PartModel | DecorationModel,
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.shape = shape

    @property
    def cost(self) -> Literal[10, 15, 20]:
        if isinstance(self.shape, DecorationModel):
            return 20
        elif self.shape in frozenset(
            {
                PartModel.MagmaTile,
                PartModel.SlipperyTile,
                PartModel.StickyTile,
                PartModel.InvisibleTile,
            }
        ):
            return 15
        else:
            return 10

    @property
    def shape(self) -> PartModel | DecorationModel:
        return self._shape

    @shape.setter
    def shape(self, value: PartModel | DecorationModel, /) -> None:
        self._shape = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, shape={self.shape!r})"


class Start(BasePart):
    __slots__ = ()

    @property
    def cost(self) -> Literal[0]:
        return 0


class Goal(BasePart):
    __slots__ = ()

    @property
    def cost(self) -> Literal[0]:
        return 0


class ProgressMarker(BasePart):
    """Either a crystal (when progress is odd) or a respawn (when progress is even)"""

    __slots__ = ("_progress",)

    _progress: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        progress: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.progress = progress

    @property
    def cost(self) -> Literal[15, 0]:
        return 15 if self.progress & 1 else 0

    @property
    def progress(self) -> Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        """The number displayed above the object. Controls which crystals are required to enable a respawn."""
        return self._progress

    @progress.setter
    def progress(self, value: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], /):
        self._progress = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, progress={self.progress!r})"


@unique
class Speed(Enum):
    SLOW = 55
    NORMAL = 39
    FAST = 23


@unique
class Walls(Flag):
    BACK = 8
    FRONT = 2
    LEFT = 4
    RIGHT = 1


class MovingTile(BasePart):
    """A part that moves in a straight line."""

    __slots__ = (
        "_dest_x",
        "_dest_y",
        "_dest_z",
        "_shape",
        "_speed",
        "_switch",
        "_walls",
    )

    _dest_x: float
    _dest_y: float
    _dest_z: float
    _shape: Literal[
        PartModel.Tile10x10,
        PartModel.Tile20x20,
        PartModel.TileA30x30,
        PartModel.TileA30x90,
        PartModel.Tile90x90,
        PartModel.HoleB90x90,
        PartModel.FunnelPipe,
        PartModel.StraightPipe,
    ]
    _speed: float
    _switch: bool
    _walls: Walls

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        dest_x: float,
        dest_y: float,
        dest_z: float,
        shape: Literal[
            PartModel.Tile10x10,
            PartModel.Tile20x20,
            PartModel.TileA30x30,
            PartModel.TileA30x90,
            PartModel.Tile90x90,
            PartModel.HoleB90x90,
            PartModel.FunnelPipe,
            PartModel.StraightPipe,
        ],
        speed: Speed | float = Speed.NORMAL,
        switch: bool = False,
        walls: Walls = Walls(0),
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.dest_z = dest_z
        self._shape = shape
        self.speed = speed  # type: ignore[assignment]
        self.switch = switch
        self.walls = walls

    @property
    def cost(self) -> Literal[20, 70, 35, 40, 50, 65]:
        match self.shape:
            case PartModel.Tile10x10:
                return 20
            case PartModel.Tile20x20 | PartModel.TileA30x30:
                return 70
            case PartModel.TileA30x90:
                return 35
            case PartModel.Tile90x90 | PartModel.HoleB90x90:
                return 40
            case PartModel.FunnelPipe:
                return 50
            case PartModel.StraightPipe:
                return 65

    @property
    def dest_x(self) -> float:
        """Positive is right, negative is left"""
        return self._dest_x

    @dest_x.setter
    def dest_x(self, value: float, /) -> None:
        self._dest_x = value

    @property
    def dest_y(self) -> float:
        return self._dest_y

    @dest_y.setter
    def dest_y(self, value: float, /) -> None:
        """Positive is up, negative is down"""
        self._dest_y = value

    @property
    def dest_z(self) -> float:
        """Positive is front, negative is back"""
        return self._dest_z

    @dest_z.setter
    def dest_z(self, value: float, /) -> None:
        self._dest_z = value

    def __repr__(self) -> str:
        output: Final[list[str]] = [
            f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, dest_x={self.dest_x!r}, dest_y={self.dest_y!r}, dest_z={self.dest_z!r}, shape={self.shape!r}"
        ]
        if self.speed != 1.0:
            output.append(f", speed={self.speed!r}")
        if self.switch:
            output.append(f", switch={self.switch!r}")
        if self.walls:
            output.append(f", walls={self.walls!r}")
        output.append(")")
        return "".join(output)

    @property
    def shape(
        self,
    ) -> Literal[
        PartModel.Tile10x10,
        PartModel.Tile20x20,
        PartModel.TileA30x30,
        PartModel.TileA30x90,
        PartModel.Tile90x90,
        PartModel.HoleB90x90,
        PartModel.FunnelPipe,
        PartModel.StraightPipe,
    ]:
        """The appearance of this moving tile."""
        return self._shape

    @shape.setter
    def shape(
        self,
        value: Literal[
            PartModel.Tile10x10,
            PartModel.Tile20x20,
            PartModel.TileA30x30,
            PartModel.TileA30x90,
            PartModel.Tile90x90,
            PartModel.HoleB90x90,
            PartModel.FunnelPipe,
            PartModel.StraightPipe,
        ],
        /,
    ) -> None:
        if (
            value in frozenset({PartModel.FunnelPipe, PartModel.StraightPipe})
            and self.switch
        ):
            raise ValueError("Moving pipes cannot be switches")
        elif (
            value not in frozenset({PartModel.Tile20x20, PartModel.TileA30x30})
            and self.walls
        ):
            raise ValueError("Invalid shape for wall attachment")
        else:
            self._shape = value

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, value: Speed | float, /) -> None:
        match value:
            case Speed.SLOW:
                self.speed = 0.5
            case Speed.NORMAL:
                self.speed = 1.0
            case Speed.FAST:
                self.speed = 1.5
            case _:
                self._speed = value

    @property
    def switch(self) -> bool:
        """Whether this moving tile must be touched in order to move."""
        return self._switch

    @switch.setter
    def switch(self, value: bool, /) -> None:
        if value and self.shape in frozenset(
            {PartModel.FunnelPipe, PartModel.StraightPipe}
        ):
            raise ValueError("Moving pipes cannot be switches")
        else:
            self._switch = value

    @property
    def walls(self) -> Walls:
        return self._walls

    @walls.setter
    def walls(self, value: Walls, /) -> None:
        if not value or self.shape in frozenset(
            {PartModel.Tile20x20, PartModel.TileA30x30}
        ):
            self._walls = value
        else:
            raise ValueError("Invalid shape for wall attachment")


class FixedSpeedDevice(BasePart, ABC):
    """Device template for devices with speeds that can be set to Slow, Normal, or Fast"""

    __slots__ = ("_speed",)

    _speed: Speed

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        speed: Speed = Speed.NORMAL,
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.speed = speed

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, speed={self.speed!r})"
            if self.speed != Speed.NORMAL
            else f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r})"
        )

    @property
    def speed(self) -> Speed:
        return self._speed

    @speed.setter
    def speed(self, value: Speed, /) -> None:
        self._speed = value


class MovingCurve(FixedSpeedDevice):
    __slots__ = ("_shape",)

    _shape: Literal[PartModel.CurveS, PartModel.CurveM, PartModel.CurveL]

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        shape: Literal[PartModel.CurveS, PartModel.CurveM, PartModel.CurveL],
        speed: Speed = Speed.NORMAL,
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot, speed=speed)
        self.shape = shape

    @property
    def cost(self) -> Literal[25]:
        return 25

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, shape={self.shape!r}, speed={self.speed!r})"
            if self.speed != Speed.NORMAL
            else f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, shape={self.shape!r})"
        )

    @property
    def shape(self) -> Literal[PartModel.CurveS, PartModel.CurveM, PartModel.CurveL]:
        return self._shape

    @shape.setter
    def shape(
        self, value: Literal[PartModel.CurveS, PartModel.CurveM, PartModel.CurveL], /
    ) -> None:
        self._shape = value


class SlidingTile(BasePart):
    __slots__ = ()

    @property
    def cost(self) -> Literal[100]:
        return 100


class ConveyorBelt(BasePart):
    __slots__ = ("_reversing",)

    _reversing: bool

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        reversing: bool = False,
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.reversing = reversing

    @property
    def cost(self) -> Literal[60]:
        return 60

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, reversing={self.reversing!r})"
            if self.reversing
            else super().__repr__()
        )

    @property
    def reversing(self) -> bool:
        return self._reversing

    @reversing.setter
    def reversing(self, value: bool, /) -> None:
        self._reversing = value


class MagnetSegment(BasePart):
    __slots__ = ("_shape",)

    _shape: Literal[
        DeviceModel.EndMagnet,
        DeviceModel.StraightMagnet,
        DeviceModel.CurveMagnetL,
        DeviceModel.CurveMagnetS,
    ]

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        shape: Literal[
            DeviceModel.EndMagnet,
            DeviceModel.StraightMagnet,
            DeviceModel.CurveMagnetL,
            DeviceModel.CurveMagnetS,
        ],
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.shape = shape

    @property
    def cost(self) -> Literal[15]:
        return 15

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, shape={self.shape!r})"

    @property
    def shape(self) -> Literal[
        DeviceModel.EndMagnet,
        DeviceModel.StraightMagnet,
        DeviceModel.CurveMagnetL,
        DeviceModel.CurveMagnetS,
    ]:
        return self._shape

    @shape.setter
    def shape(
        self,
        value: Literal[
            DeviceModel.EndMagnet,
            DeviceModel.StraightMagnet,
            DeviceModel.CurveMagnetL,
            DeviceModel.CurveMagnetS,
        ],
        /,
    ) -> None:
        self._shape = value


class Magnet(BasePart, MutableSequence[MagnetSegment]):
    __slots__ = ("_segments",)

    _segments: list[MagnetSegment]

    def __init__(self, iterable: Iterable[MagnetSegment] = (), /) -> None:
        self._segments = list(iterable)

    def append(self, value: MagnetSegment) -> None:
        return self._segments.append(value)

    def clear(self) -> None:
        self._segments.clear()

    def __contains__(self, value: Any, /) -> bool:
        return value in self._segments

    @property
    def cost(self) -> int:
        return sum(segment.cost for segment in self)

    def count(self, value: Any) -> int:
        return self._segments.count(value)

    def __delitem__(self, index: SupportsIndex | slice, /) -> None:
        del self._segments[index]

    def extend(self, iterable: Iterable[MagnetSegment], /) -> None:
        self._segments.extend(iterable)

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> MagnetSegment:
        pass

    @overload
    def __getitem__(self, index: slice, /) -> MutableSequence[MagnetSegment]:
        pass

    def __getitem__(
        self, index: SupportsIndex | slice, /
    ) -> MagnetSegment | MutableSequence[MagnetSegment]:
        return self._segments[index]

    def __iadd__(self, value: Iterable[MagnetSegment], /) -> Self:
        self._segments += value
        return self

    def index(
        self, value: Any, start: SupportsIndex = 0, stop: SupportsIndex = maxsize, /
    ) -> int:
        return self._segments.index(value, start, stop)

    def insert(self, index: SupportsIndex, value: MagnetSegment, /) -> None:
        return self._segments.insert(index, value)

    def __iter__(self) -> Iterator[MagnetSegment]:
        return iter(self._segments)

    def __len__(self) -> int:
        return len(self._segments)

    def pop(self, index: SupportsIndex = -1, /) -> MagnetSegment:
        return self._segments.pop(index)

    def remove(self, value: MagnetSegment, /) -> None:
        self._segments.remove(value)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._segments!r})"

    def reverse(self) -> None:
        self._segments.reverse()

    def __reversed__(self) -> Iterator[MagnetSegment]:
        return reversed(self._segments)

    @overload
    def __setitem__(self, index: SupportsIndex, value: MagnetSegment, /) -> None:
        pass

    @overload
    def __setitem__(self, slice: slice, value: Iterable[MagnetSegment], /) -> None:
        pass

    def __setitem__(
        self,
        index: SupportsIndex | slice,
        value: MagnetSegment | Iterable[MagnetSegment],
        /,
    ) -> None:
        self._segments[index] = value  # type: ignore

    @property
    def x_pos(self) -> float:
        """Positive is right, negative is left"""
        return self[-1].x_pos

    @x_pos.setter
    def x_pos(self, value: float, /) -> None:
        offset: float = value - self.x_pos
        for segment in self:
            segment.x_pos += offset

    @property
    def x_rot(self) -> float:
        """Represented in degrees from 0 to 360
        Positive turns top face front, negative turns top face back
        """
        return self[-1].x_rot

    @x_rot.setter
    def x_rot(self, value: float, /) -> None:
        """Positions of segments are not updated."""
        offset: float = value - self.x_rot
        for segment in self:
            segment.x_rot += offset

    @property
    def y_pos(self) -> float:
        """Positive is up, negative is down"""
        return self[-1].y_pos

    @y_pos.setter
    def y_pos(self, value: float, /) -> None:
        offset: float = value - self.y_pos
        for segment in self:
            segment.y_pos += offset

    @property
    def y_rot(self) -> float:
        """Represented in degrees from 0 to 360
        Positive turns front face right, negative turns front face left
        """
        return self[-1].y_rot

    @y_rot.setter
    def y_rot(self, value: float, /) -> None:
        """Positions of segments are not updated."""
        offset: float = value - self.y_rot
        for segment in self:
            segment.y_rot += offset

    @property
    def z_pos(self) -> float:
        """Positive is front, negative is back"""
        return self[-1].z_pos

    @z_pos.setter
    def z_pos(self, value: float, /) -> None:
        offset: float = value - self.z_pos
        for segment in self:
            segment.z_pos += offset

    @property
    def z_rot(self) -> float:
        """Represented in degrees from 0 to 360
        Positive turns top face left, negative turns top face right
        """
        return self[-1].z_rot

    @z_rot.setter
    def z_rot(self, value: float, /) -> None:
        """Positions of segments are not updated."""
        offset: float = value - self.z_rot
        for segment in self:
            segment.z_rot += offset


class DashTunnel(BasePart):
    __slots__ = ("_shape",)

    _shape: Literal[DeviceModel.DashTunnelA, DeviceModel.DashTunnelB]

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        shape: Literal[DeviceModel.DashTunnelA, DeviceModel.DashTunnelB],
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.shape = shape

    @property
    def cost(self) -> Literal[35, 100]:
        match self.shape:
            case DeviceModel.DashTunnelA:
                return 35
            case DeviceModel.DashTunnelB:
                return 100

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, shape={self.shape!r})"

    @property
    def shape(self) -> Literal[DeviceModel.DashTunnelA, DeviceModel.DashTunnelB]:
        return self._shape

    @shape.setter
    def shape(
        self, value: Literal[DeviceModel.DashTunnelA, DeviceModel.DashTunnelB], /
    ) -> None:
        self._shape = value


class SeesawBlock(BasePart):
    __slots__ = ("_auto", "_shape")

    _auto: bool
    _shape: Literal[DeviceModel.SeesawLBlock, DeviceModel.SeesawIBlock]

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        auto: bool = False,
        shape: Literal[DeviceModel.SeesawLBlock, DeviceModel.SeesawIBlock],
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.auto = auto
        self.shape = shape

    @property
    def auto(self) -> bool:
        return self._auto

    @auto.setter
    def auto(self, value: bool, /) -> None:
        self._auto = value

    @property
    def cost(self) -> Literal[100]:
        return 100

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, auto={self.auto!r}, shape={self.shape!r})"
            if self.auto
            else f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, shape={self.shape!r})"
        )

    @property
    def shape(self) -> Literal[DeviceModel.SeesawLBlock, DeviceModel.SeesawIBlock]:
        return self._shape

    @shape.setter
    def shape(
        self, value: Literal[DeviceModel.SeesawLBlock, DeviceModel.SeesawIBlock], /
    ) -> None:
        self._shape = value


class Cannon(BasePart):
    __slots__ = ()

    @property
    def cost(self) -> Literal[30]:
        return 30


class Drawbridge(BasePart):
    __slots__ = ()

    @property
    def cost(self) -> Literal[50]:
        return 50


class Turntable(FixedSpeedDevice):
    __slots__ = ()

    @property
    def cost(self) -> Literal[50]:
        return 50


class Bumper(BasePart):
    __slots__ = ("_powerful",)

    _powerful: bool

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        powerful: bool = False,
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.powerful = powerful

    @property
    def cost(self) -> Literal[20]:
        return 20

    @property
    def powerful(self) -> bool:
        return self._powerful

    @powerful.setter
    def powerful(self, value: bool, /) -> None:
        self._powerful = value

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, powerful={self.powerful!r})"
            if self.powerful
            else f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r})"
        )


class Thorn(BasePart):
    __slots__ = ()

    @property
    def cost(self) -> Literal[35]:
        return 35


class Gear(FixedSpeedDevice):
    __slots__ = ()

    @property
    def cost(self) -> Literal[50]:
        return 50


class Fan(BasePart):
    __slots__ = ("_wind_pattern",)

    _wind_pattern: Literal[
        DeviceModel.Fan, DeviceModel.PowerfulFan, DeviceModel.TimerFan
    ]

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        wind_pattern: Literal[
            DeviceModel.Fan, DeviceModel.PowerfulFan, DeviceModel.TimerFan
        ] = DeviceModel.Fan,
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.wind_pattern = wind_pattern

    @property
    def cost(self) -> Literal[50]:
        return 50

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, wind_pattern={self.wind_pattern!r})"
            if self.wind_pattern != DeviceModel.Fan
            else f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r})"
        )

    @property
    def wind_pattern(
        self,
    ) -> Literal[DeviceModel.Fan, DeviceModel.PowerfulFan, DeviceModel.TimerFan]:
        return self._wind_pattern

    @wind_pattern.setter
    def wind_pattern(
        self,
        value: Literal[DeviceModel.Fan, DeviceModel.PowerfulFan, DeviceModel.TimerFan],
        /,
    ) -> None:
        self._wind_pattern = value


class Spring(BasePart):
    __slots__ = ()

    @property
    def cost(self) -> Literal[25]:
        return 25


@unique
class MovementTiming(Enum):
    A = 23
    B = 39
    C = 55


class TimedDevice(BasePart, ABC):
    """Device Template for devices which can have one of three timings for their movements"""

    __slots__ = ("_timing",)

    _timing: MovementTiming

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        timing: MovementTiming,
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.timing = timing

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, timing={self.timing!r})"

    @property
    def timing(self) -> MovementTiming:
        return self._timing

    @timing.setter
    def timing(self, value: MovementTiming, /) -> None:
        self._timing = value


class Punch(TimedDevice):
    __slots__ = ()

    @property
    def cost(self) -> Literal[30]:
        return 30


class Press(TimedDevice):
    __slots__ = ()

    @property
    def cost(self) -> Literal[50]:
        return 50


class Scissors(TimedDevice):
    __slots__ = ()

    @property
    def cost(self) -> Literal[70]:
        return 70


class MagnifyingGlass(BasePart):
    __slots__ = ()

    @property
    def cost(self) -> Literal[200]:
        return 200


class UpsideDownStageDevice(BasePart):
    __slots__ = ()

    @property
    def cost(self) -> Literal[50]:
        return 50


class UpsideDownBall(BasePart):
    __slots__ = ()

    @property
    def cost(self) -> Literal[25]:
        return 25


class SizeTunnel(BasePart):
    __slots__ = ("_size",)

    _size: Literal[DeviceModel.SmallTunnel, DeviceModel.BigTunnel]

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        size: Literal[DeviceModel.SmallTunnel, DeviceModel.BigTunnel],
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.size = size

    @property
    def cost(self) -> Literal[50]:
        return 50

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, size={self.size!r})"

    @property
    def size(self) -> Literal[DeviceModel.SmallTunnel, DeviceModel.BigTunnel]:
        return self._size

    @size.setter
    def size(
        self, value: Literal[DeviceModel.SmallTunnel, DeviceModel.BigTunnel], /
    ) -> None:
        self._size = value


class TrainTrack(BasePart):
    __slots__ = ("_shape",)

    _shape: Literal[
        DeviceModel.EndTracks,
        DeviceModel.LeftTracks,
        DeviceModel.RightTracks,
        DeviceModel.StraightTracks,
    ]

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        shape: Literal[
            DeviceModel.EndTracks,
            DeviceModel.LeftTracks,
            DeviceModel.RightTracks,
            DeviceModel.StraightTracks,
        ],
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.shape = shape

    @property
    def cost(self) -> Literal[0, 20]:
        return 0 if self.shape is DeviceModel.EndTracks else 20

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, shape={self.shape!r})"

    @property
    def shape(
        self,
    ) -> Literal[
        DeviceModel.EndTracks,
        DeviceModel.LeftTracks,
        DeviceModel.RightTracks,
        DeviceModel.StraightTracks,
    ]:
        return self._shape

    @shape.setter
    def shape(
        self,
        value: Literal[
            DeviceModel.EndTracks,
            DeviceModel.LeftTracks,
            DeviceModel.RightTracks,
            DeviceModel.StraightTracks,
        ],
        /,
    ) -> None:
        self._shape = value


class ToyTrain(BasePart, MutableSequence[TrainTrack]):
    __slots__ = ("_tracks",)

    _tracks: list[TrainTrack]

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        tracks: Iterable[TrainTrack] = (),
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self._tracks = list(tracks)

    def append(self, value: TrainTrack) -> None:
        return self._tracks.append(value)

    def clear(self) -> None:
        self._tracks.clear()

    def __contains__(self, value: Any, /) -> bool:
        return value in self._tracks

    @property
    def cost(self) -> int:
        return 100 + sum(track.cost for track in self)

    def count(self, value: Any) -> int:
        return self._tracks.count(value)

    def __delitem__(self, index: SupportsIndex | slice, /) -> None:
        del self._tracks[index]

    def extend(self, iterable: Iterable[TrainTrack], /) -> None:
        self._tracks.extend(iterable)

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> TrainTrack:
        pass

    @overload
    def __getitem__(self, index: slice, /) -> MutableSequence[TrainTrack]:
        pass

    def __getitem__(
        self, index: SupportsIndex | slice, /
    ) -> TrainTrack | MutableSequence[TrainTrack]:
        return self._tracks[index]

    def __iadd__(self, value: Iterable[TrainTrack], /) -> Self:
        self._tracks += value
        return self

    def index(
        self, value: Any, start: SupportsIndex = 0, stop: SupportsIndex = maxsize, /
    ) -> int:
        return self._tracks.index(value, start, stop)

    def insert(self, index: SupportsIndex, value: TrainTrack, /) -> None:
        return self._tracks.insert(index, value)

    def __iter__(self) -> Iterator[TrainTrack]:
        return iter(self._tracks)

    def __len__(self) -> int:
        return len(self._tracks)

    def pop(self, index: SupportsIndex = -1, /) -> TrainTrack:
        return self._tracks.pop(index)

    def remove(self, value: TrainTrack, /) -> None:
        self._tracks.remove(value)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, tracks={self._tracks!r})"

    def reverse(self) -> None:
        self._tracks.reverse()

    def __reversed__(self) -> Iterator[TrainTrack]:
        return reversed(self._tracks)

    @overload
    def __setitem__(self, index: SupportsIndex, value: TrainTrack, /) -> None:
        pass

    @overload
    def __setitem__(self, slice: slice, value: Iterable[TrainTrack], /) -> None:
        pass

    def __setitem__(
        self, index: SupportsIndex | slice, value: TrainTrack | Iterable[TrainTrack], /
    ) -> None:
        self._tracks[index] = value  # type: ignore


class Warp(BasePart):
    __slots__ = (
        "_dest_x",
        "_dest_y",
        "_dest_z",
        "_return_dest_x",
        "_return_dest_y",
        "_return_dest_z",
        "_return_x_pos",
        "_return_x_rot",
        "_return_y_pos",
        "_return_y_rot",
        "_return_z_pos",
        "_return_z_rot",
    )

    _dest_x: float
    _dest_y: float
    _dest_z: float
    _return_dest_x: float
    _return_dest_y: float
    _return_dest_z: float
    _return_x_pos: float
    _return_x_rot: float
    _return_y_pos: float
    _return_y_rot: float
    _return_z_pos: float
    _return_z_rot: float

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        dest_x: float,
        dest_y: float,
        dest_z: float,
        return_x_pos: float,
        return_y_pos: float,
        return_z_pos: float,
        return_x_rot: float,
        return_y_rot: float,
        return_z_rot: float,
        return_dest_x: float,
        return_dest_y: float,
        return_dest_z: float,
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.dest_z = dest_z
        self.return_dest_x = return_dest_x
        self.return_dest_y = return_dest_y
        self.return_dest_z = return_dest_z
        self.return_x_pos = return_x_pos
        self.return_x_rot = return_x_rot
        self.return_y_pos = return_y_pos
        self.return_y_rot = return_y_rot
        self.return_z_pos = return_z_pos
        self.return_z_rot = return_z_rot

    @property
    def cost(self) -> Literal[25]:
        return 25

    @property
    def dest_x(self) -> float:
        """Positive is right, negative is left"""
        return self._dest_x

    @dest_x.setter
    def dest_x(self, value: float, /) -> None:
        self._dest_x = value

    @property
    def dest_y(self) -> float:
        return self._dest_y

    @dest_y.setter
    def dest_y(self, value: float, /) -> None:
        """Positive is up, negative is down"""
        self._dest_y = value

    @property
    def dest_z(self) -> float:
        """Positive is front, negative is back"""
        return self._dest_z

    @dest_z.setter
    def dest_z(self, value: float, /) -> None:
        self._dest_z = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, dest_x={self.dest_x!r}, dest_y={self.dest_y!r}, dest_z={self.dest_z!r}, return_x_pos={self.return_x_pos}, return_y_pos={self.return_y_pos}, return_z_pos={self.return_z_pos}, return_x_rot={self.return_x_rot}, return_y_rot={self.return_y_rot}, return_z_rot={self.return_z_rot}, return_dest_x={self.return_dest_x}, return_dest_y={self.return_dest_y}, return_dest_z={self.return_dest_z})"

    @property
    def return_dest_x(self) -> float:
        """Positive is right, negative is left"""
        return self._return_dest_x

    @return_dest_x.setter
    def return_dest_x(self, value: float, /) -> None:
        self._return_dest_x = value

    @property
    def return_dest_y(self) -> float:
        return self._return_dest_y

    @return_dest_y.setter
    def return_dest_y(self, value: float, /) -> None:
        """Positive is up, negative is down"""
        self._return_dest_y = value

    @property
    def return_dest_z(self) -> float:
        """Positive is front, negative is back"""
        return self._return_dest_z

    @return_dest_z.setter
    def return_dest_z(self, value: float, /) -> None:
        self._return_dest_z = value

    @property
    def return_x_pos(self) -> float:
        """Positive is right, negative is left"""
        return self._return_x_pos

    @return_x_pos.setter
    def return_x_pos(self, value: float, /) -> None:
        self._return_x_pos = value

    @property
    def return_x_rot(self) -> float:
        """Represented in degrees from 0 to 360
        Positive turns top face front, negative turns top face back
        """
        return self._return_x_rot

    @return_x_rot.setter
    def return_x_rot(self, value: float, /) -> None:
        self._return_x_rot = value % 360

    @property
    def return_y_pos(self) -> float:
        """Positive is up, negative is down"""
        return self._return_y_pos

    @return_y_pos.setter
    def return_y_pos(self, value: float, /) -> None:
        self._return_y_pos = value

    @property
    def return_y_rot(self) -> float:
        """Represented in degrees from 0 to 360
        Positive turns front face right, negative turns front face left
        """
        return self._return_y_rot

    @return_y_rot.setter
    def return_y_rot(self, value: float, /) -> None:
        self._return_y_rot = value % 360

    @property
    def return_z_pos(self) -> float:
        """Positive is front, negative is back"""
        return self._return_z_pos

    @return_z_pos.setter
    def return_z_pos(self, value: float, /) -> None:
        self._return_z_pos = value

    @property
    def return_z_rot(self) -> float:
        """Represented in degrees from 0 to 360
        Positive turns top face left, negative turns top face right
        """
        return self._return_z_rot

    @return_z_rot.setter
    def return_z_rot(self, value: float, /) -> None:
        self._return_z_rot = value % 360


class BlinkingTile(TimedDevice):
    __slots__ = ()

    @property
    def cost(self) -> Literal[20]:
        return 20


class MelodyTile(BasePart):
    __slots__ = ("_note",)

    _note: Literal[
        DeviceModel.MelodyTileLowG,
        DeviceModel.MelodyTileLowGSharp,
        DeviceModel.MelodyTileLowA,
        DeviceModel.MelodyTileLowASharp,
        DeviceModel.MelodyTileLowB,
        DeviceModel.MelodyTileC,
        DeviceModel.MelodyTileCSharp,
        DeviceModel.MelodyTileD,
        DeviceModel.MelodyTileDSharp,
        DeviceModel.MelodyTileE,
        DeviceModel.MelodyTileF,
        DeviceModel.MelodyTileFSharp,
        DeviceModel.MelodyTileG,
        DeviceModel.MelodyTileGSharp,
        DeviceModel.MelodyTileA,
        DeviceModel.MelodyTileASharp,
        DeviceModel.MelodyTileB,
        DeviceModel.MelodyTileHighC,
        DeviceModel.MelodyTileHighCSharp,
        DeviceModel.MelodyTileHighD,
        DeviceModel.MelodyTileHighDSharp,
        DeviceModel.MelodyTileHighE,
        DeviceModel.MelodyTileHighF,
        DeviceModel.MelodyTileHighFSharp,
        DeviceModel.MelodyTileHighG,
    ]

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        note: Literal[
            DeviceModel.MelodyTileLowG,
            DeviceModel.MelodyTileLowGSharp,
            DeviceModel.MelodyTileLowA,
            DeviceModel.MelodyTileLowASharp,
            DeviceModel.MelodyTileLowB,
            DeviceModel.MelodyTileC,
            DeviceModel.MelodyTileCSharp,
            DeviceModel.MelodyTileD,
            DeviceModel.MelodyTileDSharp,
            DeviceModel.MelodyTileE,
            DeviceModel.MelodyTileF,
            DeviceModel.MelodyTileFSharp,
            DeviceModel.MelodyTileG,
            DeviceModel.MelodyTileGSharp,
            DeviceModel.MelodyTileA,
            DeviceModel.MelodyTileASharp,
            DeviceModel.MelodyTileB,
            DeviceModel.MelodyTileHighC,
            DeviceModel.MelodyTileHighCSharp,
            DeviceModel.MelodyTileHighD,
            DeviceModel.MelodyTileHighDSharp,
            DeviceModel.MelodyTileHighE,
            DeviceModel.MelodyTileHighF,
            DeviceModel.MelodyTileHighFSharp,
            DeviceModel.MelodyTileHighG,
        ],
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.note = note

    @property
    def cost(self) -> Literal[20]:
        return 20

    @property
    def note(self) -> Literal[
        DeviceModel.MelodyTileLowG,
        DeviceModel.MelodyTileLowGSharp,
        DeviceModel.MelodyTileLowA,
        DeviceModel.MelodyTileLowASharp,
        DeviceModel.MelodyTileLowB,
        DeviceModel.MelodyTileC,
        DeviceModel.MelodyTileCSharp,
        DeviceModel.MelodyTileD,
        DeviceModel.MelodyTileDSharp,
        DeviceModel.MelodyTileE,
        DeviceModel.MelodyTileF,
        DeviceModel.MelodyTileFSharp,
        DeviceModel.MelodyTileG,
        DeviceModel.MelodyTileGSharp,
        DeviceModel.MelodyTileA,
        DeviceModel.MelodyTileASharp,
        DeviceModel.MelodyTileB,
        DeviceModel.MelodyTileHighC,
        DeviceModel.MelodyTileHighCSharp,
        DeviceModel.MelodyTileHighD,
        DeviceModel.MelodyTileHighDSharp,
        DeviceModel.MelodyTileHighE,
        DeviceModel.MelodyTileHighF,
        DeviceModel.MelodyTileHighFSharp,
        DeviceModel.MelodyTileHighG,
    ]:
        return self._note

    @note.setter
    def note(
        self,
        value: Literal[
            DeviceModel.MelodyTileLowG,
            DeviceModel.MelodyTileLowGSharp,
            DeviceModel.MelodyTileLowA,
            DeviceModel.MelodyTileLowASharp,
            DeviceModel.MelodyTileLowB,
            DeviceModel.MelodyTileC,
            DeviceModel.MelodyTileCSharp,
            DeviceModel.MelodyTileD,
            DeviceModel.MelodyTileDSharp,
            DeviceModel.MelodyTileE,
            DeviceModel.MelodyTileF,
            DeviceModel.MelodyTileFSharp,
            DeviceModel.MelodyTileG,
            DeviceModel.MelodyTileGSharp,
            DeviceModel.MelodyTileA,
            DeviceModel.MelodyTileASharp,
            DeviceModel.MelodyTileB,
            DeviceModel.MelodyTileHighC,
            DeviceModel.MelodyTileHighCSharp,
            DeviceModel.MelodyTileHighD,
            DeviceModel.MelodyTileHighDSharp,
            DeviceModel.MelodyTileHighE,
            DeviceModel.MelodyTileHighF,
            DeviceModel.MelodyTileHighFSharp,
            DeviceModel.MelodyTileHighG,
        ],
        /,
    ) -> None:
        self._note = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x_pos!r}, {self.y_pos!r}, {self.z_pos!r}, {self.x_rot!r}, {self.y_rot!r}, {self.z_rot!r}, note={self.note!r})"


class TextBox(BasePart):
    __slots__ = ("_shape", "_text_id")

    _shape: Literal[DeviceModel.CubicTextBox, DeviceModel.WallTextBox]
    _text_id: int

    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        z_pos: float,
        x_rot: float,
        y_rot: float,
        z_rot: float,
        *,
        shape: Literal[DeviceModel.CubicTextBox, DeviceModel.WallTextBox],
        text_id: SupportsIndex,
    ) -> None:
        super().__init__(x_pos, y_pos, z_pos, x_rot, y_rot, z_rot)
        self.shape = shape
        self.text_id = text_id  # type: ignore[assignment]

    @property
    def cost(self) -> Literal[0]:
        return 0

    @property
    def shape(self) -> Literal[DeviceModel.CubicTextBox, DeviceModel.WallTextBox]:
        return self._shape

    @shape.setter
    def shape(
        self, value: Literal[DeviceModel.CubicTextBox, DeviceModel.WallTextBox], /
    ) -> None:
        self._shape = value

    @property
    def text_id(self) -> int:
        return self._text_id

    @text_id.setter
    def text_id(self, value: SupportsIndex, /) -> None:
        self._text_id = index(value)


class KororinCapsule(BasePart):
    __slots__ = ()

    @property
    def cost(self) -> Literal[0]:
        return 0


class GreenCrystal(BasePart):
    __slots__ = ()

    @property
    def cost(self) -> Literal[0]:
        return 0


class Ant(BasePart):
    __slots__ = ()

    @property
    def cost(self) -> Literal[0]:
        return 0
