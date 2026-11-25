"""Figures for the report."""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .styles import style_for as _style  # noqa: E402


def plot_trajectories(trajectories: dict, anchors: list, title: str, path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 8))
    for anchor_id, x, y in anchors:
        ax.plot(x, y, "b^", markersize=10)
        ax.annotate(anchor_id, (x, y), textcoords="offset points", xytext=(5, 5))
    for traj in trajectories.values():
        ax.plot(traj.xy[:, 0], traj.xy[:, 1], label=traj.name, **_style(traj.name))
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title(title)
    ax.axis("equal")
    ax.grid(True)
    ax.legend()
    _save(fig, path)


def plot_errors(errors: dict, t0: float, title: str, path: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    for name, (times, values) in errors.items():
        ax.plot(times - t0, values, label=name, **_style(name))
    ax.set_xlabel("t [s]")
    ax.set_ylabel("distance to tag_pose [m]")
    ax.set_title(title)
    ax.grid(True)
    ax.legend()
    _save(fig, path)


def _save(fig, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
