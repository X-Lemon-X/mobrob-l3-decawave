"""ROS 2 node: live matplotlib view of all localization methods.

  ros2 run beacon_localization live_plot --ros-args -p robot:=pioneer4

Computes everything itself (beacon LS and the three wheel odometries), so it
does not need beacon_node. ROS runs in a background thread, the plot in the
main thread. Close the window or press Ctrl+C to stop.
"""

import math
import threading

import rclpy
from decawave_msgs.msg import AnchorArray, Tag
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException, SingleThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import JointState

from .beacon_localizer import BeaconLocalizer
from .config import AppConfig
from .live_view import BEACON, ROBOT_ODOM, TAG_POSE, WHEEL_ODOMS, LiveData, LiveView
from .messages import decode_anchor_array, decode_joint_state, decode_odometry, decode_tag
from .odometry import EncoderOdometry, VelocityOdometry


def _to_start_frame(pose, start) -> tuple:
    """Robot odom pose relative to its first pose (subtract, rotate by -theta0)."""
    dx, dy = pose.x - start.x, pose.y - start.y
    c, s = math.cos(start.theta), math.sin(start.theta)
    return (c * dx + s * dy, -s * dx + c * dy)


class LivePlotNode(Node):
    def __init__(self):
        super().__init__("live_plot")
        self.robot = self.declare_parameter("robot", "pioneer4").value
        self.config = self._load_config()
        self.lock = threading.Lock()
        self.data = LiveData()
        self.data.global_paths = {TAG_POSE: [], BEACON: []}
        self.data.odom_paths = {name: [] for name in (ROBOT_ODOM, *WHEEL_ODOMS)}
        self.localizer = BeaconLocalizer(self.config.localization)
        self.odometries = self._create_odometries()
        self.reference = None
        self.odom_start = None
        self.t0 = None
        self._subscribe()

    def _load_config(self) -> AppConfig:
        config = AppConfig()
        loc = config.localization
        loc.mode = self.declare_parameter("mode", loc.mode).value
        loc.tag_height = self.declare_parameter("tag_height", loc.tag_height).value
        return config

    def _create_odometries(self) -> dict:
        cfg = self.config.odometry
        ticks, calibrated, velocity = WHEEL_ODOMS
        return {
            ticks: EncoderOdometry(cfg),
            calibrated: EncoderOdometry(cfg, cfg.tick_calibration),
            velocity: VelocityOdometry(cfg),
        }

    def _subscribe(self) -> None:
        r = self.robot  # raw=True: decoded from bytes, see node.py
        self.create_subscription(AnchorArray, f"/{r}/tag_status", self.on_status, 10, raw=True)
        self.create_subscription(Tag, f"/{r}/tag_pose", self.on_tag, 10, raw=True)
        self.create_subscription(JointState, f"/{r}/joint_states", self.on_joints, 10, raw=True)
        self.create_subscription(Odometry, f"/{r}/odom", self.on_odom, 10, raw=True)

    def _elapsed(self, stamp: float) -> float:
        if self.t0 is None:
            self.t0 = stamp
        return stamp - self.t0

    def on_status(self, raw: bytes) -> None:
        msg = decode_anchor_array(raw)
        fix = self.localizer.process(msg)
        with self.lock:
            for a in msg.anchors:
                self.data.anchors[a.anchor_id] = (a.x, a.y)
            if fix is None:
                return
            self.data.global_paths[BEACON].append((fix.x, fix.y))
            self.data.status = f"beacon x={fix.x:6.3f} y={fix.y:6.3f} anchors={fix.anchor_count}"
            if self.reference is not None:
                d = math.hypot(fix.x - self.reference.x, fix.y - self.reference.y)
                self.data.errors.append((self._elapsed(fix.stamp), d))
                self.data.status += f" | tag_pose x={self.reference.x:6.3f} y={self.reference.y:6.3f} | d={d:.3f} m"

    def on_tag(self, raw: bytes) -> None:
        tag = decode_tag(raw)
        with self.lock:
            path = self.data.global_paths[TAG_POSE]
            if not path or path[-1] != (tag.x, tag.y):
                path.append((tag.x, tag.y))
            self.reference = tag

    def on_joints(self, raw: bytes) -> None:
        msg = decode_joint_state(raw)
        with self.lock:
            for name, odometry in self.odometries.items():
                pose = odometry.update(msg)
                self.data.odom_paths[name].append((pose.x, pose.y))

    def on_odom(self, raw: bytes) -> None:
        pose = decode_odometry(raw)
        with self.lock:
            if self.odom_start is None:
                self.odom_start = pose
            self.data.odom_paths[ROBOT_ODOM].append(_to_start_frame(pose, self.odom_start))

    def snapshot(self) -> LiveData:
        with self.lock:
            return LiveData(
                anchors=dict(self.data.anchors),
                global_paths={k: list(v) for k, v in self.data.global_paths.items()},
                odom_paths={k: list(v) for k, v in self.data.odom_paths.items()},
                errors=list(self.data.errors),
                status=self.data.status,
            )


def _spin(executor) -> None:
    try:
        executor.spin()
    except ExternalShutdownException:
        pass


def main(args=None):
    rclpy.init(args=args)
    node = LivePlotNode()
    period = node.declare_parameter("refresh_period", 0.2).value
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    threading.Thread(target=_spin, args=(executor,), daemon=True).start()
    view = LiveView(node.robot)
    try:
        while rclpy.ok() and view.is_open():
            view.update(node.snapshot())
            view.pause(period)
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
