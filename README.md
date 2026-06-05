# Unitree Go2-W Wheeled-Quadruped Workspace

This repository houses the learning progression, middleware configurations, and simulation environments for the **Unitree Go2-W hybrid wheeled-quadruped robot**. It is designed as a structured, step-by-step engineering framework transitioning from high-level Python API controls to low-level ROS 2 middleware, physics-based Gazebo simulations, and reinforcement learning (RL) policies using NVIDIA Isaac Lab.

---

## Workspace Architecture

The repository is structured into four distinct phases, allowing developers to isolate and verify components independently before integrating them on physical hardware:

```
go2-w_ws/
├── 01_learning_python_sdk/    # Phase 1: High-level sport & low-level joint motor API
│   ├── README.md
│   └── scripts/
├── 02_ros2_jazzy_middleware/  # Phase 2: ROS 2 Jazzy, DDS isolation, & custom driver nodes
│   ├── README.md
│   └── src/
├── 03_gazebo_simulation/      # Phase 3: URDF/Xacro rigid body models & joint controllers
│   ├── README.md
│   └── urdf/
└── 04_isaac_lab_rl/           # Phase 4: Isaac Lab environment configs & reward equations
    ├── README.md
    └── envs/
```

---

## Technical Stack & Dependencies

*   **Host OS:** Ubuntu 24.04 LTS (Noble Numbat)
*   **Robot Platform:** Unitree Go2-W (legged-wheeled quadruped)
*   **Middleware:** ROS 2 Jazzy Jalisco
*   **DDS Layer:** Eclipse CycloneDDS (0.10.x)
*   **Simulation Engines:** Gazebo Harmonic & NVIDIA Omniverse Isaac Sim / Isaac Lab
*   **Core Languages:** Python 3.10+, C++17

---

## Implementation Progression

### [Phase 1: Unitree Python SDK](file:///Users/kosuke/Developer/Projects/go2-w/go2-w_ws/01_learning_python_sdk/README.md)
*   **Objective:** Establish communication with the physical robot via Python bindings.
*   **Focus Areas:** High-level motion vectors ($v_x, v_y, \omega_{yaw}$) using the Sport API vs. low-level proportional-derivative (PD) torque commands sent directly to the motor joints.
*   **Mathematical Concept:** Motor joint PD control law:
    $$ \tau = K_p (q_{target} - q) + K_d (\dot{q}_{target} - \dot{q}) + \tau_{ff} $$

### [Phase 2: ROS 2 Jazzy Middleware](file:///Users/kosuke/Developer/Projects/go2-w/go2-w_ws/02_ros2_jazzy_middleware/README.md)
*   **Objective:** Bridge SDK data streams to ROS 2 topics for sensors and commands.
*   **Focus Areas:** DDS network isolation (using `cyclonedds.xml` local loopbacks), topic structures, and nodes publishing odometry (`nav_msgs/Odometry`) and subscribing to velocity inputs (`geometry_msgs/Twist`).

### [Phase 3: Gazebo Simulation](file:///Users/kosuke/Developer/Projects/go2-w/go2-w_ws/03_gazebo_simulation/README.md)
*   **Objective:** Define a virtual rigid-body model of the Go2-W.
*   **Focus Areas:** Visual, collision, and inertial parameters (mass and inertia tensors $\mathbf{I}$) defined inside URDF/Xacro macros, combined with `ros2_control` joint controllers.

### [Phase 4: NVIDIA Isaac Lab & RL](file:///Users/kosuke/Developer/Projects/go2-w/go2-w_ws/04_isaac_lab_rl/README.md)
*   **Objective:** Train a custom legged-wheeled locomotion policy on the GPU.
*   **Focus Areas:** Reinforcement learning MDP formulation (Observation/Action spaces), velocity-tracking reward functions, domain randomization, and ONNX deployment.

---

## Getting Started

### 1. Initialize the Virtual Environment
Create and activate the virtual environment inside the workspace directory:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install the Unitree SDK 2 Python Bindings
Ensure CycloneDDS is compiled on your system, then install the SDK in editable mode:
```bash
export CYCLONEDDS_HOME="/path/to/your/cyclonedds/install"
pip install -e /path/to/unitree_sdk2_python
```
