"""Plain data types and CDR decoders for the topics used in the lab.

The decawave_msgs layout was reverse-engineered from the lab rosbags
(see docs/knowledge/messages.md). Decoding from bytes means the code
does not depend on the field names of the real decawave_msgs package.
"""

import math
from dataclasses import dataclass, field

from .cdr import CdrReader


@dataclass
class AnchorMeasurement:
    anchor_id: str
    x: float
    y: float
    z: float
    distance: float
    anchor_qf: float  # unknown meaning, always 1.0 in the lab bags
    distance_qf: float  # unknown meaning, always 1.0 in the lab bags

    @property
    def position(self) -> tuple:
        return (self.x, self.y, self.z)


@dataclass
class AnchorArray:
    stamp: float
    anchors: list = field(default_factory=list)


@dataclass
class TagPose:
    stamp: float
    x: float
    y: float
    z: float
    quality: float
    anchor_count: int


@dataclass
class Pose2D:
    stamp: float
    x: float
    y: float
    theta: float


@dataclass
class WheelState:
    stamp: float
    position: list
    velocity: list


def _read_anchor(reader: CdrReader) -> AnchorMeasurement:
    _, anchor_id = reader.header()
    x, y, z, anchor_qf, distance, distance_qf = reader.float64_array(6)
    return AnchorMeasurement(anchor_id, x, y, z, distance, anchor_qf, distance_qf)


def decode_anchor_array(data: bytes) -> AnchorArray:
    reader = CdrReader(data)
    stamp, _ = reader.header()
    count = reader.uint32()
    return AnchorArray(stamp, [_read_anchor(reader) for _ in range(count)])


def decode_tag(data: bytes) -> TagPose:
    reader = CdrReader(data)
    stamp, _ = reader.header()
    x, y, z, quality = reader.float64_array(4)
    return TagPose(stamp, x, y, z, quality, reader.int32())


def yaw_from_quaternion(qx: float, qy: float, qz: float, qw: float) -> float:
    return math.atan2(2.0 * (qw * qz + qx * qy), 1.0 - 2.0 * (qy * qy + qz * qz))


def decode_odometry(data: bytes) -> Pose2D:
    reader = CdrReader(data)
    stamp, _ = reader.header()
    reader.string()  # child_frame_id
    x, y, _ = reader.float64_array(3)
    qx, qy, qz, qw = reader.float64_array(4)
    return Pose2D(stamp, x, y, yaw_from_quaternion(qx, qy, qz, qw))


def decode_joint_state(data: bytes) -> WheelState:
    reader = CdrReader(data)
    stamp, _ = reader.header()
    reader.string_sequence()  # joint names
    position = reader.float64_sequence()
    velocity = reader.float64_sequence()
    return WheelState(stamp, position, velocity)
