#!/usr/bin/env python3
"""
Safe template script for low-level state query of the Unitree Go2-W robot.
This script demonstrates how to subscribe to joint encoder states (position, velocity)
safely using the ChannelSubscriber.
"""

import argparse
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_


class LowStateReceiver:
    def __init__(self):
        self.latest_state = None

    def state_callback(self, msg: LowState_):
        self.latest_state = msg


def main():
    parser = argparse.ArgumentParser(description="Go2-W Low-Level Joint State Query")
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
        print(f"Error initializing ChannelFactory: {e}")
        return

    # 2. Subscribe to Low State topic "rt/lowstate"
    receiver = LowStateReceiver()
    subscriber = ChannelSubscriber("rt/lowstate", LowState_)
    subscriber.Init(receiver.state_callback, 10)

    # 3. Read current state safely for 5 seconds
    print("Connecting to robot low-level state stream...")
    print("Reading joint positions (HAA, HFE, KFE) for 5 seconds (Safe Query Mode)...")

    start_time = time.time()
    try:
        while time.time() - start_time < 5.0:
            state = receiver.latest_state
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
