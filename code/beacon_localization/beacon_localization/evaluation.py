"""Time matching, frame alignment and error metrics."""

from dataclasses import dataclass

import numpy as np

from .trajectories import Trajectory


@dataclass
class ErrorStats:
    name: str
    samples: int
    mean: float
    rmse: float
    median: float
    p95: float
    max: float


def sample_at(traj: Trajectory, times: np.ndarray, max_gap: float):
    """Positions of traj at given times. Linear interpolation between samples
    closer than max_gap, nearest sample otherwise. Returns (valid_mask, xy)."""
    idx = np.clip(np.searchsorted(traj.t, times), 1, len(traj.t) - 1)
    before, after = traj.t[idx - 1], traj.t[idx]
    span = after - before
    weight = np.clip((times - before) / np.where(span > 0, span, 1.0), 0.0, 1.0)
    interpolated = traj.xy[idx - 1] + weight[:, None] * (traj.xy[idx] - traj.xy[idx - 1])
    nearest = np.where(np.abs(times - before) <= np.abs(times - after), idx - 1, idx)
    xy = np.where((span <= max_gap)[:, None], interpolated, traj.xy[nearest])
    gap = np.abs(times - traj.t[nearest])
    return gap <= max_gap, xy


def rigid_transform_2d(source: np.ndarray, target: np.ndarray):
    """Least-squares R, p with target ~ R @ source + p (Kabsch, no scaling)."""
    src_mean, tgt_mean = source.mean(axis=0), target.mean(axis=0)
    cov = (source - src_mean).T @ (target - tgt_mean)
    u_mat, _, vt_mat = np.linalg.svd(cov)
    sign = np.sign(np.linalg.det(vt_mat.T @ u_mat.T))
    rotation = vt_mat.T @ np.diag([1.0, sign]) @ u_mat.T
    return rotation, tgt_mean - rotation @ src_mean


def align_to(traj: Trajectory, reference: Trajectory, max_gap: float) -> Trajectory:
    """Expresses an odometry trajectory in the global frame of the reference."""
    mask, xy = sample_at(traj, reference.t, max_gap)
    rotation, offset = rigid_transform_2d(xy[mask], reference.xy[mask])
    aligned = traj.xy @ rotation.T + offset
    return Trajectory(traj.name, traj.t, aligned, "global (aligned)")


def errors_against(traj: Trajectory, reference: Trajectory, max_gap: float):
    """Horizontal distance to the reference at reference times."""
    mask, xy = sample_at(traj, reference.t, max_gap)
    return reference.t[mask], np.linalg.norm(xy[mask] - reference.xy[mask], axis=1)


def error_stats(name: str, errors: np.ndarray) -> ErrorStats:
    if len(errors) == 0:
        return ErrorStats(name, 0, *([float("nan")] * 5))
    return ErrorStats(
        name, len(errors), float(np.mean(errors)), float(np.sqrt(np.mean(errors**2))),
        float(np.median(errors)), float(np.percentile(errors, 95)), float(np.max(errors)),
    )


def static_spread(traj: Trajectory, t_end: float) -> float:
    """RMS distance to the mean position while the robot stands still [m]."""
    xy = traj.xy[traj.t <= t_end]
    if len(xy) < 2:
        return float("nan")
    return float(np.sqrt(np.mean(np.sum((xy - xy.mean(axis=0)) ** 2, axis=1))))
