from itertools import chain
from typing import Final

from ..level import Level
from .file import FileSlot
from .xml import XmlSlot


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
                    return output + b"\x00" * (len(output) & 1)
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
    def deserialize(data: bytes, /) -> Level:
        return XmlSlot.deserialize(BinSlot.decompress(data))

    @staticmethod
    def serialize(level: Level, /) -> bytes:
        return BinSlot.compress(XmlSlot.serialize(level))
