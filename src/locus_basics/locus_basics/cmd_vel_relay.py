import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped


class CmdVelRelay(Node):
    """
    Converts /cmd_vel (geometry_msgs/Twist) published by teleop_twist_keyboard
    to /diff_drive_controller/cmd_vel (geometry_msgs/TwistStamped) expected
    by ros2_control diff_drive_controller.

    Uses simulation time so timestamps match the controller's clock.
    """

    def __init__(self):
        super().__init__('cmd_vel_relay')


        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.callback,
            10
        )

        self.publisher = self.create_publisher(
            TwistStamped,
            '/diff_drive_controller/cmd_vel',
            10
        )

        self.get_logger().info(
            'cmd_vel_relay ready: '
            '/cmd_vel (Twist) -> /diff_drive_controller/cmd_vel (TwistStamped)'
        )

    def callback(self, msg: Twist):
        stamped = TwistStamped()
        # Use node clock — respects use_sim_time parameter
        stamped.header.stamp    = self.get_clock().now().to_msg()
        stamped.header.frame_id = 'base_footprint'
        stamped.twist.linear.x  = msg.linear.x
        stamped.twist.linear.y  = msg.linear.y
        stamped.twist.linear.z  = msg.linear.z
        stamped.twist.angular.x = msg.angular.x
        stamped.twist.angular.y = msg.angular.y
        stamped.twist.angular.z = msg.angular.z
        self.publisher.publish(stamped)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
