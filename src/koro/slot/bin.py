from itertools import chain
from re import Match, fullmatch
from typing import Final, Optional

from .. import StageID
from ..stage import Stage
from .file import FileSlot
from .xml import XmlSlot

__all__ = ["BinSlot"]


class BinSlot(FileSlot):
    __slots__ = ()

    @staticmethod
    def compress(data: bytes, /) -> bytes:
        buffer: bytearray = bytearray(1024)
        buffer_index: int = 958
        chunk: bytearray
        data_index: int = 0
        output: Final[bytearray] = bytearray(
            b"\x00\x00\x00\x01\x00\x00\x00\x08"
            + len(data).to_bytes(4, byteorder="big")
            + b"\x00\x00\x00\x01"
        )
        reference_indices: list[int]
        test_buffer: bytearray
        test_length: int
        test_reference_indicies: list[int]
        while data_index < len(data):
            chunk = bytearray(b"\x00")
            for bit in range(8):
                if data_index >= len(data):
                    chunk[0] >>= 8 - bit
                    output.extend(chunk)
                    output.extend(bytes(len(output) & 1))
                    return bytes(output)
                if len(data) - data_index <= 2:
                    buffer[buffer_index] = data[data_index]
                    buffer_index = buffer_index + 1 & 1023
                    chunk[0] = chunk[0] >> 1 | 128
                    chunk.append(data[data_index])
                    data_index += 1
                    continue
                reference_indices = []
                for i in chain(range(buffer_index, 1024), range(buffer_index)):
                    if data[data_index] == buffer[i]:
                        reference_indices.append(i)
                if not reference_indices:
                    buffer[buffer_index] = data[data_index]
                    buffer_index = buffer_index + 1 & 1023
                    chunk[0] = chunk[0] >> 1 | 128
                    chunk.append(data[data_index])
                    data_index += 1
                    continue
                test_buffer = buffer.copy()
                test_buffer[buffer_index] = data[data_index]
                for i in reference_indices.copy():
                    if data[data_index + 1] != test_buffer[i - 1023]:
                        reference_indices.remove(i)
                if not reference_indices:
                    buffer[buffer_index] = data[data_index]
                    buffer_index = buffer_index + 1 & 1023
                    chunk[0] = chunk[0] >> 1 | 128
                    chunk.append(data[data_index])
                    data_index += 1
                    continue
                test_buffer[buffer_index - 1023] = data[data_index + 1]
                for i in reference_indices.copy():
                    if data[data_index + 2] != test_buffer[i - 1022]:
                        reference_indices.remove(i)
                if not reference_indices:
                    buffer[buffer_index] = data[data_index]
                    buffer_index = buffer_index + 1 & 1023
                    chunk[0] = chunk[0] >> 1 | 128
                    chunk.append(data[data_index])
                    data_index += 1
                    continue
                test_length = 4
                test_reference_indicies = reference_indices.copy()
                while test_length <= min(66, len(data) - data_index):
                    test_buffer[buffer_index + test_length - 1026] = data[
                        data_index + test_length - 2
                    ]
                    for i in test_reference_indicies.copy():
                        if (
                            data[data_index + test_length - 1]
                            != test_buffer[i + test_length - 1025]
                        ):
                            test_reference_indicies.remove(i)
                    if test_reference_indicies:
                        reference_indices = test_reference_indicies.copy()
                    else:
                        break
                    test_length += 1
                chunk[0] >>= 1
                test_length -= 1
                if buffer_index + test_length >= 1024:
                    buffer[buffer_index:] = data[
                        data_index : data_index + 1024 - buffer_index
                    ]
                    buffer[: buffer_index + test_length - 1024] = data[
                        data_index + 1024 - buffer_index : data_index + test_length
                    ]
                else:
                    buffer[buffer_index : buffer_index + test_length] = data[
                        data_index : data_index + test_length
                    ]
                buffer_index = buffer_index + test_length & 1023
                chunk.extend(
                    (
                        reference_indices[0] & 255,
                        reference_indices[0] >> 2 & 192 | test_length - 3,
                    )
                )
                data_index += test_length
            output.extend(chunk)
        return bytes(output)

    @staticmethod
    def decompress(data: bytes, /) -> bytes:
        buffer: Final[bytearray] = bytearray(1024)
        buffer_index: int = 958
        handle: int | bytearray
        flags: int
        offset: int
        raw: Final[bytearray] = bytearray(data[:15:-1])
        ref: bytes
        result: Final[bytearray] = bytearray()
        result_size: Final[int] = int.from_bytes(data[8:12], byteorder="big")
        while len(result) < result_size:
            flags = raw.pop()
            for _ in range(8):
                if flags & 1:
                    handle = raw.pop()
                    buffer[buffer_index] = handle
                    buffer_index = buffer_index + 1 & 1023
                    result.append(handle)
                else:
                    if len(raw) < 2:
                        return result
                    ref = bytes((raw.pop() for _ in range(2)))
                    offset = (ref[1] << 2 & 768) + ref[0]
                    handle = bytearray()
                    for i in range((ref[1] & 63) + 3):
                        handle.append(buffer[offset + i - 1024])
                        buffer[buffer_index] = handle[-1]
                        buffer_index = buffer_index + 1 & 1023
                    result.extend(handle)
                flags >>= 1
        return bytes(result)

    @staticmethod
    def deserialize(data: bytes, /) -> Stage:
        return XmlSlot.deserialize(BinSlot.decompress(data))

    @staticmethod
    def filename_to_stageid(filename: str, /) -> StageID:
        m: Final[Optional[Match]] = fullmatch(
            r"A(?P<area>\d{2})S(?P<stage>\d{3})(?P<difficulty>[EH]?)\.bin", filename
        )
        if m is None:
            raise ValueError("Filename did not match the required pattern")
        area: StageID.Region
        try:
            area = {
                1: StageID.Region.THE_EMPTY_LOT,
                2: StageID.Region.NEIGHBORS_HOUSE,
                3: StageID.Region.SIZZLIN_DESERT,
                4: StageID.Region.CHILL_MOUNTAIN,
                5: StageID.Region.OCEAN_TREASURE,
                6: StageID.Region.SPACE_STATION,
                7: StageID.Region.STUMP_TEMPLE,
                8: StageID.Region.CANDY_ISLAND,
                9: StageID.Region.HAUNTED_HOUSE,
                10: StageID.Region.HAUNTED_HOUSE_DARKNESS,
                11: StageID.Region.CITY,
                12: StageID.Region.NIGHT_CITY,
                13: StageID.Region.TUTORIAL,
                15: StageID.Region.WII_BALANCE_BOARD,
                16: StageID.Region.RANKING_STAGE,
                19: StageID.Region.HUDSON,
            }[int(m["area"])]
        except:
            raise ValueError(f'Area {m["area"]} not recognized')
        stage: int = int(m["stage"])
        difficulty: Optional[StageID.Difficulty] = {
            "E": StageID.Difficulty.EASY,
            "": StageID.Difficulty.NORMAL,
            "H": StageID.Difficulty.HARD,
        }[m["difficulty"]]
        if (
            area is StageID.Region.CANDY_ISLAND
            and difficulty is StageID.Difficulty.HARD
        ):
            area = StageID.Region.CANDY_ISLAND_2
            difficulty = StageID.Difficulty.NORMAL
        elif area is StageID.Region.HUDSON and 5 < stage <= 20:
            raise ValueError(
                "Hudson 06 \u2013 20 are stored in the save file; these stages are not used."
            )
        if (
            area
            not in {
                StageID.Region.THE_EMPTY_LOT,
                StageID.Region.NEIGHBORS_HOUSE,
                StageID.Region.SIZZLIN_DESERT,
                StageID.Region.CHILL_MOUNTAIN,
                StageID.Region.OCEAN_TREASURE,
                StageID.Region.SPACE_STATION,
                StageID.Region.STUMP_TEMPLE,
            }
            and difficulty is StageID.Difficulty.NORMAL
        ):
            difficulty = None
        return StageID(area, stage, difficulty)

    @staticmethod
    def serialize(stage: Stage, /) -> bytes:
        return BinSlot.compress(XmlSlot.serialize(stage))

    @staticmethod
    def stageid_to_filename(stageid: StageID, /) -> str:
        if stageid.region is stageid.Region.SURVIVAL:
            raise ValueError("Survivals don't have dedicated stage files.")
        elif stageid.region is stageid.Region.HUDSON and stageid.number > 5:
            raise ValueError("Hudson 06 \u2013 20 are stored in the save file.")
        difficulty_string: Final[str] = (
            "H"
            if stageid.region is stageid.Region.CANDY_ISLAND_2
            else {
                stageid.Difficulty.EASY: "E",
                stageid.Difficulty.NORMAL: "",
                stageid.Difficulty.HARD: "H",
                None: "",
            }[stageid.difficulty]
        )
        region_number: Final[int] = {
            stageid.Region.THE_EMPTY_LOT: 1,
            stageid.Region.NEIGHBORS_HOUSE: 2,
            stageid.Region.SIZZLIN_DESERT: 3,
            stageid.Region.CHILL_MOUNTAIN: 4,
            stageid.Region.OCEAN_TREASURE: 5,
            stageid.Region.SPACE_STATION: 6,
            stageid.Region.STUMP_TEMPLE: 7,
            stageid.Region.CANDY_ISLAND: 8,
            stageid.Region.CANDY_ISLAND_2: 8,
            stageid.Region.HAUNTED_HOUSE: 9,
            stageid.Region.HAUNTED_HOUSE_DARKNESS: 10,
            stageid.Region.CITY: 11,
            stageid.Region.NIGHT_CITY: 12,
            stageid.Region.TUTORIAL: 13,
            stageid.Region.WII_BALANCE_BOARD: 15,
            stageid.Region.RANKING_STAGE: 16,
            stageid.Region.HUDSON: 19,
        }[stageid.region]
        return f"A{region_number:02}S{stageid.number:03}{difficulty_string}.bin"
