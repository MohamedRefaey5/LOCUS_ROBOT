import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from geometry_msgs.msg import Twist, TwistStamped

class CmdVelRelay(Node):
    def __init__(self):
        super().__init__('cmd_vel_relay')

        # Tell this node to use simulation time
        self.set_parameters([
            rclpy.parameter.Parameter(
                'use_sim_time',
                rclpy.Parameter.Type.BOOL,
                True
            )
        ])

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

        self.get_logger().info('cmd_vel_relay ready')

    def callback(self, msg):
        stamped = TwistStamped()
        # Use simulation clock — CRITICAL for ros2_control with use_sim_time
        stamped.header.stamp = self.get_clock().now().to_msg()
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
