from argparse import ArgumentParser, Namespace
from typing import Final
from zipfile import ZipFile

from koro import BinSlot, EditorPage, SaveSlot

parser: Final[ArgumentParser] = ArgumentParser(
    description="Injects Marble Saga: Kororinpa stages into a save file."
)
parser.add_argument("source", help="the stages to add")
parser.add_argument("dest", help="the save file to inject")
parser.add_argument(
    "slot",
    nargs="?",
    default=1,
    type=int,
    help="the slot number to place the stage in\n(only applies if injecting a single stage)",
)
args: Final[Namespace] = parser.parse_args()

if args.source.endswith(".zip"):
    with ZipFile(args.source) as z:
        for slot in range(1, 21):
            save_location: SaveSlot = SaveSlot(args.dest, EditorPage.FRIEND, slot)
            try:
                save_location.save(BinSlot.deserialize(z.read(f"{slot:02}.bin")))
            except KeyError:
                save_location.save(None)
else:
    SaveSlot(args.dest, EditorPage.FRIEND, args.slot - 1).save(
        BinSlot(args.source).load()
    )
