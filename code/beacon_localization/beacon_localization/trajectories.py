"""Builds comparable trajectories (time, x, y) for every method in a bag."""

from dataclasses import dataclass

import numpy as np

from .bag_reader import BagData
from .beacon_localizer import BeaconLocalizer
from .config import AppConfig
from .odometry import EncoderOdometry, VelocityOdometry


@dataclass
class Trajectory:
    name: str
    t: np.ndarray
    xy: np.ndarray  # (N, 2)
    frame: str  # "global" or "odom"


def _make(name: str, rows: list, frame: str) -> Trajectory:
    data = np.array(rows, dtype=float).reshape(-1, 3)
    return Trajectory(name, data[:, 0], data[:, 1:], frame)


def beacon_trajectory(bag: BagData, config: AppConfig) -> Trajectory:
    localizer = BeaconLocalizer(config.localization)
    fixes = [localizer.process(msg) for msg in bag.tag_status]
    rows = [(f.stamp, f.x, f.y) for f in fixes if f is not None]
    return _make(f"beacon LS ({config.localization.mode})", rows, "global")


def tag_pose_trajectory(bag: BagData, config: AppConfig) -> Trajectory:
    """Built-in estimate; repeated (unchanged) samples are dropped."""
    rows, last = [], None
    for msg in bag.tag_pose:
        key = (msg.x, msg.y, msg.z)
        if key != last and msg.quality >= config.evaluation.min_reference_quality:
            rows.append((msg.stamp, msg.x, msg.y))
        last = key
    return _make("tag_pose (built-in)", rows, "global")


def robot_odom_trajectory(bag: BagData) -> Trajectory:
    return _make("odom (robot)", [(p.stamp, p.x, p.y) for p in bag.odom], "odom")


def _wheel_odom_trajectory(bag: BagData, name: str, odometry) -> Trajectory:
    poses = [odometry.update(msg) for msg in bag.joint_states]
    return _make(name, [(p.stamp, p.x, p.y) for p in poses], "odom")


def wheel_odom_trajectories(bag: BagData, config: AppConfig) -> list:
    """Lab 2 odometry: ticks (nominal and calibrated radius) and wheel velocities."""
    cfg = config.odometry
    return [
        _wheel_odom_trajectory(bag, "odom (ours, ticks)", EncoderOdometry(cfg)),
        _wheel_odom_trajectory(
            bag, "odom (ours, ticks calibrated)", EncoderOdometry(cfg, cfg.tick_calibration)
        ),
        _wheel_odom_trajectory(bag, "odom (ours, velocity)", VelocityOdometry(cfg)),
    ]


def all_trajectories(bag: BagData, config: AppConfig) -> dict:
    trajectories = [
        tag_pose_trajectory(bag, config),
        beacon_trajectory(bag, config),
        robot_odom_trajectory(bag),
        *wheel_odom_trajectories(bag, config),
    ]
    return {t.name: t for t in trajectories}
