# Workspace Memory: Unitree Go2-W Robotics Workspace

This repository houses the learning progression, middleware configurations, and simulation assets for the **Unitree Go2-W wheeled-quadruped robot**. It is structured to guide developers step-by-step from high-level Python API locomotion to low-level ROS 2 middleware and GPU-accelerated reinforcement learning inside NVIDIA Isaac Lab.

---

## 1. System Topology & Specifications

The Unitree Go2-W is a hybrid legged-wheeled quadruped robot. The chassis acts as the primary inertial base, housing the onboard processing units, depth cameras, 3D LiDAR, and battery.

### Mechanical Dimensions & Actuators
*   **Mass ($M$):** $\approx 18.0 \text{ kg}$ (base configuration).
*   **Actuation Degrees of Freedom (DoF):** 16 active joints.
    *   **Leg Joints (12 DoF):** 3 active revolute joints per leg.
        *   Hip Abduction/Adduction (HAA)
        *   Hip Flexion/Extension (HFE)
        *   Knee Flexion/Extension (KFE)
    *   **Wheel Actuators (4 DoF):** 1 active brushless DC in-wheel motor at the distal end of each calf, replacing the traditional rubber foot pad with a 7-inch pneumatic tire.

### Sensor Suite
*   **Proprietary IMU:** High-frequency Inertial Measurement Unit providing 3-axis acceleration and angular rate.
*   **Exteroceptive Sensors:** Wide-angle HD camera and a super-wide-angle 3D LiDAR for spatial mapping and depth estimation.

---

## 2. Locomotion Physics: First-Principles Derivation

To program control systems or train reinforcement learning models, we must define the mathematical models governing the robot's physical interactions.

### 2.1 Leg Kinematics (Joint Space to Cartesian Space)

Each leg is modeled as a 3-DoF serial linkage manipulator. The origin of the local frame is located at the center of the HAA joint. Let the coordinates of the foot contact point relative to the HAA origin be represented by the vector $\mathbf{p} = [x, y, z]^T$.

Let:
*   $d_{hip}$ be the lateral offset of the hip joint.
*   $l_{thigh}$ be the length of the thigh link.
*   $l_{calf}$ be the length of the calf link.
*   $\theta_{hip}$ be the HAA joint angle (rotation about the $x$-axis).
*   $\theta_{thigh}$ be the HFE joint angle (rotation about the $y$-axis, relative to the gravity vector).
*   $\theta_{calf}$ be the KFE joint angle (rotation about the $y$-axis, relative to the thigh link).

We define the intermediate planar coordinates in the leg's sagittal plane (post-HAA rotation) as $x'$ and $z'$:

$$ x' = l_{thigh} \sin(\theta_{thigh}) + l_{calf} \sin(\theta_{thigh} + \theta_{calf}) $$

$$ z' = -l_{thigh} \cos(\theta_{thigh}) - l_{calf} \cos(\theta_{thigh} + \theta_{calf}) $$

To map these planar coordinates back to the 3D hip frame, we apply a rotation of $\theta_{hip}$ about the $x$-axis:

$$ \mathbf{p}_{foot} = \begin{bmatrix} x \\ y \\ z \end{bmatrix} = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos(\theta_{hip}) & -\sin(\theta_{hip}) \\ 0 & \sin(\theta_{hip}) & \cos(\theta_{hip}) \end{bmatrix} \begin{bmatrix} x' \\ d_{hip} \\ z' \end{bmatrix} $$

Evaluating this matrix multiplication yields the explicit forward kinematics equations:

$$ x = l_{thigh} \sin(\theta_{thigh}) + l_{calf} \sin(\theta_{thigh} + \theta_{calf}) $$

$$ y = d_{hip} \cos(\theta_{hip}) - z' \sin(\theta_{hip}) $$

$$ z = d_{hip} \sin(\theta_{hip}) + z' \cos(\theta_{hip}) $$

Substituting $z'$ into the expressions for $y$ and $z$:

$$ y = d_{hip} \cos(\theta_{hip}) + \left( l_{thigh} \cos(\theta_{thigh}) + l_{calf} \cos(\theta_{thigh} + \theta_{calf}) \right) \sin(\theta_{hip}) $$

$$ z = d_{hip} \sin(\theta_{hip}) - \left( l_{thigh} \cos(\theta_{thigh}) + l_{calf} \cos(\theta_{thigh} + \theta_{calf}) \right) \cos(\theta_{hip}) $$

These expressions form the baseline for inverse kinematics mapping and trajectory planning.

---

### 2.2 Non-Holonomic Wheeled Dynamics & Contact Mechanics

When the robot operates in wheeled-rolling mode, the distal end of the leg is constrained by the tire contact patch. Let the wheel have a radius $R$ and rotate with an angular velocity $\omega$ driven by the hub motor.

Under the ideal non-holonomic assumption of pure rolling without slipping, the forward velocity of the wheel center relative to the ground plane, denoted $v_x$, satisfies:

$$ v_x = R \cdot \omega $$

In real-world scenarios, soft tires on deformable or slippery surfaces undergo longitudinal slipping. We quantify this mechanical deviation using the non-dimensional longitudinal slip ratio $s$:

$$ s = \frac{v_x - R\omega}{\max(|v_x|, |R\omega|)} $$

The boundary states are defined as:
*   $s = 0$: Perfect rolling (zero slipping).
*   $s = 1$: The wheel is locked ($\omega = 0$) while the robot slides forward (100% braking slip).
*   $s = -1$: The wheel is spinning in place ($v_x = 0$) (100% drive slip).

The longitudinal friction force $F_x$ exerted by the ground on the tire is a non-linear function of the slip ratio $s$ and the normal force $F_z$ (vertical load):

$$ F_x = \mu(s) \cdot F_z $$

Where $\mu(s)$ is typically modeled using Pacjeka's Magic Formula or similar empirical tire models. During reinforcement learning training, we randomly perturb the friction coefficient $\mu$ to ensure the policy generalizes across slippery, rigid, and deformable terrains.

---

## 3. Project Guidelines

### Coding Standards
*   **Python:** Enforced using PEP 8 standards with Ruff checks configured in `pyproject.toml`.
*   **C++ / ROS 2:** Enforced using standard ROS 2 linting rules, using descriptive variable names and structured comments.
*   **No Placeholders:** All source code and launch configurations must contain functional, clean implementations.

### Git Version Control
*   Use descriptive, imperative commit messages (e.g., `feat(kinematics): add coordinate mapping calculations`).
*   Verify that local cache folders (`build/`, `install/`, `log/`, `__pycache__/`) are never committed.
