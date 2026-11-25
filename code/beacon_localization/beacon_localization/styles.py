"""Line styles shared by the report plots and the live view (no backend set here)."""

STYLES = {
    "tag_pose (built-in)": dict(color="black", marker=".", linestyle="-", linewidth=1),
    "odom (robot)": dict(color="tab:green", linestyle="--", linewidth=1.5),
    "odom (ours, ticks)": dict(color="tab:orange", linestyle=":", linewidth=2),
    "odom (ours, ticks calibrated)": dict(color="tab:purple", linestyle="-.", linewidth=1.5),
    "odom (ours, velocity)": dict(color="tab:blue", linestyle="--", linewidth=1),
}
BEACON_STYLE = dict(color="tab:red", marker="x", linestyle="-", linewidth=1, markersize=4)


def style_for(name: str) -> dict:
    return STYLES.get(name, BEACON_STYLE)
