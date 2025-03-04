from argparse import ArgumentParser, Namespace
from typing import Final
from zipfile import ZipFile

from koro import BinSlot, EditorPage, SaveSlot, Stage

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

with ZipFile(args.dest, "w") as z:
    for dest_slot, src_slot in enumerate(args.slots, 1):
        stage_data: Stage | None = SaveSlot(
            args.source, EditorPage.FRIEND, src_slot
        ).load()
        if stage_data is not None:
            z.writestr(f"{dest_slot:02}.bin", BinSlot.serialize(stage_data))
