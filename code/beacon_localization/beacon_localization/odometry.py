"""Differential-drive odometry from wheel encoder counters (joint_states)."""

import math
from typing import Optional

from .config import OdometryConfig
from .messages import Pose2D, WheelState


def wrap_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


class EncoderOdometry:
    """Integrates wheel rotations; pose is in the robot start frame."""

    def __init__(self, config: OdometryConfig):
        self.config = config
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self._previous: Optional[list] = None

    def _tick_delta(self, now: float, before: float) -> float:
        half = self.config.counter_modulo // 2
        return ((int(now) - int(before) + half) % self.config.counter_modulo) - half

    def _wheel_distances(self, position: list) -> tuple:
        cfg = self.config
        scale = cfg.wheel_radius / cfg.ticks_per_rad
        left = self._tick_delta(position[cfg.left_index], self._previous[cfg.left_index])
        right = self._tick_delta(position[cfg.right_index], self._previous[cfg.right_index])
        return left * scale, right * scale

    def update(self, msg: WheelState) -> Pose2D:
        if self._previous is not None:
            ds_left, ds_right = self._wheel_distances(msg.position)
            ds = 0.5 * (ds_left + ds_right)
            d_theta = (ds_right - ds_left) / self.config.wheel_base
            self.x += ds * math.cos(self.theta + 0.5 * d_theta)
            self.y += ds * math.sin(self.theta + 0.5 * d_theta)
            self.theta = wrap_angle(self.theta + d_theta)
        self._previous = list(msg.position)
        return Pose2D(msg.stamp, self.x, self.y, self.theta)
