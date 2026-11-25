"""Minimal little-endian CDR reader for ROS 2 serialized messages."""

import struct


class CdrReader:
    """Reads primitive values from a ROS 2 CDR buffer, honouring alignment."""

    ENCAPSULATION_SIZE = 4

    def __init__(self, data: bytes):
        self._data = data
        self._pos = self.ENCAPSULATION_SIZE

    def _align(self, size: int) -> None:
        offset = self._pos - self.ENCAPSULATION_SIZE
        self._pos += (-offset) % size

    def _unpack(self, fmt: str, size: int):
        self._align(size)
        (value,) = struct.unpack_from("<" + fmt, self._data, self._pos)
        self._pos += size
        return value

    def int32(self) -> int:
        return self._unpack("i", 4)

    def uint32(self) -> int:
        return self._unpack("I", 4)

    def float64(self) -> float:
        return self._unpack("d", 8)

    def float64_array(self, count: int) -> list:
        return [self.float64() for _ in range(count)]

    def float64_sequence(self) -> list:
        return self.float64_array(self.uint32())

    def string(self) -> str:
        length = self.uint32()
        raw = self._data[self._pos : self._pos + length]
        self._pos += length
        return raw.rstrip(b"\x00").decode("utf-8", errors="replace")

    def string_sequence(self) -> list:
        return [self.string() for _ in range(self.uint32())]

    def stamp(self) -> float:
        """builtin_interfaces/Time as seconds."""
        sec = self.int32()
        nanosec = self.uint32()
        return sec + nanosec * 1e-9

    def header(self) -> tuple:
        """std_msgs/Header -> (stamp_seconds, frame_id)."""
        stamp = self.stamp()
        return stamp, self.string()
