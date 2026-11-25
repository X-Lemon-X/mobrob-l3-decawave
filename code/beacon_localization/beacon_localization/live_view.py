"""Matplotlib window for the live_plot node (runs in the main thread)."""

from dataclasses import dataclass, field

import matplotlib.pyplot as plt

from .styles import BEACON_STYLE, style_for as _style

TAG_POSE = "tag_pose (built-in)"
BEACON = "beacon LS"
ROBOT_ODOM = "odom (robot)"
WHEEL_ODOMS = ("odom (ours, ticks)", "odom (ours, ticks calibrated)", "odom (ours, velocity)")


@dataclass
class LiveData:
    """Snapshot of everything drawn; paths are lists of (x, y)."""

    anchors: dict = field(default_factory=dict)  # id -> (x, y)
    global_paths: dict = field(default_factory=dict)  # tag_pose, beacon LS
    odom_paths: dict = field(default_factory=dict)  # robot start frame
    errors: list = field(default_factory=list)  # (t, distance beacon - tag_pose)
    status: str = "waiting for data..."


class LiveView:
    """Three panels: global map, odometry in start frame, beacon error over time."""

    def __init__(self, robot: str):
        plt.ion()
        self.fig = plt.figure(f"live localization – {robot}", figsize=(14, 8))
        grid = self.fig.add_gridspec(2, 2, height_ratios=[3, 1])
        self.ax_map = self.fig.add_subplot(grid[0, 0])
        self.ax_odom = self.fig.add_subplot(grid[0, 1])
        self.ax_err = self.fig.add_subplot(grid[1, :])
        self._setup_axes()
        self.lines = self._create_lines()
        self.anchor_artists = []
        self.fig.tight_layout(rect=(0, 0, 1, 0.95))

    def _setup_axes(self) -> None:
        for ax, title in ((self.ax_map, "global frame (Decawave)"),
                          (self.ax_odom, "odometry (robot start frame)")):
            ax.set_title(title)
            ax.set_xlabel("x [m]")
            ax.set_ylabel("y [m]")
            ax.set_aspect("equal", adjustable="datalim")
            ax.grid(True)
        self.ax_err.set_xlabel("t [s]")
        self.ax_err.set_ylabel("beacon − tag_pose [m]")
        self.ax_err.grid(True)

    def _create_lines(self) -> dict:
        lines = {}
        for name in (TAG_POSE, BEACON):
            lines[name] = self.ax_map.plot([], [], label=name, **_style(name))[0]
        for name in (ROBOT_ODOM, *WHEEL_ODOMS):
            lines[name] = self.ax_odom.plot([], [], label=name, **_style(name))[0]
        lines["error"] = self.ax_err.plot([], [], **BEACON_STYLE)[0]
        self.ax_map.legend(loc="upper right")
        self.ax_odom.legend(loc="upper right")
        return lines

    def is_open(self) -> bool:
        return plt.fignum_exists(self.fig.number)

    def update(self, data: LiveData) -> None:
        self._draw_anchors(data.anchors)
        for name, path in {**data.global_paths, **data.odom_paths}.items():
            if path and name in self.lines:
                xs, ys = zip(*path)
                self.lines[name].set_data(xs, ys)
        if data.errors:
            ts, ds = zip(*data.errors)
            self.lines["error"].set_data(ts, ds)
        for ax in (self.ax_map, self.ax_odom, self.ax_err):
            ax.relim()
            ax.autoscale_view()
        self.fig.suptitle(data.status, fontsize=10, family="monospace")

    def _draw_anchors(self, anchors: dict) -> None:
        if len(self.anchor_artists) == 2 * len(anchors):
            return
        for artist in self.anchor_artists:
            artist.remove()
        self.anchor_artists = []
        for anchor_id, (x, y) in anchors.items():
            self.anchor_artists += self.ax_map.plot(x, y, "b^", markersize=10)
            self.anchor_artists.append(
                self.ax_map.annotate(anchor_id, (x, y), textcoords="offset points", xytext=(5, 5))
            )

    @staticmethod
    def pause(seconds: float) -> None:
        plt.pause(seconds)
