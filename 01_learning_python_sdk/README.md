# Step 1: Unitree Python SDK Locomotion Control

This directory focuses on learning how to interact with the Unitree Go2-W using the Python SDK. We cover the transition from High-Level locomotion vectors to Low-Level joint torque actuation.

---

## 1. High-Level vs. Low-Level Control Modes

The Unitree SDK exposes two primary ways to interface with the robot's locomotion system:

| Aspect | High-Level Control (Sport API) | Low-Level Control (Joint API) |
| :--- | :--- | :--- |
| **Input Data** | Linear and angular velocity vectors ($v_x, v_y, \omega_{yaw}$) | Target position, velocity, and PD gains per motor joint |
| **Control Loop** | Low-frequency ($10 \text{ Hz} - 50 \text{ Hz}$) | High-frequency ($200 \text{ Hz} - 1000 \text{ Hz}$) |
| **Safety Net** | Internal balance algorithms are fully active | Disabled. Raw joint commands are sent directly to motors |
| **Ideal For** | Navigation, mapping, teleoperation, tracking | Custom gait design, impedance control, RL deployment |

---

## 2. High-Level Control (Velocity Vectors)

In High-Level mode, you send desired movement velocities to the robot. The internal controller automatically coordinates leg swing phases, foot contact sequences, and body balance using CycloneDDS networking.

### Command Structure
A standard high-level command specifies:
*   $v_x$: Longitudinal speed (forward/backward) in $\text{m/s}$
*   $v_y$: Lateral speed (left/right) in $\text{m/s}$
*   $\omega_{yaw}$: Yaw angular rate (turn left/right) in $\text{rad/s}$

To initiate movement safely, the command sequence follows a strict state transition:
1.  **Stand:** Command the robot to transition from a laying position to a standard standing pose.
2.  **Locomotion State:** Send continuous motion packets. If packets stop arriving, the robot automatically decelerates and stands still.

---

## 3. Low-Level Control (Joint Actuation Physics)

In Low-Level mode, the internal balancing algorithm is bypassed. You control each of the 12 joint motors individually. 

For each joint, you send a control packet containing five parameters:
*   $q_{target}$: Target joint position ($\text{rad}$)
*   $\dot{q}_{target}$: Target joint velocity ($\text{rad/s}$)
*   $K_p$: Proportional gain ($\text{N}\cdot\text{m/rad}$)
*   $K_d$: Derivative gain ($\text{N}\cdot\text{m}\cdot\text{s/rad}$)
*   $\tau_{ff}$: Feed-forward torque ($\text{N}\cdot\text{m}$)

The onboard motor driver calculates the target torque $\tau$ to apply using a closed-loop PD control law:

$$ \tau = K_p (q_{target} - q) + K_d (\dot{q}_{target} - \dot{q}) + \tau_{ff} $$

Where:
*   $q$ is the current joint position measured by the absolute encoder.
*   $\dot{q}$ is the current joint velocity.

> [!WARNING]
> When programming in Low-Level mode, setting $K_p$ and $K_d$ gains incorrectly can cause the leg to swing violently or oscillate. This can immediately trigger motor over-current protection or cause mechanical structural damage. Always test low-level scripts in simulation before deploying to physical hardware.

---

## 4. Vision Streaming

The onboard wide-angle camera streams a 720p feed. The SDK provides a DDS-based video streaming listener. By binding this listener to a receiver, you can capture frames directly into standard NumPy arrays for processing with OpenCV or passing to deep-learning models (e.g., YOLO object detection) on your workstation or the onboard NVIDIA Jetson.

---

## 5. Implementation Roadmap
1.  **[high_level_walk.py](file:///Users/kosuke/Developer/Projects/go2-w/go2-w_ws/01_learning_python_sdk/scripts/high_level_walk.py):** Initializes the SportClient, commands the robot to stand, walks forward slowly, and stands down.
2.  **[low_level_joint_pd.py](file:///Users/kosuke/Developer/Projects/go2-w/go2-w_ws/01_learning_python_sdk/scripts/low_level_joint_pd.py):** Queries the joint motor state stream safely and prints absolute encoder telemetry.

