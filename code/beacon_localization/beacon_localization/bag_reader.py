"""Reads a ROS 2 sqlite3 bag without needing ROS or message packages."""

import glob
import os
import sqlite3
from dataclasses import dataclass

from .messages import (
    decode_anchor_array,
    decode_joint_state,
    decode_odometry,
    decode_tag,
)

DECODERS = {
    "decawave_msgs/msg/AnchorArray": decode_anchor_array,
    "decawave_msgs/msg/Tag": decode_tag,
    "nav_msgs/msg/Odometry": decode_odometry,
    "sensor_msgs/msg/JointState": decode_joint_state,
}


@dataclass
class BagData:
    """Decoded messages of one bag, grouped by topic suffix."""

    tag_status: list
    tag_pose: list
    odom: list
    joint_states: list


def _find_db3(bag_path: str) -> str:
    if os.path.isfile(bag_path):
        return bag_path
    files = sorted(glob.glob(os.path.join(bag_path, "*.db3")))
    if not files:
        raise FileNotFoundError(f"No .db3 file in {bag_path}")
    return files[0]


def _read_topic(conn, topic_id: int, decoder) -> list:
    rows = conn.execute(
        "SELECT data FROM messages WHERE topic_id=? ORDER BY timestamp", (topic_id,)
    )
    return [decoder(bytes(row[0])) for row in rows]


def read_bag(bag_path: str) -> BagData:
    conn = sqlite3.connect(_find_db3(bag_path))
    by_suffix = {}
    for topic_id, name, msg_type in conn.execute("SELECT id, name, type FROM topics"):
        if msg_type in DECODERS:
            suffix = name.rsplit("/", 1)[-1]
            by_suffix[suffix] = _read_topic(conn, topic_id, DECODERS[msg_type])
    conn.close()
    return BagData(
        tag_status=by_suffix.get("tag_status", []),
        tag_pose=by_suffix.get("tag_pose", []),
        odom=by_suffix.get("odom", []),
        joint_states=by_suffix.get("joint_states", []),
    )
