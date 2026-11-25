"""Report figure: one trilateration step on a real message.

  python3 -m beacon_localization.example_figure BAG --index 60 --out ../../report/figures/trilateration_example.png
"""

import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .bag_reader import read_bag  # noqa: E402
from .beacon_localizer import BeaconLocalizer  # noqa: E402
from .config import LocalizationConfig  # noqa: E402
from .trilateration import linear_solution_2d  # noqa: E402

ZOOM_HALF = 0.6  # [m] half size of the zoomed panel


def _nth_full_fix(bag, config: LocalizationConfig, index: int):
    localizer, count = BeaconLocalizer(config), 0
    for msg in bag.tag_status:
        fix = localizer.process(msg)
        if fix is not None and len(msg.anchors) == 4:
            count += 1
            if count == index:
                return msg, fix
    raise ValueError(f"bag has fewer than {index} fixes with 4 anchors")


def _draw(ax, anchors, radii, fix, linear, reference, zoom: bool) -> None:
    for (x, y, _), rho, anchor_id in anchors:
        ax.add_patch(plt.Circle((x, y), rho, fill=False, color="tab:blue", alpha=0.6, lw=2 if zoom else 1))
        if not zoom:
            ax.plot(x, y, "b^", markersize=10)
            ax.annotate(anchor_id, (x, y), textcoords="offset points", xytext=(6, 6))
    ax.plot(*linear, "o", mfc="white", mec="tab:red", mew=2, markersize=9, label="linear LS (start)")
    ax.plot(*fix, "o", color="tab:red", markersize=8, label="nonlinear LS (result)")
    ax.plot(*reference, "ks", markersize=7, label="tag_pose (built-in)")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.4)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")


def make_figure(bag_path: str, index: int, out: str) -> None:
    config = LocalizationConfig()
    bag = read_bag(bag_path)
    msg, fix = _nth_full_fix(bag, config, index)
    positions = np.array([a.position for a in msg.anchors])
    ranges = np.array([a.distance for a in msg.anchors])
    radii = np.sqrt(ranges**2 - (config.tag_height - positions[:, 2]) ** 2)
    anchors = [(a.position, rho, a.anchor_id) for a, rho in zip(msg.anchors, radii)]
    linear = linear_solution_2d(positions, ranges, config.tag_height)
    ref = min(bag.tag_pose, key=lambda t: abs(t.stamp - msg.stamp))
    args = (anchors, radii, (fix.x, fix.y), linear, (ref.x, ref.y))

    fig, (room, zoom) = plt.subplots(1, 2, figsize=(13, 6.2))
    _draw(room, *args, zoom=False)
    room.set_xlim(-3.5, 9.5)
    room.set_ylim(-1.5, 10.5)
    room.add_patch(plt.Rectangle((fix.x - ZOOM_HALF, fix.y - ZOOM_HALF), 2 * ZOOM_HALF, 2 * ZOOM_HALF,
                                 fill=False, ls="--", color="tab:red"))
    room.set_title(f"range circles on the floor plane (h = {config.tag_height} m)")
    _draw(zoom, *args, zoom=True)
    zoom.set_xlim(fix.x - ZOOM_HALF, fix.x + ZOOM_HALF)
    zoom.set_ylim(fix.y - ZOOM_HALF, fix.y + ZOOM_HALF)
    zoom.set_title(f"zoom: residual RMS {fix.residual_rms * 100:.1f} cm")
    zoom.legend(loc="upper right")
    fig.tight_layout()
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bag")
    parser.add_argument("--index", type=int, default=60, help="n-th fix with 4 anchors")
    parser.add_argument("--out", default="trilateration_example.png")
    args = parser.parse_args()
    make_figure(args.bag, args.index, args.out)
    print(f"Written {args.out}")


if __name__ == "__main__":
    main()
