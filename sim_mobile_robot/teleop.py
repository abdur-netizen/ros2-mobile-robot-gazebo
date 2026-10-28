#!/usr/bin/env python3
"""Keyboard teleoperation for the simulated mobile robot.

Run from an interactive terminal with:
    ros2 run sim_mobile_robot keyboard_teleop

Controls: W/S drive forward/backward, A/D turn, Space stop, Q quit.
The last selected command remains active until another key is pressed.
"""

import select
import sys
import termios
import time
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


def command_for_key(key, linear_speed=0.25, angular_speed=0.8):
    """Return (linear.x, angular.z) for a supported key, or None."""
    commands = {
        "w": (linear_speed, 0.0),
        "s": (-linear_speed, 0.0),
        "a": (0.0, angular_speed),
        "d": (0.0, -angular_speed),
        " ": (0.0, 0.0),
    }
    return commands.get(key.lower() if key != " " else key)


class KeyboardTeleop(Node):
    """Publish keyboard-selected velocity commands to /cmd_vel."""

    def __init__(self):
        super().__init__("keyboard_teleop")
        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)
        self.linear_speed = 0.25
        self.angular_speed = 0.8

    def publish_command(self, linear, angular):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.publisher.publish(msg)


def main(args=None):
    if not sys.stdin.isatty():
        raise RuntimeError(
            "keyboard_teleop needs an interactive terminal. "
            "Run it in a terminal window, not as a background process."
        )

    rclpy.init(args=args)
    node = KeyboardTeleop()
    original_terminal_settings = termios.tcgetattr(sys.stdin)
    current_command = (0.0, 0.0)

    print("\nMobile robot keyboard control")
    print("  W: forward   S: reverse")
    print("  A: turn left D: turn right")
    print("  SPACE: stop  Q: quit")
    print("The command persists until another key is pressed.\n")

    try:
        tty.setcbreak(sys.stdin.fileno())
        while rclpy.ok():
            readable, _, _ = select.select([sys.stdin], [], [], 0.1)
            if readable:
                key = sys.stdin.read(1)
                if key.lower() == "q":
                    current_command = (0.0, 0.0)
                    node.publish_command(*current_command)
                    break

                command = command_for_key(
                    key, node.linear_speed, node.angular_speed
                )
                if command is not None:
                    current_command = command
                    node.get_logger().info(
                        f"cmd_vel: linear.x={command[0]:.2f}, "
                        f"angular.z={command[1]:.2f}"
                    )

            node.publish_command(*current_command)

    except KeyboardInterrupt:
        pass
    finally:
        node.publish_command(0.0, 0.0)
        time.sleep(0.05)
        termios.tcsetattr(
            sys.stdin, termios.TCSADRAIN, original_terminal_settings
        )
        node.destroy_node()
        rclpy.shutdown()
        print("\nKeyboard teleoperation stopped.")


if __name__ == "__main__":
    main()
