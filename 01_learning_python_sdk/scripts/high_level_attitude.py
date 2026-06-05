#!/usr/bin/env python3
"""
Test script for high-level body attitude control of the Unitree Go2-W robot.
This script stands the robot up, enables attitude control (Pose), sweeps the body
through roll, pitch, and yaw oscillations, disables attitude control, and lies down.
"""

import argparse
import sys
import time
import math
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient


def main():
    parser = argparse.ArgumentParser(description="Go2-W High-Level Attitude Sweep Test")
    parser.add_argument(
        "--interface",
        type=str,
        default="wlan0",
        help="Network interface name connected to the robot (e.g. eth0, wlan0, lo)",
    )
    args = parser.parse_args()

    # 1. Initialize the communication channel
    print(f"Initializing ChannelFactory on network interface: {args.interface}")
    try:
        ChannelFactoryInitialize(0, args.interface)
    except Exception as e:
        print(f"Error initializing ChannelFactory: {e}", file=sys.stderr)
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

        # 4. Enable Attitude Control mode (Pose)
        print("Enabling body attitude control (Pose mode)...")
        sport_client.Pose(True)
        time.sleep(1.0)

        # 5. Sweep Roll
        # Roll: Rotation about x-axis (lateral sway)
        print("Swaying body laterally (ROLL sweep)...")
        for i in range(41):
            t = i * 0.1
            roll = 0.15 * math.sin(2 * math.pi * 0.25 * t)  # 0.25 Hz frequency
            sport_client.Euler(roll, 0.0, 0.0)
            time.sleep(0.05)
        
        # Reset Euler
        sport_client.Euler(0.0, 0.0, 0.0)
        time.sleep(1.0)

        # 6. Sweep Pitch
        # Pitch: Rotation about y-axis (nodding)
        print("Nodding body up and down (PITCH sweep)...")
        for i in range(41):
            t = i * 0.1
            pitch = 0.15 * math.sin(2 * math.pi * 0.25 * t)
            sport_client.Euler(0.0, pitch, 0.0)
            time.sleep(0.05)

        # Reset Euler
        sport_client.Euler(0.0, 0.0, 0.0)
        time.sleep(1.0)

        # 7. Sweep Yaw
        # Yaw: Rotation about z-axis (heading twisting)
        print("Twisting body heading (YAW sweep)...")
        for i in range(41):
            t = i * 0.1
            yaw = 0.20 * math.sin(2 * math.pi * 0.25 * t)
            sport_client.Euler(0.0, 0.0, yaw)
            time.sleep(0.05)

        # Reset Euler
        print("Resetting to neutral stance...")
        sport_client.Euler(0.0, 0.0, 0.0)
        time.sleep(1.0)

        # 8. Disable Attitude Control mode (Pose)
        print("Disabling attitude control...")
        sport_client.Pose(False)
        time.sleep(1.0)

        # 9. Command Stand Down (Lie down)
        print("Commanding robot to STAND DOWN (lie down)...")
        sport_client.StandDown()
        print("Attitude sweep test complete.")

    except KeyboardInterrupt:
        print("\nInterrupt received. Resetting pose and standing down...")
        try:
            sport_client.Euler(0.0, 0.0, 0.0)
            sport_client.Pose(False)
            time.sleep(0.5)
            sport_client.StandDown()
        except Exception:
            print("Could not stand down cleanly. Sending Damp command...")
            sport_client.Damp()
        sys.exit(1)


if __name__ == "__main__":
    main()
