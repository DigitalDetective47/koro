from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from typing import Final
from zipfile import ZipFile

from koro import BinSlot, EditorPage, SaveSlot, get_slots

parser: Final[ArgumentParser] = ArgumentParser(
    description="Injects Marble Saga: Kororinpa stages into a save file."
)
parser.add_argument("source", help="the stages to add")
parser.add_argument("dest", help="the save file to inject")
parser.add_argument("slot", nargs="?", default=1, type=int, help="the slot number to place the stage in\n(only applies if injecting a single stage)")
args: Final[Namespace] = parser.parse_args()

s: Sequence[SaveSlot] = get_slots(args.dest)[EditorPage.FRIEND]
if args.source.endswith(".zip"):
    with ZipFile(args.source) as z:
        for i in range(20):
            try:
                s[i].save(BinSlot.deserialize(z.read(f"{i + 1:02}.bin")))
            except KeyError:
                s[i].save(None)
else:
    s[args.slot - 1].save(BinSlot(args.source).load())
