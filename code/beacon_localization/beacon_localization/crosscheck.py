"""Second reference: compare the UWB methods with wheel odometry.

Odometry does not depend on UWB, has no measurement gaps and (with the lab 2
calibration) drifts only a few cm on these short runs, so it shows time lag
and outliers of `tag_pose` that a comparison against `tag_pose` itself cannot.
"""

from dataclasses import dataclass

import numpy as np

from .config import EvaluationConfig
from .evaluation import rigid_transform_2d
from .trajectories import Trajectory


@dataclass
class CrossCheck:
    name: str
    samples: int
    rmse: float
    p95: float
    max: float
    best_lag: float  # [s] shift of odometry giving the lowest RMSE (> 0: method lags)
    rmse_at_best_lag: float


@dataclass
class Gap:
    start: float  # [s] since bag start
    duration: float
    odom_distance: float  # [m] driven during the gap


def _interpolate(traj: Trajectory, times: np.ndarray) -> np.ndarray:
    return np.c_[np.interp(times, traj.t, traj.xy[:, 0]), np.interp(times, traj.t, traj.xy[:, 1])]


def _aligned_errors(traj: Trajectory, odom: Trajectory, times: np.ndarray, xy: np.ndarray, lag: float):
    odom_xy = _interpolate(odom, times - lag)
    rotation, shift = rigid_transform_2d(odom_xy, xy)
    return np.linalg.norm(xy - (odom_xy @ rotation.T + shift), axis=1)


def crosscheck(traj: Trajectory, odom: Trajectory, config: EvaluationConfig) -> CrossCheck:
    margin = config.max_lag
    inside = (traj.t > odom.t[0] + margin) & (traj.t < odom.t[-1] - margin)
    times, xy = traj.t[inside], traj.xy[inside]
    errors = _aligned_errors(traj, odom, times, xy, 0.0)
    lags = np.arange(-margin, margin + 1e-9, config.lag_step)
    rmse = [np.sqrt(np.mean(_aligned_errors(traj, odom, times, xy, lag) ** 2)) for lag in lags]
    best = int(np.argmin(rmse))
    return CrossCheck(
        traj.name, len(times), float(np.sqrt(np.mean(errors**2))),
        float(np.percentile(errors, 95)), float(errors.max()), float(lags[best]), float(rmse[best]),
    )


def measurement_gaps(traj: Trajectory, odom: Trajectory, min_gap: float) -> list:
    """Intervals without a new fix, with the distance the robot drove meanwhile."""
    steps = np.linalg.norm(np.diff(odom.xy, axis=0), axis=1)
    gaps = []
    for i in np.where(np.diff(traj.t) > min_gap)[0]:
        start, end = traj.t[i], traj.t[i + 1]
        inside = (odom.t[1:] > start) & (odom.t[1:] <= end)
        gaps.append(Gap(start - odom.t[0], end - start, float(steps[inside].sum())))
    return gaps
