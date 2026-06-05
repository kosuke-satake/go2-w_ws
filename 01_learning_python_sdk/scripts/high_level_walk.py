#!/usr/bin/env python3
"""
Test script for high-level motion control of the Unitree Go2-W robot.
This script initializes the Unitree SportClient and commands the robot
to stand up, execute a slow forward walk, stop, and lie down.
"""

import argparse
import sys
import time
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient


def main():
    parser = argparse.ArgumentParser(description="Go2-W High-Level Locomotion Walk Test")
    parser.add_argument(
        "--interface",
        type=str,
        default="wlan0",
        help="Network interface name connected to the robot (e.g. eth0, wlan0, lo)",
    )
    args = parser.parse_args()

    # 1. Initialize the communication channel
    # The first parameter is the local system ID (typically 0)
    # The second parameter is the network interface bound to the robot
    print(f"Initializing ChannelFactory on network interface: {args.interface}")
    try:
        ChannelFactoryInitialize(0, args.interface)
    except Exception as e:
        print(f"Error initializing ChannelFactory: {e}", file=sys.stderr)
        print("Make sure you are running this on the Thinkpad and the interface exists.", file=sys.stderr)
        sys.exit(1)

    # 2. Instantiate and initialize the SportClient
    print("Initializing SportClient...")
    sport_client = SportClient()
    sport_client.SetTimeout(10.0)
    sport_client.Init()

    try:
        # 3. Command Stand Up
        print("Commanding robot to STAND UP...")
        sport_client.StandUp()
        print("Waiting 3 seconds for stabilization...")
        time.sleep(3.0)

        # 4. Command Forward Movement
        # VelocityMove parameters: vx (longitudinal), vy (lateral), vyaw (yaw rate)
        # vx = 0.2 m/s (forward), vy = 0.0 m/s, vyaw = 0.0 rad/s
        print("Commanding robot to WALK FORWARD at 0.2 m/s...")
        sport_client.VelocityMove(0.2, 0.0, 0.0)
        
        print("Walking for 4 seconds...")
        time.sleep(4.0)

        # 5. Stop Movement
        print("Commanding robot to STOP moving...")
        sport_client.StopMove()
        print("Waiting 2 seconds...")
        time.sleep(2.0)

        # 6. Command Stand Down (Lie down)
        print("Commanding robot to STAND DOWN (lie down)...")
        sport_client.StandDown()
        print("Test complete.")

    except KeyboardInterrupt:
        print("\nInterrupt received. Sending emergency stop (Damp) command...")
        # Damp command cuts power/dampens joints in case of emergency
        sport_client.Damp()
        sys.exit(1)


if __name__ == "__main__":
    main()
