import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class VelocityPublisher(Node):
    def __init__(self):
        # Register this node with the DDS network under the name 'velocity_publisher'
        # Other nodes can now discover it via ros2 node list
        super().__init__('velocity_publisher')

        # Create a publisher on the /cmd_vel topic
        # Twist is the standard velocity message type for mobile robots
        # 10 = queue depth: if subscriber is slow, keep last 10 messages
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)

        # Timer: calls send_velocity every 0.5 seconds
        # ROS 2 manages this internally — not Python threading
        self.timer = self.create_timer(0.5, self.send_velocity)
        self.get_logger().info('Velocity publisher started')

    def send_velocity(self):
        msg = Twist()
        # For differential drive: only linear.x and angular.z matter
        # linear.x  = forward speed in m/s (positive = forward)
        # angular.z = rotation speed in rad/s (positive = left turn)
        msg.linear.x = 0.2
        msg.angular.z = 0.1
        self.publisher_.publish(msg)
        self.get_logger().info(
            f'Publishing: linear={msg.linear.x}, angular={msg.angular.z}'
        )

def main(args=None):
    rclpy.init(args=args)         # Initialize DDS communication
    node = VelocityPublisher()
    rclpy.spin(node)              # Event loop — blocks here, fires callbacks
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
