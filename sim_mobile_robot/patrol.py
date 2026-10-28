#!/usr/bin/env python3
"""Prototype patrol action server for the simulated mobile robot."""

import asyncio

import rclpy
from geometry_msgs.msg import Twist
from rclpy.action import ActionServer
from rclpy.node import Node
from turtlesim.action import RotateAbsolute


class PatrolActionServer(Node):
    """Demonstration action server that commands a short in-place rotation."""

    def __init__(self):
        super().__init__("patrol_action_server")
        self._action_server = ActionServer(
            self,
            RotateAbsolute,
            "/patrol_routine",
            self.execute_patrol_callback,
        )
        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.get_logger().info("Patrol Action Server initialized.")

    async def execute_patrol_callback(self, goal_handle):
        """Publish five short rotation commands and report action feedback.

        This is a demonstration only: the requested theta is not yet used to
        calculate a target angle or stop condition.
        """
        self.get_logger().info("Executing patrol mission...")
        twist = Twist()
        twist.angular.z = 0.5
        result = RotateAbsolute.Result()

        try:
            for step in range(1, 6):
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    self.get_logger().info("Patrol mission canceled.")
                    return result

                self.cmd_pub.publish(twist)
                feedback = RotateAbsolute.Feedback()
                # RotateAbsolute.Feedback defines the field 'delta'.
                # At 0.5 rad/s for roughly one second, the expected increment
                # is approximately 0.5 rad (simulation timing may vary).
                feedback.delta = 0.5
                goal_handle.publish_feedback(feedback)
                self.get_logger().info(
                    f"Patrol progress: step {step}/5"
                )
                await asyncio.sleep(1.0)

            goal_handle.succeed()
            self.get_logger().info("Patrol mission completed.")
            return result
        finally:
            # Stop even when the goal is canceled or the callback exits early.
            self.cmd_pub.publish(Twist())

    def destroy_node(self):
        self._action_server.destroy()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = PatrolActionServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
