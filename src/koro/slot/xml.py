from io import StringIO
from typing import Final

from ..level import Level
from ..level.model import DecorationModel, DeviceModel, PartModel
from ..level.part import (
    Ant,
    BasePart,
    BlinkingTile,
    Bumper,
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
    MagnifyingGlass,
    MelodyTile,
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
    Spring,
    Start,
    Thorn,
    TimedDevice,
    ToyTrain,
    Turntable,
    UpsideDownBall,
    UpsideDownStageDevice,
    Warp,
)
from .file import FileSlot

__all__ = ["XmlSlot"]


def minify(value: float, /) -> str:
    """Removes the decimal point from floats representing integers."""
    return str(int(value) if value.is_integer() else value)


def serialize_numbers(*values: float) -> str:
    """Does not include leading or trailing spaces."""
    return " ".join(minify(value) for value in values)


def anmtype(device: BasePart, /) -> DeviceModel:
    if isinstance(device, ProgressMarker):
        return DeviceModel.Crystal if device.progress % 2 else DeviceModel.Respawn
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
    elif isinstance(device, DashTunnel):
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
        return DeviceModel.PowerfulBumper if device.powerful else DeviceModel.Bumper
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
        return f"<hook> {(device._progress - 1) // 2} 0 </hook>"
    elif isinstance(device, MovingTile):
        anmmov: Final[str] = (
            f"<anmspd> {minify(device.speed)} 0 </anmspeed><anmmov0> {serialize_numbers(device.x_pos, device.y_pos, device.z_pos)} </anmmov0><anmmov1> {serialize_numbers(device.dest_x, device.dest_y, device.dest_z)} </anmmov1>"
        )
        if (
            device.wall_back
            or device.wall_front
            or device.wall_left
            or device.wall_right
        ):
            match device.shape:
                case PartModel.Tile20x20:
                    return f"<hook> {DeviceModel.MovingTile20x20Wall.value} {(device.wall_back << 3) + (device.wall_left << 2) + (device.wall_front << 1) + device.wall_right} </hook>{anmmov}"
                case PartModel.TileA30x30:
                    return f"<hook> {DeviceModel.MovingTile30x30Wall.value} {(device.wall_back << 3) + (device.wall_left << 2) + (device.wall_front << 1) + device.wall_right} </hook>{anmmov}"
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


class XmlSlot(FileSlot):
    @staticmethod
    def serialize(level: Level, /) -> bytes:
        with StringIO(
            f'<?xml version="1.0" encoding="SHIFT_JIS"?><EDITINFO><THEME> {level.theme.value} </THEME><LOCK> {int(level.tilt_lock)} </LOCK><EDITUSER> {level.edit_user.value} </EDITUSER></EDITINFO><STAGEDATA><EDIT_BG_NORMAL><model> "EBB_{level.theme.value:02}.bin 0 </model></EDIT_BG_NORMAL>'
        ) as output:
            group: int = 0
            for part in level:
                if isinstance(part, Magnet):
                    for i, segment in enumerate(part):
                        output.write(
                            f'<EDIT_GIM_NORMAL><model> "EGB_{level.theme.value:02}.bin" {segment.shape} </model><pos> {serialize_numbers(segment.x_pos, segment.y_pos, segment.z_pos)} </pos><rot> {serialize_numbers(segment.x_rot, segment.y_rot, segment.z_rot)} </rot><sts> 7 </sts><group> {group} {i} </group></EDIT_GIM_NORMAL>'
                        )
                    group += 1
                elif isinstance(part, ToyTrain):
                    output.write(
                        f'<EDIT_GIM_NORMAL><model> "EGB_{level.theme.value:02}.bin" {DeviceModel.ToyTrain.value} </model><pos> {serialize_numbers(part.x_pos, part.y_pos, part.z_pos)} </pos><rot> {part.x_rot, part.y_rot, part.z_rot} </rot><sts> 7 </sts><group> {group} 0 </group></EDIT_GIM_NORMAL>'
                    )
                    for i, track in enumerate(part, 1):
                        output.write(
                            f'<EDIT_GIM_NORMAL><model> "EGB_{level.theme.value:02}.bin" {track.shape} </model><pos> {serialize_numbers(track.x_pos, track.y_pos, track.z_pos)} </pos><rot> {serialize_numbers(track.x_rot, track.y_rot, track.z_rot)} </rot><sts> 7 </sts><group> {group} {i} </group></EDIT_GIM_NORMAL>'
                        )
                    group += 1
                elif isinstance(part, Warp):
                    output.write(
                        f'<EDIT_GIM_NORMAL><model> "EGB_{level.theme.value:02}.bin" {DeviceModel.Warp.value} </model><pos> {serialize_numbers(part.x_pos, part.y_pos, part.z_pos)} </pos><rot> {part.x_rot, part.y_rot, part.z_rot} </rot><sts> 7 </sts><anmmov0> {serialize_numbers(part.dest_x, part.dest_y, part.dest_z)} </anmmov0><group> {group} 0 </group></EDIT_GIM_NORMAL><EDIT_GIM_NORMAL><model> "EGB_{level.theme.value:02}.bin" {DeviceModel.Warp.value} </model><pos> {serialize_numbers(part.return_x_pos, part.return_y_pos, part.return_z_pos)} </pos><rot> {part.return_x_rot, part.return_y_rot, part.return_z_rot} </rot><sts> 7 </sts><anmmov0> {serialize_numbers(part.return_dest_x, part.return_dest_y, part.return_dest_z)} </anmmov0><group> {group} 0 </group></EDIT_GIM_NORMAL>'
                    )
                    group += 1
                else:
                    if isinstance(part, Start):
                        output.write("<EDIT_GIM_START>")
                    elif isinstance(part, Goal):
                        output.write("<EDIT_GIM_GOAL>")
                    elif isinstance(part, Part):
                        if isinstance(part.shape, DecorationModel):
                            output.write("<EDIT_MAP_EXT>")
                        else:
                            output.write("<EDIT_MAP_NORMAL>")
                    else:
                        output.write("<EDIT_GIM_NORMAL>")
                    if isinstance(part, Part):
                        if isinstance(part.shape, DecorationModel):
                            output.write(
                                f'<model> "EME_{level.theme.value:02}.bin" {part.shape.value} </model>'
                            )
                        else:
                            output.write(
                                f'<model> "EMB_{level.theme.value:02}.bin" {part.shape.value} </model>'
                            )
                    elif isinstance(part, Start):
                        output.write(
                            f'<model> "EGB_{level.theme.value:02}.bin" 0 </model>'
                        )
                    elif isinstance(part, Goal):
                        output.write(
                            f'<model> "EGB_{level.theme.value:02}.bin" 1 </model>'
                        )
                    else:
                        output.write(
                            f'<model> "EGB_{level.theme.value:02}.bin" {anmtype(part).value} </model>'
                        )
                    output.write(
                        f"<pos> {serialize_numbers(part.x_pos, part.y_pos, part.z_pos)} </pos><rot> {part.x_rot, part.y_rot, part.z_rot} </rot><sts> {sts(part)} </sts>"
                    )
                    try:
                        output.write(f"<anmtype> {anmtype(part).value} </anmtype>")
                    except ValueError:
                        pass
                    output.write(device_data(part))
                    if isinstance(part, Start):
                        output.write("</EDIT_GIM_START>")
                    elif isinstance(part, Goal):
                        output.write("</EDIT_GIM_GOAL>")
                    elif isinstance(part, Part):
                        if isinstance(part.shape, DecorationModel):
                            output.write("</EDIT_MAP_EXT>")
                        else:
                            output.write("</EDIT_MAP_NORMAL>")
                    else:
                        output.write("</EDIT_GIM_NORMAL>")
            output.write("</STAGEDATA>")
            return output.getvalue().encode("shift_jis", "xmlcharrefreplace")
