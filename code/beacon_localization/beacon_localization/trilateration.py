"""Position from ranges to fixed anchors: linear LS + nonlinear LS refinement."""

from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.optimize import least_squares

from .config import LocalizationConfig


@dataclass
class Fix:
    """One position estimate."""

    stamp: float
    x: float
    y: float
    z: float
    residual_rms: float
    anchor_count: int


def linear_solution_2d(anchors: np.ndarray, ranges: np.ndarray, height: float):
    """Closed form x,y: subtract the first range equation from the others.

    (x-xi)^2 + (y-yi)^2 = ri^2 - (h-zi)^2 = qi
    => 2(xi-x0)x + 2(yi-y0)y = q0 - qi + xi^2 - x0^2 + yi^2 - y0^2
    """
    q = ranges**2 - (height - anchors[:, 2]) ** 2
    a_mat = 2.0 * (anchors[1:, :2] - anchors[0, :2])
    sq = np.sum(anchors[:, :2] ** 2, axis=1)
    b_vec = q[0] - q[1:] + sq[1:] - sq[0]
    solution, *_ = np.linalg.lstsq(a_mat, b_vec, rcond=None)
    return solution


def _residuals(params, anchors, ranges, fixed_height):
    z = params[2] if fixed_height is None else fixed_height
    point = np.array([params[0], params[1], z])
    return np.linalg.norm(anchors - point, axis=1) - ranges


class Trilaterator:
    """Stateful solver: keeps the previous fix as a prior for weak geometry."""

    def __init__(self, config: LocalizationConfig):
        self.config = config
        self.previous: Optional[Fix] = None

    def _initial_guess(self, anchors, ranges) -> Optional[np.ndarray]:
        cfg = self.config
        if len(ranges) >= cfg.min_anchors:
            xy = linear_solution_2d(anchors, ranges, cfg.tag_height)
            return np.array([xy[0], xy[1], cfg.tag_height])
        if self.previous is not None and len(ranges) >= cfg.min_anchors_with_prior:
            return np.array([self.previous.x, self.previous.y, self.previous.z])
        return None

    def _refine(self, guess, anchors, ranges):
        cfg = self.config
        if cfg.mode == "3d" and len(ranges) >= 3:
            z_max = float(np.min(anchors[:, 2])) - cfg.max_anchor_z_margin
            guess[2] = min(guess[2], z_max - 1e-3)
            result = least_squares(
                _residuals, guess, args=(anchors, ranges, None),
                bounds=([-np.inf, -np.inf, -np.inf], [np.inf, np.inf, z_max]),
                loss=cfg.robust_loss, f_scale=cfg.loss_scale,
            )
            return result.x, result.fun
        result = least_squares(
            _residuals, guess[:2], args=(anchors, ranges, cfg.tag_height),
            loss=cfg.robust_loss, f_scale=cfg.loss_scale,
        )
        return np.array([result.x[0], result.x[1], cfg.tag_height]), result.fun

    def solve(self, stamp: float, anchors: np.ndarray, ranges: np.ndarray) -> Optional[Fix]:
        """anchors: (N,3) positions [m], ranges: (N,) distances [m]."""
        guess = self._initial_guess(anchors, ranges)
        if guess is None:
            return None
        point, residuals = self._refine(guess, anchors, ranges)
        rms = float(np.sqrt(np.mean(residuals**2)))
        if rms > self.config.max_residual_rms:
            return None
        fix = Fix(stamp, float(point[0]), float(point[1]), float(point[2]), rms, len(ranges))
        self.previous = fix
        return fix
