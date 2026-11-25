"""Offline analysis of lab bags: python3 -m beacon_localization.analyze BAG [BAG ...]"""

import argparse
import os

import numpy as np

from .bag_reader import BagData, read_bag
from .config import AppConfig
from .evaluation import align_to, error_stats, errors_against, static_spread
from .plots import plot_errors, plot_trajectories
from .trajectories import all_trajectories

REFERENCE = "tag_pose (built-in)"


def _anchors(bag: BagData) -> list:
    seen = {a.anchor_id: (a.anchor_id, a.x, a.y) for m in bag.tag_status for a in m.anchors}
    return sorted(seen.values())


def _start_of_motion(bag: BagData) -> float:
    for msg in bag.joint_states:
        if any(abs(v) > 0.0 for v in msg.velocity):
            return msg.stamp
    return bag.joint_states[-1].stamp


def _global_trajectories(bag: BagData, config: AppConfig) -> dict:
    trajectories = all_trajectories(bag, config)
    reference, gap = trajectories[REFERENCE], config.evaluation.max_sync_gap
    return {
        name: align_to(t, reference, gap) if t.frame == "odom" else t
        for name, t in trajectories.items()
    }


def _fmt(value: float) -> str:
    return "n/a" if np.isnan(value) else f"{value:.3f}"


def _table(rows: list, header: list) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def _stats_rows(errors: dict) -> list:
    rows = []
    for name, (_, values) in errors.items():
        s = error_stats(name, values)
        rows.append([name, s.samples] + [_fmt(v) for v in (s.mean, s.rmse, s.median, s.p95, s.max)])
    return rows


def _info_rows(trajectories: dict, still_until: float) -> list:
    rows = []
    for name, t in trajectories.items():
        closure = float(np.linalg.norm(t.xy[-1] - t.xy[0]))
        rate = len(t.t) / max(t.t[-1] - t.t[0], 1e-9)
        spread = static_spread(t, still_until)
        rows.append([name, len(t.t), f"{rate:.1f}", _fmt(spread), f"{closure:.3f}"])
    return rows


def _bag_report(name: str, bag: BagData, trajectories: dict, errors: dict) -> str:
    still_until = _start_of_motion(bag)
    still_for = still_until - bag.joint_states[0].stamp
    return "\n\n".join([
        f"## {name}",
        f"![trajectories]({name}_xy.png)\n\n![errors]({name}_error.png)",
        "Distance to `tag_pose` [m] (odometry aligned to `tag_pose` by a best-fit rigid transform):",
        _table(_stats_rows(errors), ["method", "samples", "mean", "RMSE", "median", "p95", "max"]),
        f"Static spread = RMS distance to the mean position before the robot starts "
        f"moving ({still_for:.1f} s). Closure = |end - start|.",
        _table(_info_rows(trajectories, still_until),
               ["method", "samples", "rate [Hz]", "static spread [m]", "closure [m]"]),
    ])


def analyze_bag(name: str, bag: BagData, config: AppConfig) -> str:
    trajectories = _global_trajectories(bag, config)
    reference, gap = trajectories[REFERENCE], config.evaluation.max_sync_gap
    errors = {
        n: errors_against(t, reference, gap) for n, t in trajectories.items() if n != REFERENCE
    }
    out_dir = config.evaluation.output_dir
    plot_trajectories(trajectories, _anchors(bag), name, os.path.join(out_dir, f"{name}_xy.png"))
    plot_errors(errors, reference.t[0], name, os.path.join(out_dir, f"{name}_error.png"))
    return _bag_report(name, bag, trajectories, errors)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bags", nargs="+", help="bag directories (or .db3 files)")
    parser.add_argument("--out", default=None, help="directory for figures and results.md")
    parser.add_argument("--mode", choices=["2d", "3d"], default=None)
    parser.add_argument("--tag-height", type=float, default=None, help="[m], used in 2d mode")
    parser.add_argument("--loss", default=None, help="linear | soft_l1 | huber | cauchy")
    return parser.parse_args()


def build_config(args) -> AppConfig:
    config = AppConfig()
    overrides = {"mode": args.mode, "tag_height": args.tag_height, "robust_loss": args.loss}
    for key, value in overrides.items():
        if value is not None:
            setattr(config.localization, key, value)
    if args.out:
        config.evaluation.output_dir = args.out
    return config


def write_report(named_bags: list, config: AppConfig) -> str:
    """named_bags: [(name, BagData)]. Saves figures + results.md, returns the text."""
    os.makedirs(config.evaluation.output_dir, exist_ok=True)
    sections = [analyze_bag(name, bag, config) for name, bag in named_bags]
    header = f"# Results\n\nLocalization config: `{config.localization}`"
    report = "\n\n".join([header] + sections) + "\n"
    path = os.path.join(config.evaluation.output_dir, "results.md")
    with open(path, "w") as handle:
        handle.write(report)
    return report + f"\nWritten {path}"


def main():
    args = parse_args()
    config = build_config(args)
    named = [(os.path.basename(os.path.normpath(p)), read_bag(p)) for p in args.bags]
    print(write_report(named, config))


if __name__ == "__main__":
    main()
