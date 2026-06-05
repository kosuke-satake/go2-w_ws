#!/usr/bin/env python3
"""
A simple ROS 2 node that subscribes to the robot's odometry topic (/odom)
to monitor and display its current coordinates and heading.
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import math


class OdometryMonitor(Node):
    def __init__(self):
        super().__init__("odom_monitor")
        
        # Create a subscriber to the "/odom" topic
        # Topic type: nav_msgs/msg/Odometry
        # Queue size (QoS): 10 (keeps the last 10 messages)
        self.subscription = self.create_subscription(
            Odometry,
            "/odom",
            self.odom_callback,
            10
        )
        self.get_logger().info("Odometry Monitor Node has been started.")
        self.get_logger().info("Listening on topic: /odom")

    def odom_callback(self, msg: Odometry):
        # 1. Extract Position coordinates (x, y, z)
        position = msg.pose.pose.position
        
        # 2. Extract Orientation quaternion (x, y, z, w)
        q = msg.pose.pose.orientation
        
        # 3. Convert Quaternion to Euler Yaw (Heading) angle
        # Formula for yaw from quaternion rotation:
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        yaw_degrees = math.degrees(yaw)

        # 4. Log the state at regular intervals
        self.get_logger().info(
            f"Pose: [{position.x:.2f}, {position.y:.2f}, {position.z:.2f}] | "
            f"Yaw: {yaw_degrees:.1f}°"
        )


def main(args=None):
    rclpy.init(args=args)
    node = OdometryMonitor()
    
    try:
        # Spin keeps the node active, listening for callback triggers
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down Odometry Monitor Node.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
