from collections.abc import Iterator, Sequence
from io import StringIO
from itertools import chain
from os import SEEK_END
from typing import Final
from xml.etree.ElementTree import Element, fromstring

from ..stage import EditUser, Stage, Theme
from ..stage.model import DecorationModel, DeviceModel, PartModel
from ..stage.part import (
    Ant,
    BasePart,
    BlinkingTile,
    Bumper,
    TextBox,
    Cannon,
    ConveyorBelt,
    DashTunnel,
    Drawbridge,
    Fan,
    FixedSpeedDevice,
    Gear,
    Goal,
    GreenCrystal,
    KororinCapsule,
    Magnet,
    MagnetSegment,
    MagnifyingGlass,
    MelodyTile,
    MovementTiming,
    MovingCurve,
    MovingTile,
    Part,
    Press,
    ProgressMarker,
    Punch,
    Scissors,
    SeesawBlock,
    SizeTunnel,
    SlidingTile,
    Speed,
    Spring,
    Start,
    Thorn,
    TimedDevice,
    ToyTrain,
    TrainTrack,
    Turntable,
    UpsideDownBall,
    UpsideDownStageDevice,
    Walls,
    Warp,
)
from .file import FileSlot

__all__ = ["XmlSlot"]


class XmlSlot(FileSlot):
    __slots__ = ()

    @staticmethod
    def deserialize(data: bytes) -> Stage:
        """Behavior is undefined when passed invalid stage data"""

        def get_values(element: Element, /, tag: str) -> Sequence[str]:
            return element.find(tag).text.strip().split()  # type: ignore[union-attr]

        def get_pos_rot(element: Element, /) -> Iterator[float]:
            return chain(
                map(float, get_values(element, "pos")),
                map(float, get_values(element, "rot")),
            )

        root: Final[Element] = fromstring(
            data.decode("shift_jis", "xmlcharrefreplace").replace(
                '<?xml version="1.0" encoding="SHIFT_JIS"?>',
                '<?xml version="1.0"?>\n<body>',
            )
            + "</body>"
        )
        editinfo: Final[Element] = root.find("EDITINFO")  # type: ignore[assignment]
        output: Final[Stage] = Stage(
            (),
            edit_user=(
                EditUser.PROTECTED
                if editinfo.find("EDITUSER") is None
                else EditUser(int(editinfo.find("EDITUSER").text.strip()))  # type: ignore[union-attr]
            ),
            theme=Theme(int(editinfo.find("THEME").text.strip())),  # type: ignore[union-attr]
            tilt_lock=False if editinfo.find("LOCK") is None else bool(int(editinfo.find("LOCK").text.strip())),  # type: ignore[union-attr]
        )
        groups: Final[dict[int, dict[int, Element]]] = {}
        for elem in root.find("STAGEDATA") or ():
            match elem.tag:
                case "EDIT_LIGHT" | "EDIT_BG_NORMAL":
                    continue
                case "EDIT_MAP_NORMAL":
                    output.add(
                        Part(
                            *get_pos_rot(elem),
                            shape=PartModel(int(get_values(elem, "model")[1])),
                        )
                    )
                case "EDIT_MAP_EXT":
                    output.add(
                        Part(
                            *get_pos_rot(elem),
                            shape=DecorationModel(int(get_values(elem, "model")[1])),
                        )
                    )
                case "EDIT_GIM_START":
                    output.add(Start(*get_pos_rot(elem)))
                case "EDIT_GIM_GOAL":
                    output.add(Goal(*get_pos_rot(elem)))
                case "EDIT_GIM_NORMAL":
                    match DeviceModel(int(get_values(elem, "model")[1])):
                        case DeviceModel.Crystal:
                            output.add(
                                ProgressMarker(
                                    *get_pos_rot(elem),
                                    progress=int(get_values(elem, "hook")[0]) * 2 + 1,  # type: ignore[arg-type]
                                )
                            )
                        case DeviceModel.Respawn:
                            output.add(
                                ProgressMarker(
                                    *get_pos_rot(elem),
                                    progress=int(get_values(elem, "hook")[0]) * 2 + 2,  # type: ignore[arg-type]
                                )
                            )
                        case DeviceModel.MovingTile10x10:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.Tile10x10,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                )
                            )
                        case DeviceModel.MovingTile20x20:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.Tile20x20,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                    walls=(
                                        Walls(0)
                                        if elem.find("hook") is None
                                        else Walls(int(get_values(elem, "hook")[1]))
                                    ),
                                )
                            )
                        case DeviceModel.MovingTile30x30:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.TileA30x30,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                    walls=(
                                        Walls(0)
                                        if elem.find("hook") is None
                                        else Walls(int(get_values(elem, "hook")[1]))
                                    ),
                                )
                            )
                        case DeviceModel.MovingTile30x90:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.TileA30x90,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                )
                            )
                        case DeviceModel.MovingTile90x90A:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.Tile90x90,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                )
                            )
                        case DeviceModel.MovingTile90x90B:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.HoleB90x90,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                )
                            )
                        case DeviceModel.MovingTile10x10Switch:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.Tile10x10,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                    switch=True,
                                )
                            )
                        case DeviceModel.MovingTile20x20Switch:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.Tile20x20,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                    switch=True,
                                    walls=(
                                        Walls(0)
                                        if elem.find("hook") is None
                                        else Walls(int(get_values(elem, "hook")[1]))
                                    ),
                                )
                            )
                        case DeviceModel.MovingTile30x30Switch:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.TileA30x30,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                    switch=True,
                                    walls=(
                                        Walls(0)
                                        if elem.find("hook") is None
                                        else Walls(int(get_values(elem, "hook")[1]))
                                    ),
                                )
                            )
                        case DeviceModel.MovingTile30x90Switch:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.TileA30x90,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                    switch=True,
                                )
                            )
                        case DeviceModel.MovingTile90x90ASwitch:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.Tile90x90,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                    switch=True,
                                )
                            )
                        case DeviceModel.MovingTile90x90BSwitch:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.HoleB90x90,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                    switch=True,
                                )
                            )
                        case DeviceModel.MovingFunnelPipe:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.FunnelPipe,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                )
                            )
                        case DeviceModel.MovingStraightPipe:
                            output.add(
                                MovingTile(
                                    *get_pos_rot(elem),
                                    **dict(
                                        zip(
                                            ("dest_x", "dest_y", "dest_z"),
                                            map(float, get_values(elem, "anmmov1")),
                                        )
                                    ),  # type: ignore[arg-type]
                                    shape=PartModel.StraightPipe,
                                    speed=float(get_values(elem, "anmspd")[0]),
                                )
                            )
                        case DeviceModel.MovingCurveS:
                            output.add(
                                MovingCurve(
                                    *get_pos_rot(elem),
                                    shape=PartModel.CurveS,
                                    speed=Speed(int(get_values(elem, "sts")[0])),
                                )
                            )
                        case DeviceModel.MovingCurveM:
                            output.add(
                                MovingCurve(
                                    *get_pos_rot(elem),
                                    shape=PartModel.CurveM,
                                    speed=Speed(int(get_values(elem, "sts")[0])),
                                )
                            )
                        case DeviceModel.MovingCurveL:
                            output.add(
                                MovingCurve(
                                    *get_pos_rot(elem),
                                    shape=PartModel.CurveL,
                                    speed=Speed(int(get_values(elem, "sts")[0])),
                                )
                            )
                        case DeviceModel.SlidingTile:
                            output.add(SlidingTile(*get_pos_rot(elem)))
                        case DeviceModel.ConveyorBelt:
                            output.add(
                                ConveyorBelt(
                                    *get_pos_rot(elem),
                                    reversing=get_values(elem, "sts")[0] == "39",
                                )
                            )
                        case DeviceModel.DashTunnelA:
                            output.add(
                                DashTunnel(
                                    *get_pos_rot(elem),
                                    shape=DeviceModel.DashTunnelA,
                                )
                            )
                        case DeviceModel.DashTunnelB:
                            output.add(
                                DashTunnel(
                                    *get_pos_rot(elem),
                                    shape=DeviceModel.DashTunnelB,
                                )
                            )
                        case DeviceModel.SeesawLBlock:
                            output.add(
                                SeesawBlock(
                                    *get_pos_rot(elem),
                                    shape=DeviceModel.SeesawLBlock,
                                )
                            )
                        case DeviceModel.SeesawIBlock:
                            output.add(
                                SeesawBlock(
                                    *get_pos_rot(elem),
                                    shape=DeviceModel.SeesawIBlock,
                                )
                            )
                        case DeviceModel.AutoSeesawLBlock:
                            output.add(
                                SeesawBlock(
                                    *get_pos_rot(elem),
                                    auto=True,
                                    shape=DeviceModel.SeesawLBlock,
                                )
                            )
                        case DeviceModel.AutoSeesawIBlock:
                            output.add(
                                SeesawBlock(
                                    *get_pos_rot(elem),
                                    auto=True,
                                    shape=DeviceModel.SeesawIBlock,
                                )
                            )
                        case DeviceModel.Cannon:
                            output.add(Cannon(*get_pos_rot(elem)))
                        case DeviceModel.Drawbridge:
                            output.add(Drawbridge(*get_pos_rot(elem)))
                        case DeviceModel.Turntable:
                            output.add(
                                Turntable(
                                    *get_pos_rot(elem),
                                    speed=Speed(int(get_values(elem, "sts")[0])),
                                )
                            )
                        case DeviceModel.Bumper:
                            output.add(Bumper(*get_pos_rot(elem)))
                        case DeviceModel.PowerfulBumper:
                            output.add(Bumper(*get_pos_rot(elem), powerful=True))
                        case DeviceModel.Thorn:
                            output.add(Thorn(*get_pos_rot(elem)))
                        case DeviceModel.Gear:
                            output.add(
                                Gear(
                                    *get_pos_rot(elem),
                                    speed=Speed(int(get_values(elem, "sts")[0])),
                                )
                            )
                        case DeviceModel.Fan:
                            output.add(Fan(*get_pos_rot(elem)))
                        case DeviceModel.PowerfulFan:
                            output.add(
                                Fan(
                                    *get_pos_rot(elem),
                                    wind_pattern=DeviceModel.PowerfulFan,
                                )
                            )
                        case DeviceModel.TimerFan:
                            output.add(
                                Fan(
                                    *get_pos_rot(elem),
                                    wind_pattern=DeviceModel.TimerFan,
                                )
                            )
                        case DeviceModel.Spring:
                            output.add(Spring(*get_pos_rot(elem)))
                        case DeviceModel.Punch:
                            output.add(
                                Punch(
                                    *get_pos_rot(elem),
                                    timing=MovementTiming(
                                        int(get_values(elem, "sts")[0])
                                    ),
                                )
                            )
                        case DeviceModel.Press:
                            output.add(
                                Press(
                                    *get_pos_rot(elem),
                                    timing=MovementTiming(
                                        int(get_values(elem, "sts")[0])
                                    ),
                                )
                            )
                        case DeviceModel.Scissors:
                            output.add(
                                Scissors(
                                    *get_pos_rot(elem),
                                    timing=MovementTiming(
                                        int(get_values(elem, "sts")[0])
                                    ),
                                )
                            )
                        case DeviceModel.MagnifyingGlass:
                            output.add(MagnifyingGlass(*get_pos_rot(elem)))
                        case DeviceModel.UpsideDownStageDevice:
                            output.add(UpsideDownStageDevice(*get_pos_rot(elem)))
                        case DeviceModel.UpsideDownBall:
                            output.add(UpsideDownBall(*get_pos_rot(elem)))
                        case DeviceModel.SmallTunnel:
                            output.add(
                                SizeTunnel(
                                    *get_pos_rot(elem), size=DeviceModel.SmallTunnel
                                )
                            )
                        case DeviceModel.BigTunnel:
                            output.add(
                                SizeTunnel(
                                    *get_pos_rot(elem), size=DeviceModel.BigTunnel
                                )
                            )
                        case DeviceModel.BlinkingTile:
                            output.add(
                                BlinkingTile(
                                    *get_pos_rot(elem),
                                    timing=MovementTiming(
                                        int(get_values(elem, "sts")[0])
                                    ),
                                )
                            )
                        case DeviceModel.CubicTextBox:
                            output.add(
                                TextBox(
                                    *get_pos_rot(elem),
                                    shape=DeviceModel.CubicTextBox,
                                    text_id=int(get_values(elem, "sts")[0]),
                                )
                            )
                        case DeviceModel.WallTextBox:
                            output.add(
                                TextBox(
                                    *get_pos_rot(elem),
                                    shape=DeviceModel.WallTextBox,
                                    text_id=int(get_values(elem, "sts")[0]),
                                )
                            )
                        case DeviceModel.KororinCapsule:
                            output.add(KororinCapsule(*get_pos_rot(elem)))
                        case DeviceModel.GreenCrystal:
                            output.add(GreenCrystal(*get_pos_rot(elem)))
                        case DeviceModel.Ant:
                            output.add(Ant(*get_pos_rot(elem)))
                        case model if model.name.startswith("MelodyTile"):
                            output.add(MelodyTile(*get_pos_rot(elem), note=model))  # type: ignore[arg-type]
                        case _:
                            groups.setdefault(int(get_values(elem, "group")[0]), {})[
                                int(get_values(elem, "group")[1])
                            ] = elem
        for group in groups.values():
            match DeviceModel(int(get_values(group[0], "model")[1])):
                case DeviceModel.EndMagnet:
                    m: Magnet = Magnet()
                    for _, elem in sorted(group.items()):
                        m.append(
                            MagnetSegment(
                                *get_pos_rot(elem),
                                shape=DeviceModel(int(get_values(elem, "model")[1])),  # type: ignore[arg-type]
                            )
                        )
                    output.add(m)
                case DeviceModel.ToyTrain:
                    t: ToyTrain = ToyTrain(*get_pos_rot(group[0]))
                    for i, elem in sorted(group.items()):
                        if i:
                            t.append(
                                TrainTrack(
                                    *get_pos_rot(elem),
                                    shape=DeviceModel(int(get_values(elem, "model")[1])),  # type: ignore[arg-type]
                                )
                            )
                    output.add(t)
                case DeviceModel.Warp:
                    output.add(
                        Warp(
                            *get_pos_rot(group[0]),
                            **dict(
                                zip(
                                    ("dest_x", "dest_y", "dest_z"),
                                    map(float, get_values(group[0], "anmmov0")),
                                )
                            ),
                            **dict(
                                zip(
                                    (
                                        "return_x_pos",
                                        "return_y_pos",
                                        "return_z_pos",
                                        "return_x_rot",
                                        "return_y_rot",
                                        "return_z_rot",
                                    ),
                                    get_pos_rot(group[1]),
                                    strict=True,
                                )
                            ),
                            **dict(
                                zip(
                                    ("return_dest_x", "return_dest_y", "return_dest_z"),
                                    map(float, get_values(group[1], "anmmov0")),
                                )
                            ),
                        )  # type: ignore[misc]
                    )
        return output

    @staticmethod
    def serialize(stage: Stage, /) -> bytes:
        def minify(value: float, /) -> str:
            """Removes the decimal point from floats representing integers."""
            return str(int(value) if value.is_integer() else value)

        def serialize_numbers(*values: float) -> str:
            """Does not include leading or trailing spaces."""
            return " ".join(minify(value) for value in values)

        def anmtype(device: BasePart, /) -> DeviceModel:
            if isinstance(device, ProgressMarker):
                return (
                    DeviceModel.Crystal if device.progress % 2 else DeviceModel.Respawn
                )
            elif isinstance(device, MovingTile):
                match device.shape:
                    case PartModel.Tile10x10:
                        return (
                            DeviceModel.MovingTile10x10Switch
                            if device.switch
                            else DeviceModel.MovingTile10x10
                        )
                    case PartModel.Tile20x20:
                        return (
                            DeviceModel.MovingTile20x20Switch
                            if device.switch
                            else DeviceModel.MovingTile20x20
                        )
                    case PartModel.TileA30x30:
                        return (
                            DeviceModel.MovingTile30x30Switch
                            if device.switch
                            else DeviceModel.MovingTile30x30
                        )
                    case PartModel.TileA30x90:
                        return (
                            DeviceModel.MovingTile30x90Switch
                            if device.switch
                            else DeviceModel.MovingTile30x90
                        )
                    case PartModel.Tile90x90:
                        return (
                            DeviceModel.MovingTile90x90ASwitch
                            if device.switch
                            else DeviceModel.MovingTile90x90A
                        )
                    case PartModel.HoleB90x90:
                        return (
                            DeviceModel.MovingTile90x90BSwitch
                            if device.switch
                            else DeviceModel.MovingTile90x90B
                        )
                    case PartModel.FunnelPipe:
                        return DeviceModel.MovingFunnelPipe
                    case PartModel.StraightPipe:
                        return DeviceModel.MovingStraightPipe
            elif isinstance(device, MovingCurve):
                match device.shape:
                    case PartModel.CurveS:
                        return DeviceModel.MovingCurveS
                    case PartModel.CurveM:
                        return DeviceModel.MovingCurveM
                    case PartModel.CurveL:
                        return DeviceModel.MovingCurveL
            elif isinstance(device, SlidingTile):
                return DeviceModel.SlidingTile
            elif isinstance(device, ConveyorBelt):
                return DeviceModel.ConveyorBelt
            elif isinstance(device, (DashTunnel, TextBox)):
                return device.shape
            elif isinstance(device, SeesawBlock):
                if device.auto:
                    match device.shape:
                        case DeviceModel.SeesawLBlock:
                            return DeviceModel.AutoSeesawLBlock
                        case DeviceModel.SeesawIBlock:
                            return DeviceModel.AutoSeesawIBlock
                else:
                    return device.shape
            elif isinstance(device, Cannon):
                return DeviceModel.Cannon
            elif isinstance(device, Drawbridge):
                return DeviceModel.Drawbridge
            elif isinstance(device, Turntable):
                return DeviceModel.Turntable
            elif isinstance(device, Bumper):
                return (
                    DeviceModel.PowerfulBumper
                    if device.powerful
                    else DeviceModel.Bumper
                )
            elif isinstance(device, Thorn):
                return DeviceModel.Thorn
            elif isinstance(device, Gear):
                return DeviceModel.Gear
            elif isinstance(device, Fan):
                return device.wind_pattern
            elif isinstance(device, Spring):
                return DeviceModel.Spring
            elif isinstance(device, Punch):
                return DeviceModel.Punch
            elif isinstance(device, Press):
                return DeviceModel.Press
            elif isinstance(device, Scissors):
                return DeviceModel.Scissors
            elif isinstance(device, MagnifyingGlass):
                return DeviceModel.MagnifyingGlass
            elif isinstance(device, UpsideDownStageDevice):
                return DeviceModel.UpsideDownStageDevice
            elif isinstance(device, UpsideDownBall):
                return DeviceModel.UpsideDownBall
            elif isinstance(device, SizeTunnel):
                return device.size
            elif isinstance(device, BlinkingTile):
                return DeviceModel.BlinkingTile
            elif isinstance(device, MelodyTile):
                return device.note
            elif isinstance(device, KororinCapsule):
                return DeviceModel.KororinCapsule
            elif isinstance(device, GreenCrystal):
                return DeviceModel.GreenCrystal
            elif isinstance(device, Ant):
                return DeviceModel.Ant
            else:
                raise ValueError(f"part {device!r} does not have a known anmtype")

        def device_data(device: BasePart, /) -> str:
            if isinstance(device, ProgressMarker):
                return f"<hook> {(device._progress - 1) // 2} 0 </hook>\n"
            elif isinstance(device, MovingTile):
                anmmov: Final[str] = (
                    f"<anmspd> {minify(device.speed)} 0 </anmspd>\n<anmmov0> {serialize_numbers(device.x_pos, device.y_pos, device.z_pos)} </anmmov0>\n<anmmov1> {serialize_numbers(device.dest_x, device.dest_y, device.dest_z)} </anmmov1>"
                )
                if device.walls:
                    match device.shape:
                        case PartModel.Tile20x20:
                            return f"<hook> {DeviceModel.MovingTile20x20Wall.value} {device.walls.value} </hook>\n{anmmov}\n"
                        case PartModel.TileA30x30:
                            return f"<hook> {DeviceModel.MovingTile30x30Wall.value} {device.walls.value} </hook>\n{anmmov}\n"
                return anmmov
            else:
                return ""

        def sts(part: BasePart, /) -> int:
            if isinstance(part, FixedSpeedDevice):
                return part.speed.value
            elif isinstance(part, ConveyorBelt):
                return 39 if part.reversing else 23
            elif isinstance(part, TimedDevice):
                return part.timing.value
            else:
                return 7

        with StringIO(
            f'<?xml version="1.0" encoding="SHIFT_JIS"?>\n<EDITINFO>\n<THEME> {stage.theme.value} </THEME>\n<LOCK> {int(stage.tilt_lock)} </LOCK>\n<EDITUSER> {stage.edit_user.value} </EDITUSER>\n</EDITINFO>\n<STAGEDATA>\n<EDIT_BG_NORMAL>\n<model> "EBB_{stage.theme.value:02}.bin 0 </model>\n</EDIT_BG_NORMAL>\n'
        ) as output:
            output.seek(0, SEEK_END)
            group: int = 1
            for part in stage:
                if isinstance(part, Magnet):
                    for i, segment in enumerate(part):
                        output.write(
                            f'<EDIT_GIM_NORMAL>\n<model> "EGB_{stage.theme.value:02}.bin" {segment.shape.value} </model>\n<pos> {serialize_numbers(segment.x_pos, segment.y_pos, segment.z_pos)} </pos>\n<rot> {serialize_numbers(segment.x_rot, segment.y_rot, segment.z_rot)} </rot>\n<sts> 7 </sts>\n<group> {group} {i} </group>\n</EDIT_GIM_NORMAL>\n'
                        )
                    group += 1
                elif isinstance(part, ToyTrain):
                    output.write(
                        f'<EDIT_GIM_NORMAL>\n<model> "EGB_{stage.theme.value:02}.bin" {DeviceModel.ToyTrain.value} </model>\n<pos> {serialize_numbers(part.x_pos, part.y_pos, part.z_pos)} </pos>\n<rot> {serialize_numbers(part.x_rot, part.y_rot, part.z_rot)} </rot>\n<sts> 7 </sts>\n<group> {group} 0 </group>\n</EDIT_GIM_NORMAL>\n'
                    )
                    for i, track in enumerate(part, 1):
                        output.write(
                            f'<EDIT_GIM_NORMAL>\n<model> "EGB_{stage.theme.value:02}.bin" {track.shape.value} </model>\n<pos> {serialize_numbers(track.x_pos, track.y_pos, track.z_pos)} </pos>\n<rot> {serialize_numbers(track.x_rot, track.y_rot, track.z_rot)} </rot>\n<sts> 7 </sts>\n<group> {group} {i} </group>\n</EDIT_GIM_NORMAL>\n'
                        )
                    group += 1
                elif isinstance(part, Warp):
                    output.write(
                        f'<EDIT_GIM_NORMAL>\n<model> "EGB_{stage.theme.value:02}.bin" {DeviceModel.Warp.value} </model>\n<pos> {serialize_numbers(part.x_pos, part.y_pos, part.z_pos)} </pos>\n<rot> {serialize_numbers(part.x_rot, part.y_rot, part.z_rot)} </rot>\n<sts> 7 </sts>\n<anmmov0> {serialize_numbers(part.dest_x, part.dest_y, part.dest_z)} </anmmov0>\n<group> {group} 0 </group>\n</EDIT_GIM_NORMAL>\n<EDIT_GIM_NORMAL>\n<model> "EGB_{stage.theme.value:02}.bin" {DeviceModel.Warp.value} </model>\n<pos> {serialize_numbers(part.return_x_pos, part.return_y_pos, part.return_z_pos)} </pos>\n<rot> {serialize_numbers(part.return_x_rot, part.return_y_rot, part.return_z_rot)} </rot>\n<sts> 7 </sts>\n<anmmov0> {serialize_numbers(part.return_dest_x, part.return_dest_y, part.return_dest_z)} </anmmov0>\n<group> {group} 1 </group>\n</EDIT_GIM_NORMAL>\n'
                    )
                    group += 1
                else:
                    if isinstance(part, Start):
                        output.write("<EDIT_GIM_START>\n")
                    elif isinstance(part, Goal):
                        output.write("<EDIT_GIM_GOAL>\n")
                    elif isinstance(part, Part):
                        if isinstance(part.shape, DecorationModel):
                            output.write("<EDIT_MAP_EXT>\n")
                        else:
                            output.write("<EDIT_MAP_NORMAL>\n")
                    else:
                        output.write("<EDIT_GIM_NORMAL>\n")
                    if isinstance(part, Part):
                        if isinstance(part.shape, DecorationModel):
                            output.write(
                                f'<model> "EME_{stage.theme.value:02}.bin" {part.shape.value} </model>\n'
                            )
                        else:
                            output.write(
                                f'<model> "EMB_{stage.theme.value:02}.bin" {part.shape.value} </model>\n'
                            )
                    elif isinstance(part, Start):
                        output.write(
                            f'<model> "EGB_{stage.theme.value:02}.bin" 0 </model>\n'
                        )
                    elif isinstance(part, Goal):
                        output.write(
                            f'<model> "EGB_{stage.theme.value:02}.bin" 1 </model>\n'
                        )
                    else:
                        output.write(
                            f'<model> "EGB_{stage.theme.value:02}.bin" {anmtype(part).value} </model>\n'
                        )
                    output.write(
                        f"<pos> {serialize_numbers(part.x_pos, part.y_pos, part.z_pos)} </pos>\n<rot> {serialize_numbers(part.x_rot, part.y_rot, part.z_rot)} </rot>\n<sts> {sts(part)} </sts>\n"
                    )
                    try:
                        output.write(f"<anmtype> {anmtype(part).value} </anmtype>\n")
                    except ValueError:
                        pass
                    output.write(device_data(part))
                    if isinstance(part, Start):
                        output.write("</EDIT_GIM_START>\n")
                    elif isinstance(part, Goal):
                        output.write("</EDIT_GIM_GOAL>\n")
                    elif isinstance(part, Part):
                        if isinstance(part.shape, DecorationModel):
                            output.write("</EDIT_MAP_EXT>\n")
                        else:
                            output.write("</EDIT_MAP_NORMAL>\n")
                    else:
                        output.write("</EDIT_GIM_NORMAL>\n")
            output.write("</STAGEDATA>")
            return output.getvalue().encode("shift_jis", "xmlcharrefreplace")
