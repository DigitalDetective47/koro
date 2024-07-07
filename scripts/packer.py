from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from typing import Final
from zipfile import ZipFile

from koro import BinSlot, EditorPage, SaveSlot, get_slots

parser: Final[ArgumentParser] = ArgumentParser(
    description="Export saved levels from a Marble Saga: Kororinpa save file and packs them into a ZIP archive."
)
parser.add_argument("source", help="the save file to export levels from")
parser.add_argument("dest", help="the location of the archive")
parser.add_argument(
    "slots",
    nargs="*",
    default=range(1, 21),
    type=int,
    help="the slots to read levels from (useful if your levels aren't neatly sorted in-game)",
    metavar="i",
)
args: Final[Namespace] = parser.parse_args()

s: Sequence[SaveSlot] = get_slots(args.source)[EditorPage.ORIGINAL]
with ZipFile(args.dest, "w") as z:
    for i in args.slots:
        if s[i - 1]:
            z.writestr(f"{i:02}.bin", BinSlot.serialize(s[i - 1].load()))
