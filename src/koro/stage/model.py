from enum import Enum, unique
from typing import TypeAlias


__all__ = ["DecorationModel", "DeviceModel", "Model", "PartModel"]


@unique
class PartModel(Enum):
    Tile10x10 = 9
    Tile20x20 = 11
    TileA30x30 = 13
    TileB30x30 = 16
    Tile10x90 = 10
    Tile20x90 = 12
    TileA30x90 = 14
    TileB30x90 = 17
    Tile90x90 = 15
    MagmaTile = 20
    """Touching the magma will start you over."""
    SlipperyTile = 21
    """This tile made of ice will make you slide."""
    StickyTile = 22
    """Touching this tile makes it hard to roll."""
    Wall10x10 = 48
    Wall10x20 = 49
    Wall10x30 = 50
    Wall10x90 = 51
    Wall5x30 = 52
    Wall30x15 = 53
    DecorativeWallA = 55
    DecorativeWallB = 54
    InvisibleTile = 34
    HillA = 41
    HillB = 42
    HillC = 43
    ObstacleHill = 44
    HillWallA = 31
    HillWallB = 32
    HillWallC = 33
    Arch = 39
    ArchWall = 40
    CurveS = 1
    CurveM = 2
    CurveL = 3
    SpiralSet = 46
    RoundPillar = 4
    CurveWallS = 5
    CurveWallM = 6
    CurveWallL = 7
    SpiralWallA = 37
    SpiralWallB = 38
    StraightRailA = 60
    StraightRailB = 61
    CurveRail = 56
    ArchRail = 58
    StraightRailLA = 62
    StraightRailLB = 63
    CurveRailL = 57
    ArchRailL = 59
    FunnelPipe = 23
    StraightPipe = 24
    CurvePipe = 25
    SpiralPipe = 26
    Tunnel = 47
    Bridge = 0
    RampA = 35
    RampB = 36
    Turnover = 8
    DecorativeTile = 18
    GuardTile = 19
    MouseHole = 45
    Hole30x30 = 27
    HoleA90x90 = 28
    HoleB90x90 = 29
    HoleC90x90 = 30


@unique
class DecorationModel(Enum):
    """Decoration models are stored in a separate file; their appearance, size, shape, and availability varies depending on the theme."""

    Decoration01 = 0
    Decoration02 = 1
    Decoration03 = 2
    Decoration04 = 3
    Decoration05 = 4
    Decoration06 = 5
    Decoration07 = 6
    Decoration08 = 7
    Decoration09 = 8
    Decoration10 = 9
    Decoration11 = 10
    Decoration12 = 11


@unique
class DeviceModel(Enum):
    Start = 0
    """This part marks the starting point."""
    Goal = 1
    """This part marks the goal point."""
    Crystal = 49
    """Crystals are placed throughout the stage."""
    Respawn = 2
    """This part marks the restart point."""
    MovingTile10x10 = 3
    """A tile that moves."""
    MovingTile20x20 = 4
    """A tile that moves."""
    MovingTile30x30 = 5
    """A tile that moves."""
    MovingTile30x90 = 6
    """A tile that moves."""
    MovingTile90x90A = 8
    """A tile that moves."""
    MovingTile90x90B = 7
    """A tile that moves."""
    MovingTile10x10Switch = 84
    """This tile moves when you get on it."""
    MovingTile20x20Switch = 85
    """This tile moves when you get on it."""
    MovingTile30x30Switch = 86
    """This tile moves when you get on it."""
    MovingTile30x90Switch = 87
    """This tile moves when you get on it."""
    MovingTile90x90ASwitch = 89
    """This tile moves when you get on it."""
    MovingTile90x90BSwitch = 88
    """This tile moves when you get on it."""
    MovingFunnelPipe = 37
    """A moving pipe."""
    MovingStraightPipe = 38
    """A moving pipe."""
    MovingCurveS = 46
    """A moving curve."""
    MovingCurveM = 47
    """A moving curve."""
    MovingCurveL = 48
    """A moving curve."""
    SlidingTile = 11
    """This tile slides as you tilt the Wii Remote."""
    ConveyorBelt = 23
    """This conveyor belt carries your ball."""
    EndMagnet = 20
    """Your ball can stick to this magnet to travel."""
    StraightMagnet = 17
    """Your ball can stick to this magnet to travel."""
    CurveMagnetL = 18
    """Your ball can stick to this magnet to travel."""
    CurveMagnetS = 19
    """Your ball can stick to this magnet to travel."""
    DashTunnelA = 32
    """This tunnel speeds up your ball."""
    DashTunnelB = 33
    """This tunnel speeds up your ball."""
    SeesawLBlock = 13
    """This part rotates when tilting the Wii Remote."""
    SeesawIBlock = 14
    """This part rotates when tilting the Wii Remote."""
    AutoSeesawLBlock = 15
    """A rotating block."""
    AutoSeesawIBlock = 16
    """A rotating block."""
    Cannon = 21
    """Fires your ball into the air."""
    Drawbridge = 44
    """Can be crossed if your ball bumps it down."""
    Turntable = 35
    """A rotating disc."""
    Bumper = 12
    """Your ball goes flying when touching it."""
    PowerfulBumper = 51
    """Your ball goes flying when touching it."""
    Thorn = 34
    """You have to start over when touching it."""
    Gear = 39
    """A rotating gear."""
    Fan = 45
    """This fan will blow your ball around."""
    PowerfulFan = 52
    """A fan with strong wind power."""
    TimerFan = 53
    """Its wind power is switched on and off."""
    Spring = 30
    """This tile makes your ball bounce."""
    Punch = 27
    """Pushes the ball forward with a strong punch."""
    Press = 28
    """Pushes the ball forward."""
    Scissors = 36
    """You'll start over if you ball is chopped."""
    MagnifyingGlass = 29
    """You start over if the ball hits the light."""
    UpsideDownStageDevice = 31
    """Flips the stage 180 degrees upside down."""
    UpsideDownBall = 43
    """Flips gravity upside down."""
    SmallTunnel = 25
    """Your ball shrinks when going through."""
    BigTunnel = 26
    """Your ball grows when going through."""
    ToyTrain = 58
    """Carries your ball."""
    EndTracks = 57
    LeftTracks = 56
    RightTracks = 55
    StraightTracks = 54
    Warp = 41
    """Teleports your ball to another warp point."""
    BlinkingTile = 40
    """Turns visible and invisible."""
    MelodyTileLowG = 59
    """Makes a sound when the ball rolls over it."""
    MelodyTileLowGSharp = 60
    """Makes a sound when the ball rolls over it."""
    MelodyTileLowA = 61
    """Makes a sound when the ball rolls over it."""
    MelodyTileLowASharp = 62
    """Makes a sound when the ball rolls over it."""
    MelodyTileLowB = 63
    """Makes a sound when the ball rolls over it."""
    MelodyTileC = 64
    """Makes a sound when the ball rolls over it."""
    MelodyTileCSharp = 65
    """Makes a sound when the ball rolls over it."""
    MelodyTileD = 66
    """Makes a sound when the ball rolls over it."""
    MelodyTileDSharp = 67
    """Makes a sound when the ball rolls over it."""
    MelodyTileE = 68
    """Makes a sound when the ball rolls over it."""
    MelodyTileF = 69
    """Makes a sound when the ball rolls over it."""
    MelodyTileFSharp = 70
    """Makes a sound when the ball rolls over it."""
    MelodyTileG = 71
    """Makes a sound when the ball rolls over it."""
    MelodyTileGSharp = 72
    """Makes a sound when the ball rolls over it."""
    MelodyTileA = 73
    """Makes a sound when the ball rolls over it."""
    MelodyTileASharp = 74
    """Makes a sound when the ball rolls over it."""
    MelodyTileB = 75
    """Makes a sound when the ball rolls over it."""
    MelodyTileHighC = 76
    """Makes a sound when the ball rolls over it."""
    MelodyTileHighCSharp = 77
    """Makes a sound when the ball rolls over it."""
    MelodyTileHighD = 78
    """Makes a sound when the ball rolls over it."""
    MelodyTileHighDSharp = 79
    """Makes a sound when the ball rolls over it."""
    MelodyTileHighE = 80
    """Makes a sound when the ball rolls over it."""
    MelodyTileHighF = 81
    """Makes a sound when the ball rolls over it."""
    MelodyTileHighFSharp = 82
    """Makes a sound when the ball rolls over it."""
    MelodyTileHighG = 83
    """Makes a sound when the ball rolls over it."""
    KororinCapsule = 95
    GreenCrystal = 96
    Ant = 97

    # Extra models
    MovingTile20x20Wall = 9
    """The wall that can be added to Moving Tile 20x20"""
    MovingTile30x30Wall = 10
    """The wall that can be added to Moving Tile 30x30"""
    CannonArrow = 22
    """The arrow used to show the trajectory from a Cannon"""
    ConveyorBeltArrows = 24
    """The arrows used by the Conveyor Belt when changing direction"""
    BlueLine = 42
    """The blue line used by moving tiles"""
    OrangeLine = 50
    """The orange line used by switch moving tiles"""
    CubicTextBox = 92
    """A cubic region that opens a text box"""
    WallTextBox = 93
    """A tall, wide, and thin region that opens a text box"""
    QuestionMark = 94
    """An animated question mark with a glow beneath it"""


Model: TypeAlias = PartModel | DecorationModel | DeviceModel
