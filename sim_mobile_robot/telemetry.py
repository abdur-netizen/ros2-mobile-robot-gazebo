import rclpy
from rclpy.node import Node
from std_msgs.msg import String # Topic message type

class TelemetryPublisher(Node):

    def __init__(self):
        super().__init__('telemetry_publisher')
        
        # Create a topic publisher broadcasting status strings
        self.publisher_ = self.create_publisher(String, '/robot_telemetry', 10)
        self.timer = self.create_timer(2.0, self.publish_status) # Every 2 seconds
        self.counter = 0

    def publish_status(self):
        msg = String()
        msg.data = f'Robot Operational | Heartbeat #{self.counter}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Broadcasting Telemetry: "{msg.data}"')
        self.counter += 1

def main(args=None):
    rclpy.init(args=args)
    node = TelemetryPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
