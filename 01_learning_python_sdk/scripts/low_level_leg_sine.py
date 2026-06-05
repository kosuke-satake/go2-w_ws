#!/usr/bin/env python3
"""
Safe low-level control script for the Unitree Go2-W robot.
This script demonstrates how to:
1. Release the high-level Sport mode using MotionSwitcherClient.
2. Read the initial joint state encoders.
3. Hold 11 joints steady while commanding the Front Left calf joint (FL_calf)
   to execute a safe, low-frequency sinusoidal sweep.
4. Keep the wheel hub motors damped at zero velocity.
5. Re-enable Sport mode cleanly upon exit.

CRITICAL: Run this test ONLY when the robot chassis is suspended in the air.
"""

import argparse
import sys
import time
import math
from unitree_sdk2py.core.channel import ChannelPublisher, ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.default import unitree_go_msg_dds__LowCmd_
from unitree_sdk2py.idl.default import unitree_go_msg_dds__LowState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowCmd_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_
from unitree_sdk2py.utils.crc import CRC
from unitree_sdk2py.utils.thread import RecurrentThread
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient


# Joint index mapping for Go2-W (12 leg joints, 4 wheel hub motors)
JOINT_IDS = {
    "FR_hip": 0, "FR_thigh": 1, "FR_calf": 2,
    "FL_hip": 3, "FL_thigh": 4, "FL_calf": 5,
    "RR_hip": 6, "RR_thigh": 7, "RR_calf": 8,
    "RL_hip": 9, "RL_thigh": 10, "RL_calf": 11,
    "FR_wheel": 12, "FL_wheel": 13, "RR_wheel": 14, "RL_wheel": 15
}

# SDK constants for disabling individual motor control
POS_STOP_F = 2.146e9
VEL_STOP_F = 16000.0


class LowLevelSineController:
    def __init__(self):
        # PD Gains
        self.kp_hold = 20.0     # Holding gain for other joints
        self.kd_hold = 1.0
        
        self.kp_sweep = 15.0    # Sweeping joint gain
        self.kd_sweep = 0.8
        
        self.kd_wheel = 1.0     # Wheel damping gain

        self.low_cmd = unitree_go_msg_dds__LowCmd_()
        self.low_state = None
        self.first_run = True
        
        self.start_pos = [0.0] * 12
        self.crc = CRC()
        self.time_elapsed = 0.0
        self.dt = 0.002  # 500 Hz control loop
        
        self.write_thread = None
        self.motion_switcher = None
        self.lowcmd_publisher = None
        self.lowstate_subscriber = None

    def state_callback(self, msg: LowState_):
        self.low_state = msg

    def init_clients(self, interface):
        # 1. Initialize channel factory
        ChannelFactoryInitialize(0, interface)

        # 2. Setup publisher and subscriber
        self.lowcmd_publisher = ChannelPublisher("rt/lowcmd", LowCmd_)
        self.lowcmd_publisher.Init()
        
        self.lowstate_subscriber = ChannelSubscriber("rt/lowstate", LowState_)
        self.lowstate_subscriber.Init(self.state_callback, 10)

        # 3. Release high-level Sport mode
        print("Connecting to Motion Switcher...")
        self.motion_switcher = MotionSwitcherClient()
        self.motion_switcher.SetTimeout(5.0)
        self.motion_switcher.Init()

        status, mode_state = self.motion_switcher.CheckMode()
        if mode_state['name']:
            print(f"Robot currently in High-Level Mode: {mode_state['name']}. Releasing...")
            self.motion_switcher.ReleaseMode()
            time.sleep(1.0)
        print("Low-Level control interface enabled.")

        # 4. Wait for state packet to ensure we have valid encoder telemetry
        print("Waiting for low state telemetry packet...")
        while self.low_state is None:
            time.sleep(0.1)
        print("Received low state packet. Initializing motor command packets...")

        # 5. Initialize motor command structures (set all to default stop/damp state)
        self.low_cmd.head[0] = 0xFE
        self.low_cmd.head[1] = 0xEF
        self.low_cmd.level_flag = 0xFF
        self.low_cmd.gpio = 0
        for i in range(20):
            self.low_cmd.motor_cmd[i].mode = 0x01  # Normal servo control mode
            self.low_cmd.motor_cmd[i].q = POS_STOP_F
            self.low_cmd.motor_cmd[i].kp = 0.0
            self.low_cmd.motor_cmd[i].dq = VEL_STOP_F
            self.low_cmd.motor_cmd[i].kd = 0.0
            self.low_cmd.motor_cmd[i].tau = 0.0

    def start_control_loop(self):
        self.write_thread = RecurrentThread(
            name="low_cmd_loop", interval=self.dt, target=self.control_step
        )
        self.write_thread.Start()
        print("Low-level control loop started at 500Hz.")

    def control_step(self):
        # On the first step, capture current joint encoder positions
        if self.first_run:
            for i in range(12):
                self.start_pos[i] = self.low_state.motor_state[i].q
            self.first_run = False
            print(f"Captured initial joint coordinates: FL_calf = {self.start_pos[5]:.3f} rad")

        # Increment trajectory time
        self.time_elapsed += self.dt

        # 1. Set Leg Joints Commands
        for i in range(12):
            if i == JOINT_IDS["FL_calf"]:
                # Execute gentle sinusoidal sweep on FL_calf joint
                # Amplitude: 0.15 rad (approx 8.5 degrees)
                # Frequency: 0.4 Hz
                angle_offset = 0.15 * math.sin(2 * math.pi * 0.4 * self.time_elapsed)
                self.low_cmd.motor_cmd[i].q = self.start_pos[i] + angle_offset
                self.low_cmd.motor_cmd[i].dq = 0.0
                self.low_cmd.motor_cmd[i].kp = self.kp_sweep
                self.low_cmd.motor_cmd[i].kd = self.kd_sweep
            else:
                # Hold all other leg joints at their startup positions
                self.low_cmd.motor_cmd[i].q = self.start_pos[i]
                self.low_cmd.motor_cmd[i].dq = 0.0
                self.low_cmd.motor_cmd[i].kp = self.kp_hold
                self.low_cmd.motor_cmd[i].kd = self.kd_hold
            
            self.low_cmd.motor_cmd[i].tau = 0.0

        # 2. Set Wheel Motor Commands (index 12-15)
        # Keep wheels stationary and damped
        for i in range(12, 16):
            self.low_cmd.motor_cmd[i].q = 0.0
            self.low_cmd.motor_cmd[i].kp = 0.0
            self.low_cmd.motor_cmd[i].dq = 0.0  # Zero target speed
            self.low_cmd.motor_cmd[i].kd = self.kd_wheel
            self.low_cmd.motor_cmd[i].tau = 0.0

        # Compute CRC check and publish lowcmd
        self.low_cmd.crc = self.crc.Crc(self.low_cmd)
        self.lowcmd_publisher.Write(self.low_cmd)

    def shutdown(self):
        print("\nShutting down controller...")
        if self.write_thread:
            self.write_thread.Stop()
            print("Control thread stopped.")

        # Restore Sport mode (high-level) so the robot is left in default standing state
        if self.motion_switcher:
            print("Restoring high-level Sport mode...")
            try:
                self.motion_switcher.SelectMode("sport")
                print("Sport mode restored.")
            except Exception as e:
                print(f"Failed to restore Sport mode: {e}")


def main():
    parser = argparse.ArgumentParser(description="Go2-W Low-Level Joint Sinusoidal Sweep Test")
    parser.add_argument(
        "--interface",
        type=str,
        default="wlan0",
        help="Network interface name connected to the robot (e.g. eth0, wlan0, lo)",
    )
    args = parser.parse_args()

    controller = LowLevelSineController()
    
    try:
        controller.init_clients(args.interface)
        controller.start_control_loop()
        
        print("Sweeping FL_calf joint. Press Ctrl+C to stop...")
        while True:
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")
    finally:
        controller.shutdown()
        print("Low level sine test complete.")


if __name__ == "__main__":
    main()
