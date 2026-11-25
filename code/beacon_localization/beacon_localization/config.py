"""All tunable parameters in one place."""

import math
from dataclasses import dataclass, field


@dataclass
class LocalizationConfig:
    """Parameters of the beacon (trilateration) localization."""

    mode: str = "2d"  # "2d": fixed tag height, "3d": z estimated too
    tag_height: float = 0.3  # [m] tag z used in "2d" mode
    max_anchor_z_margin: float = 0.05  # [m] "3d": tag must be this far below anchors
    robust_loss: str = "linear"  # scipy least_squares loss: linear, soft_l1, huber
    loss_scale: float = 0.1  # [m] residual scale for robust losses
    min_anchors: int = 3  # fewer anchors -> use previous estimate as initial guess
    min_anchors_with_prior: int = 2  # below this, no estimate is produced
    max_residual_rms: float = 0.5  # [m] reject solutions worse than this


@dataclass
class OdometryConfig:
    """Pioneer 3-DX wheel odometry parameters (values from lab 2)."""

    gear_ratio: float = 38.3
    encoder_lines: int = 500
    quadrature: int = 4
    counter_modulo: int = 65536  # encoder counter wraps at 16 bits
    wheel_radius: float = 0.0975  # [m]
    wheel_base: float = 0.325  # [m] distance between wheel contact points
    left_index: int = 0
    right_index: int = 1

    @property
    def ticks_per_rad(self) -> float:
        return self.quadrature * self.encoder_lines * self.gear_ratio / (2.0 * math.pi)


@dataclass
class EvaluationConfig:
    """How methods are compared."""

    min_reference_quality: float = 0.0  # tag_pose samples below are ignored
    max_sync_gap: float = 0.3  # [s] max time distance when matching samples
    output_dir: str = "results"


@dataclass
class AppConfig:
    localization: LocalizationConfig = field(default_factory=LocalizationConfig)
    odometry: OdometryConfig = field(default_factory=OdometryConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
