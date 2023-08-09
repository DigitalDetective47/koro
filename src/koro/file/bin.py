from itertools import chain
from typing import Final

from ..item.level import Level, LevelNotFoundError
from . import Location

__all__ = ["BinLevel", "BinLevelNotFoundError"]


class BinLevelNotFoundError(FileNotFoundError, LevelNotFoundError):
    pass


class BinLevel(Location, Level):
    __slots__ = ()

    @staticmethod
    def compress(data: bytes, /) -> bytes:
        """Compress the given level data into the game's format."""
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
            for _ in range(8):
                if data_index >= len(data):
                    output.extend(chunk)
                    return output
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
                    test_buffer[buffer_index + test_length - 1025] = data[
                        data_index + test_length - 1
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
        return output + b"\x00"

    @staticmethod
    def decompress(data: bytes, /) -> bytes:
        """Decompress the given data into raw level data."""
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
        return result.replace(b"<EDITUSER> 3 </EDITUSER>", b"<EDITUSER> 2 </EDITUSER>")

    def delete(self) -> None:
        try:
            return super().delete()
        except FileNotFoundError as e:
            raise BinLevelNotFoundError(*e.args)

    def __len__(self) -> int:
        try:
            with open(self.path, "rb") as f:
                f.seek(8)
                return int.from_bytes(f.read(4), byteorder="big")
        except FileNotFoundError as e:
            BinLevelNotFoundError(*e.args)

    def read(self) -> bytes:
        try:
            with open(self.path, "rb") as f:
                return self.decompress(f.read())
        except FileNotFoundError as e:
            raise BinLevelNotFoundError(*e.args)

    def write(self, new_content: bytes, /) -> None:
        with open(self.path, "wb") as f:
            f.write(self.compress(new_content))
