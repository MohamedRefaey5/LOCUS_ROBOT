import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray

class DiffDriveNode(Node):
    def __init__(self):
        super().__init__('diff_drive_node')

        # Robot physical parameters — must match URDF
        self.wheel_radius = 0.1       # meters
        self.track_width  = 0.5       # meters (distance between left and right wheels)

        # Subscribe to cmd_vel
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        # Publish to ForwardCommandController
        # Order must match joints list in yaml:
        # [front_left, front_right, rear_left, rear_right]
        self.publisher = self.create_publisher(
            Float64MultiArray,
            '/forward_velocity_controller/commands',
            10
        )

        self.get_logger().info('diff_drive_node ready')

    def cmd_vel_callback(self, msg):
        # Differential drive kinematics
        # v = linear velocity, w = angular velocity
        v = msg.linear.x
        w = msg.angular.z

        # Convert to wheel velocities
        # left  = (v - w * track_width/2) / wheel_radius
        # right = (v + w * track_width/2) / wheel_radius
        left_vel  = (v - w * self.track_width / 2.0) / self.wheel_radius
        right_vel = (v + w * self.track_width / 2.0) / self.wheel_radius

        # Publish [front_left, front_right, rear_left, rear_right]
        cmd = Float64MultiArray()
        cmd.data = [left_vel, right_vel, left_vel, right_vel]
        self.publisher.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = DiffDriveNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
