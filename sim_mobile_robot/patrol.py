import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from geometry_msgs.msg import Twist

# ROS 2 default action interface for rotation/patrol goals
from turtlesim.action import RotateAbsolute 

class PatrolActionServer(Node):

    def __init__(self):
        super().__init__('patrol_action_server')
        
        # Create Action Server
        self._action_server = ActionServer(
            self,
            RotateAbsolute,
            '/patrol_routine',
            self.execute_patrol_callback
        )
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('Patrol Action Server initialized.')

    def execute_patrol_callback(self, goal_handle):
        self.get_logger().info('Executing patrol mission...')
        
        feedback_msg = RotateAbsolute.Feedback()
        twist = Twist()
        twist.angular.z = 0.5 # Rotate in circle
        
        # Execute long-running patrol loop (5 iterations)
        for i in range(1, 6):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Patrol Mission Canceled!')
                return RotateAbsolute.Result()

            self.cmd_pub.publish(twist)
            feedback_msg.remaining = float(5 - i) # Send feedback update
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f'Patrol Progress: Step {i}/5 completed')
            time.sleep(1.0) # Simulate time passing during flight/patrol

        # Stop robot after patrol completes
        twist.angular.z = 0.0
        self.cmd_pub.publish(twist)

        goal_handle.succeed()
        result = RotateAbsolute.Result()
        self.get_logger().info('Patrol Mission Accomplished!')
        return result

def main(args=None):
    rclpy.init(args=args)
    node = PatrolActionServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
