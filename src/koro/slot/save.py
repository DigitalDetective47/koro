from . import Slot
from enum import Enum, unique


@unique
class EditorPage(Enum):
    ORIGINAL = 0
    FRIEND = 1
    HUDSON = 2
