"""ROS 2 node: live beacon localization + encoder odometry + comparison.

Subscribes (prefix = parameter `robot`, e.g. pioneer4):
  /<robot>/tag_status    decawave_msgs/AnchorArray  (raw bytes, decoded by us)
  /<robot>/tag_pose      decawave_msgs/Tag          (reference)
  /<robot>/joint_states  sensor_msgs/JointState
  /<robot>/odom          nav_msgs/Odometry
Publishes:
  /<robot>/beacon_pose   geometry_msgs/PoseStamped  (our trilateration, frame `map`)
  /<robot>/encoder_odom  nav_msgs/Odometry          (our odometry, robot start frame)
On Ctrl+C it saves the plots and results.md for the recorded session.
"""

import math

import rclpy
from decawave_msgs.msg import AnchorArray, Tag
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState

from .bag_reader import BagData
from .beacon_localizer import BeaconLocalizer
from .config import AppConfig
from .messages import (
    decode_anchor_array,
    decode_joint_state,
    decode_odometry,
    decode_tag,
)
from .odometry import EncoderOdometry


class BeaconNode(Node):
    def __init__(self):
        super().__init__("beacon_localization")
        self.config = self._load_config()
        robot = self.declare_parameter("robot", "pioneer4").value
        self.localizer = BeaconLocalizer(self.config.localization)
        self.odometry = EncoderOdometry(self.config.odometry)
        self.recorded = BagData([], [], [], [])
        self.last_reference = None
        self._subscribe(robot)
        self.pose_pub = self.create_publisher(PoseStamped, f"/{robot}/beacon_pose", 10)
        self.odom_pub = self.create_publisher(Odometry, f"/{robot}/encoder_odom", 10)

    def _load_config(self) -> AppConfig:
        config = AppConfig()
        loc = config.localization
        loc.mode = self.declare_parameter("mode", loc.mode).value
        loc.tag_height = self.declare_parameter("tag_height", loc.tag_height).value
        loc.robust_loss = self.declare_parameter("robust_loss", loc.robust_loss).value
        out = self.declare_parameter("output_dir", config.evaluation.output_dir).value
        config.evaluation.output_dir = out
        return config

    def _subscribe(self, robot: str) -> None:
        # raw=True: we decode bytes ourselves, so field names of the installed
        # decawave_msgs package do not matter, only the type name.
        self.create_subscription(AnchorArray, f"/{robot}/tag_status", self.on_status, 10, raw=True)
        self.create_subscription(Tag, f"/{robot}/tag_pose", self.on_tag, 10, raw=True)
        self.create_subscription(JointState, f"/{robot}/joint_states", self.on_joints, 10, raw=True)
        self.create_subscription(Odometry, f"/{robot}/odom", self.on_odom, 10, raw=True)

    def on_status(self, data: bytes) -> None:
        msg = decode_anchor_array(data)
        self.recorded.tag_status.append(msg)
        fix = self.localizer.process(msg)
        if fix is None:
            return
        self.pose_pub.publish(self._pose_msg(fix))
        self.get_logger().info(self._describe(fix))

    def _describe(self, fix) -> str:
        text = f"beacon x={fix.x:6.3f} y={fix.y:6.3f} rms={fix.residual_rms:.3f} n={fix.anchor_count}"
        if self.last_reference is not None:
            ref = self.last_reference
            text += f" | tag_pose x={ref.x:6.3f} y={ref.y:6.3f} d={math.hypot(fix.x - ref.x, fix.y - ref.y):.3f}"
        return text

    def _pose_msg(self, fix) -> PoseStamped:
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "map"
        msg.pose.position.x, msg.pose.position.y, msg.pose.position.z = fix.x, fix.y, fix.z
        msg.pose.orientation.w = 1.0
        return msg

    def on_tag(self, data: bytes) -> None:
        self.last_reference = decode_tag(data)
        self.recorded.tag_pose.append(self.last_reference)

    def on_joints(self, data: bytes) -> None:
        msg = decode_joint_state(data)
        self.recorded.joint_states.append(msg)
        pose = self.odometry.update(msg)
        self.odom_pub.publish(self._odom_msg(pose))

    def _odom_msg(self, pose) -> Odometry:
        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "encoder_odom"
        msg.child_frame_id = "base_link"
        msg.pose.pose.position.x, msg.pose.pose.position.y = pose.x, pose.y
        msg.pose.pose.orientation.z = math.sin(pose.theta / 2.0)
        msg.pose.pose.orientation.w = math.cos(pose.theta / 2.0)
        return msg

    def on_odom(self, data: bytes) -> None:
        self.recorded.odom.append(decode_odometry(data))

    def save_results(self) -> None:
        from .analyze import write_report

        if min(len(v) for v in vars(self.recorded).values()) < 2:
            print("Not enough data received - no results saved")
            return
        print(write_report([("live", self.recorded)], self.config))


def main(args=None):
    rclpy.init(args=args)
    node = BeaconNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.save_results()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
