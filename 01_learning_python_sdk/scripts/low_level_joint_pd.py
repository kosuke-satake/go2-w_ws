#!/usr/bin/env python3
"""
Safe template script for low-level control of the Unitree Go2-W robot.
This script demonstrates how to read joint encoder states (position, velocity)
and structure target joint motor packets using the PD control law.
"""

import argparse
import sys
import time
from unitree_sdk2.core.channel import ChannelFactoryInitialize
from unitree_sdk2.go2.low_level.low_state_client import LowStateClient
# Note: In low-level control, commands are sent via a LowCmdClient
from unitree_sdk2.go2.low_level.low_cmd_client import LowCmdClient


def main():
    parser = argparse.ArgumentParser(description="Go2-W Low-Level Joint State Query and PD Template")
    parser.add_argument(
        "--interface",
        type=str,
        default="wlan0",
        help="Network interface name connected to the robot (e.g. eth0, wlan0, lo)",
    )
    args = parser.parse_args()

    # 1. Initialize communication channel
    print(f"Initializing ChannelFactory on network interface: {args.interface}")
    try:
        ChannelFactoryInitialize(0, args.interface)
    except Exception as e:
        print(f"Error initializing ChannelFactory: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Initialize Low-level clients
    # LowStateClient reads data, LowCmdClient sends motor control commands
    low_state_client = LowStateClient()
    low_state_client.Init()
    
    # 3. Read current state safely
    print("Connecting to robot low-level state stream...")
    print("Reading joint positions (HAA, HFE, KFE) for 5 seconds (Safe Query Mode)...")
    
    # Mapping of 12 joints in Unitree SDK:
    # 0: FR_hip, 1: FR_thigh, 2: FR_calf
    # 3: FL_hip, 4: FL_thigh, 5: FL_calf
    # 6: RR_hip, 7: RR_thigh, 8: RR_calf
    # 9: RL_hip, 10: RL_thigh, 11: RL_calf
    joint_names = [
        "FR_hip", "FR_thigh", "FR_calf",
        "FL_hip", "FL_thigh", "FL_calf",
        "RR_hip", "RR_thigh", "RR_calf",
        "RL_hip", "RL_thigh", "RL_calf"
    ]

    try:
        start_time = time.time()
        while time.time() - start_time < 5.0:
            # Fetch current state packet
            state = low_state_client.GetLatestState()
            if state is not None:
                # Print motor states for Front Left (FL) Leg (joints 3, 4, 5)
                fl_hip_pos = state.motor_state[3].q
                fl_thigh_pos = state.motor_state[4].q
                fl_calf_pos = state.motor_state[5].q
                
                print(
                    f"\rFL Leg Encoders -> Hip (HAA): {fl_hip_pos:6.3f} rad | "
                    f"Thigh (HFE): {fl_thigh_pos:6.3f} rad | "
                    f"Calf (KFE): {fl_calf_pos:6.3f} rad",
                    end="",
                    flush=True
                )
            else:
                print("\rWaiting for state packet...", end="", flush=True)
            time.sleep(0.1)
        print("\nQuery complete.")

    except KeyboardInterrupt:
        print("\nExiting safe query.")

    # 4. Illustrative Low-Level Motor Packet Assembly (Not Sent)
    print("\n--- Low-Level PD Motor Packet Guide ---")
    print("To actuate a motor, you construct a target packet per joint:")
    print("  torque = K_p * (q_target - q) + K_d * (q_dot_target - q_dot) + torque_feedforward")
    print("\nExample structure for a single motor command:")
    print("  motor_cmd.q = 0.0          # Target angle (rad)")
    print("  motor_cmd.dq = 0.0         # Target angular velocity (rad/s)")
    print("  motor_cmd.kp = 20.0        # Proportional gain (N-m/rad)")
    print("  motor_cmd.kd = 0.5         # Derivative gain (N-m-s/rad)")
    print("  motor_cmd.tau = 0.0        # Feed-forward torque (N-m)")


if __name__ == "__main__":
    main()
