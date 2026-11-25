import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import String, Header
from nav_msgs.msg import Odometry 
from sensor_msgs.msg import JointState
from builtin_interfaces.msg import Time

from abc import ABC, abstractmethod
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from time import sleep

loop_count = 25  # drawing loop iterations
beam_half_angle = 7.5  # half of angular beam width


gear_ratio = 38.3
encoder = 4 * 500 * gear_ratio # tics per rotaion
wheel_radius =  195 / 2.0
grubosc_kola = 50
wheel_distance = 375 - grubosc_kola 

class ReadPosVel():
    def __init__(self):
        pass

    @abstractmethod
    def update(self,val,time:Time):
        pass

    @abstractmethod
    def get_velocity(self) -> float:
        pass

    @abstractmethod
    def get_position(self) -> float:
        pass

def wrap_angle(a):
    return math.atan2(math.sin(a), math.cos(a))

def time_to_double(ti:Time):
    return ti.sec +  (ti.nanosec / 1000000000.0)

class TicksReadPosVel(ReadPosVel):
    def __init__(self):
        self.prev_pos = 0
        self.prev_time = 0
        self.pos = 0.0
        self.vel = 0.0
        self.ticks = None

    def update(self,val,time:Time):
        val = int(val)
        if self.ticks is None:
            self.ticks = val
            self.prev_time = time_to_double(time)
            return

        delta = ((val-self.ticks + 32768) % 65536) - 32768 
        self.pos += delta *  2 * math.pi /  encoder
        
        self.ticks = val

        time_diff = time_to_double(time) - self.prev_time 
        
        diff = self.pos - self.prev_pos
        self.vel = diff / time_diff

        self.prev_pos = self.pos 
        self.prev_time = time_to_double(time)


    def get_velocity(self) -> float:
        return self.vel

    def get_position(self) -> float:
        return self.pos


class VelReadPosVel(ReadPosVel):
    def __init__(self):
        pass
        self.prev_vel = None
        self.prev_time = 0
        self.pos = 0.0
        self.vel = 0.0
    
    def update(self,val,time:Time):
        if self.prev_vel is None:
            self.prev_vel = val
            self.prev_time = time_to_double(time)
            return

        self.vel =  val / wheel_radius
        diff_time = time_to_double(time) - self.prev_time

        self.pos += self.vel * diff_time

        self.prev_vel = val
        self.prev_time = time_to_double(time)


    def get_velocity(self) -> float:
        return self.vel

    def get_position(self) -> float:
        return self.pos

class DiffDrive:
    def __init__(self, wheel_radius, wheel_distance):
        self.wheel_radius = wheel_radius
        self.wheel_distance = wheel_distance
        
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0  
        
        self.time = None
        self.prev_angle_l = 0.0
        self.prev_angle_r = 0.0

    def update(self, left:ReadPosVel, right:ReadPosVel, time):
        time = time_to_double(time)
        current_angle_l = left.get_position()
        current_angle_r = right.get_position()
        
        if self.time is None:
            self.prev_angle_l = current_angle_l
            self.prev_angle_r = current_angle_r
            self.time = time
            return


        delta_angle_l = current_angle_l - self.prev_angle_l
        delta_angle_r = current_angle_r - self.prev_angle_r

        ds_l = self.wheel_radius * delta_angle_l
        ds_r = self.wheel_radius * delta_angle_r

        ds = (ds_r + ds_l) / 2.0
        d_theta = (ds_r - ds_l) / self.wheel_distance

        self.x += ds * math.cos(self.theta + d_theta / 2.0)
        self.y += ds * math.sin(self.theta + d_theta / 2.0)
        self.theta += d_theta

        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))

        self.prev_angle_l = current_angle_l
        self.prev_angle_r = current_angle_r
        self.time = time

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.sub = self.create_subscription(
            Odometry, '/pp5/odom', self.callback_odom, 10
        )

        self.sub2 = self.create_subscription(
            JointState, '/pp5/joint_states', self.callback_encoder, 10
        )
        self.pos_vel_left = TicksReadPosVel()
        self.pos_vel_right = TicksReadPosVel()
        self.vel_left = VelReadPosVel()
        self.vel_right = VelReadPosVel()
        self.beg = True
        self.odom = DiffDrive(wheel_radius/1000.0,wheel_distance/1000.0)      # from encoder ticks
        self.odom_vel = DiffDrive(wheel_radius/1000.0,wheel_distance/1000.0)  # from wheel velocities
        self.msg = Odometry()
        self.first_msg = None
        self.path_ticks = []
        self.path_vel = []
        self.path_robot = []


    def yaw_from_quaternion(self,quaternion):
        """
        Converts quaternion (w in last place) to yaw angle
        quaternion = [x, y, z, w]

        modified from
        https://gist.github.com/salmagro/2e698ad4fbf9dae40244769c5ab74434
        """
        x = quaternion.x
        y = quaternion.y
        z = quaternion.z
        w = quaternion.w

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        return yaw


    def callback_encoder(self,msg:JointState):

        self.pos_vel_left.update(msg.position[0],msg.header.stamp)
        self.pos_vel_right.update(msg.position[1],msg.header.stamp)
        
        self.vel_left.update(msg.velocity[0],msg.header.stamp)
        self.vel_right.update(msg.velocity[1],msg.header.stamp)

        self.odom.update(self.pos_vel_left,self.pos_vel_right,msg.header.stamp)
        self.odom_vel.update(self.vel_left,self.vel_right,msg.header.stamp)

        print(f"LEFT pos: {self.pos_vel_left.get_position():.2f},  vel: {self.pos_vel_left.get_velocity():.2f}  | pos: {self.vel_left.get_position():.2f},  vel: {self.vel_left.get_velocity():.2f}")
        print(f"RIGHT pos: {self.pos_vel_right.get_position():.2f},  vel: {self.pos_vel_right.get_velocity():.2f}  | pos: {self.vel_right.get_position():.2f},  vel: {self.vel_right.get_velocity():.2f}")
        print(f"ODOM TICKS x:{self.odom.x:8.3f}  y:{self.odom.y:8.3f}  theta:{self.odom.theta:7.3f}")
        print(f"ODOM VEL   x:{self.odom_vel.x:8.3f}  y:{self.odom_vel.y:8.3f}  theta:{self.odom_vel.theta:7.3f}")

        self.path_ticks.append((self.odom.x, self.odom.y))
        self.path_vel.append((self.odom_vel.x, self.odom_vel.y))

        if self.first_msg is not None:
            x, y, th = self.robot_odom_in_start_frame()
            print(f"ROBOT ODOM x:{x:8.3f}  y:{y:8.3f}  theta:{th:7.3f}")
            self.path_robot.append((x, y))

            for name, est in (("TICKS", self.odom), ("VEL  ", self.odom_vel)):
                ex, ey = est.x - x, est.y - y
                eth = wrap_angle(est.theta - th)
                print(f"ERR {name}  dx:{ex:8.3f}  dy:{ey:8.3f}  dist:{math.hypot(ex, ey):7.3f} m  dtheta:{eth:7.3f} rad ({math.degrees(eth):6.1f} deg)")
        print()

    def robot_odom_in_start_frame(self):
        """Robot odom pose relative to its first message: subtract start pose and rotate by -theta0."""
        th0 = self.yaw_from_quaternion(self.first_msg.pose.pose.orientation)
        dx = self.msg.pose.pose.position.x - self.first_msg.pose.pose.position.x
        dy = self.msg.pose.pose.position.y - self.first_msg.pose.pose.position.y
        x = math.cos(th0) * dx + math.sin(th0) * dy
        y = -math.sin(th0) * dx + math.cos(th0) * dy
        th = wrap_angle(self.yaw_from_quaternion(self.msg.pose.pose.orientation) - th0)
        return x, y, th

    def plot_paths(self, filename="odom_paths.png"):
        if not self.path_ticks:
            print("No joint_states received - nothing to plot")
            return
        fig, ax = plt.subplots(figsize=(8, 8))
        for path, label, style in ((self.path_robot, "robot /odom", "k-"),
                                   (self.path_ticks, "ours: ticks", "r--"),
                                   (self.path_vel, "ours: velocity", "b:")):
            if path:
                xs, ys = zip(*path)
                ax.plot(xs, ys, style, label=label, linewidth=2)
        ax.plot(0, 0, "go", label="start")
        ax.set_xlabel("x [m]")
        ax.set_ylabel("y [m]")
        ax.set_title("Odometry paths (start frame)")
        ax.axis("equal")
        ax.grid(True)
        ax.legend()
        fig.savefig(filename, dpi=150)
        print(f"Figure saved to {filename}")
        plt.show()





    def callback_odom(self,msg:Odometry):
        if self.first_msg  is None:
            self.first_msg = msg
        self.msg = msg
    


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    try:
        rclpy.spin(minimal_publisher)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        minimal_publisher.plot_paths()
        minimal_publisher.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()