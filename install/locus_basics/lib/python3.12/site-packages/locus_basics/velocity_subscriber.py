import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class VelocitySubscriber(Node):
    def __init__(self):
        super().__init__('velocity_subscriber')
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.velocity_callback,
            10
        )

    def velocity_callback(self, msg: Twist):
        # Differential drive kinematics:
        # Convert linear + angular velocity to individual wheel speeds
        # L = 0.25m = half the wheel base (distance between wheels / 2)
        L = 0.25
        left_wheel  = msg.linear.x - (msg.angular.z * L)
        right_wheel = msg.linear.x + (msg.angular.z * L)

        self.get_logger().info(
            f'Left wheel: {left_wheel:.3f} m/s | '
            f'Right wheel: {right_wheel:.3f} m/s'
        )

def main(args=None):
    rclpy.init(args=args)
    node = VelocitySubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
