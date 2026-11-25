"""Differential-drive odometry from joint_states (both lab 2 versions)."""

import math
from typing import Optional

from .config import OdometryConfig
from .messages import Pose2D, WheelState


def wrap_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


class _DiffDriveOdometry:
    """Midpoint integration of wheel displacements; pose is in the robot start frame."""

    def __init__(self, config: OdometryConfig):
        self.config = config
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self._previous: Optional[WheelState] = None

    def _wheel_distances(self, msg: WheelState, previous: WheelState) -> tuple:
        raise NotImplementedError

    def update(self, msg: WheelState) -> Pose2D:
        if self._previous is not None:
            ds_left, ds_right = self._wheel_distances(msg, self._previous)
            ds = 0.5 * (ds_left + ds_right)
            d_theta = (ds_right - ds_left) / self.config.wheel_base
            self.x += ds * math.cos(self.theta + 0.5 * d_theta)
            self.y += ds * math.sin(self.theta + 0.5 * d_theta)
            self.theta = wrap_angle(self.theta + d_theta)
        self._previous = msg
        return Pose2D(msg.stamp, self.x, self.y, self.theta)


class EncoderOdometry(_DiffDriveOdometry):
    """Lab 2 version A: 16-bit encoder counters in joint_states.position."""

    def __init__(self, config: OdometryConfig, scale: float = 1.0):
        super().__init__(config)
        self.scale = scale

    def _tick_delta(self, now: float, before: float) -> float:
        half = self.config.counter_modulo // 2
        return ((int(now) - int(before) + half) % self.config.counter_modulo) - half

    def _wheel_distances(self, msg: WheelState, previous: WheelState) -> tuple:
        cfg = self.config
        metres_per_tick = self.scale * cfg.wheel_radius / cfg.ticks_per_rad
        left = self._tick_delta(msg.position[cfg.left_index], previous.position[cfg.left_index])
        right = self._tick_delta(msg.position[cfg.right_index], previous.position[cfg.right_index])
        return left * metres_per_tick, right * metres_per_tick


class VelocityOdometry(_DiffDriveOdometry):
    """Lab 2 version B: linear wheel speeds (mm/s) in joint_states.velocity."""

    def _wheel_distances(self, msg: WheelState, previous: WheelState) -> tuple:
        cfg = self.config
        dt = msg.stamp - previous.stamp
        left = msg.velocity[cfg.left_index] * cfg.velocity_to_mps * dt
        right = msg.velocity[cfg.right_index] * cfg.velocity_to_mps * dt
        return left, right
