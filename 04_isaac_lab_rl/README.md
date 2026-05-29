# Step 4: NVIDIA Isaac Lab & Reinforcement Learning

This directory introduces reinforcement learning (RL) using **NVIDIA Isaac Lab** (formerly Orbit), a GPU-accelerated robotics simulation platform built on **NVIDIA Omniverse**. We cover observation states, action mapping, reward functions, and sim-to-real deployment.

---

## 1. Traditional Control vs. Reinforcement Learning

Traditional locomotion control requires manual design of Model Predictive Control (MPC) solvers or Whole-Body Controllers (WBC). While highly effective, these solvers struggle when the environment undergoes rapid, unstructured changes (e.g., slipping on ice, stepping on loose gravel).

Reinforcement Learning bypasses manual design. By placing the robot in a virtual sandbox, a policy (represented by a neural network) learns locomotion through trial and error:

```
                  +--------------------------------+
                  |           Environment          |
                  |     (Isaac Lab Simulation)     |
                  +--------------------------------+
                     /                          ^
      Observations  /                            \ Actions (Joint Positions)
         State     /                              \ 
                  v                                \ 
            +-----------+                      +-----------+
            |   Agent   | ===(Evaluation)===>  |  Policy   |
            | (PyTorch) |                      |  Network  |
            +-----------+                      +-----------+
                  \                                  ^
                   \=====(Calculate Rewards)========/
```

---

## 2. Mathematical MDP Formulation

We model the learning problem as a Markov Decision Process (MDP) defined by the tuple $(\mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma)$:

### 2.1 Observation Space ($\mathcal{S}$)
The policy network requires state observation vectors $s_t$ at each timestep to make decisions. For a hybrid wheeled-quadruped, $s_t$ typically includes:
*   **Command Vectors:** Desired forward, lateral, and rotational velocities ($v_{x, cmd}, v_{y, cmd}, \omega_{yaw, cmd}$).
*   **Base Orientation:** Gravity vector projection onto the local robot base frame (extracted from the simulated IMU).
*   **Base Angular Velocity:** Rotational rates ($\omega_x, \omega_y, \omega_z$).
*   **Joint State Vectors:** 12-element leg joint positions ($q$) and velocities ($\dot{q}$).
*   **Wheel State Vectors:** 4-element wheel angular rates ($\omega$).
*   **Action History:** The control actions output at the previous timestep ($a_{t-1}$).

### 2.2 Action Space ($\mathcal{A}$)
The policy outputs actions $a_t$ at a frequency of $50 \text{ Hz} - 100 \text{ Hz}$. Rather than outputting raw motor voltages or target torques (which are highly unstable to learn), the action space maps to:
*   **Joint Target Offsets:** Angled offsets $\Delta q_{target}$ added to a nominal standing joint configuration $q_{nominal}$.
*   **Wheel Target Speeds:** Target angular velocities $\omega_{target}$ for the hub motors.

---

## 3. Reward Function Design ($\mathcal{R}$)

The behavior of the robot is entirely shaped by the reward function $r_t$. A poorly designed reward function can cause the robot to learn unnatural, energy-inefficient gaits (like hopping or dragging a leg).

We construct a multi-term reward function to balance velocity tracking with smoothness and safety:

### Velocity Tracking Term
To encourage the robot to match the commanded velocity $v_{x, target}$, we use a Gaussian kernel reward:

$$ r_{vel} = \exp\left( -\frac{(v_{x, target} - v_x)^2}{\sigma^2} \right) $$

Where $\sigma$ is a scaling parameter adjusting the penalty sensitivity. If the error is zero, the term yields a maximum reward of $1.0$.

### Regularization & Safety Terms
To prevent jerky behaviors, joint wear, and falls, we add negative rewards (penalties):
*   **Torque Penalty:** Minimizes thermal wear by penalizing high motor torques:
    $$ p_{torque} = -\sum_{i=1}^{16} \tau_i^2 $$
*   **Joint Acceleration Penalty:** Penalizes sharp, non-smooth movement changes:
    $$ p_{accel} = -\sum_{i=1}^{12} \ddot{q}_i^2 $$
*   **Base Orientation Penalty:** Keeps the torso upright by penalizing deviation from the vertical gravity vector:
    $$ p_{orient} = -\|\mathbf{g}_{projected} - \mathbf{g}_{vertical}\|^2 $$

The total step reward is the weighted sum of these terms:

$$ r_t = w_{vel} r_{vel} + w_{torque} p_{torque} + w_{accel} p_{accel} + w_{orient} p_{orient} $$

---

## 4. Sim-to-Real & ONNX Deployment

To deploy the trained policy onto the physical Go2-W:
1.  **Export the Model:** Once PyTorch training converges, compile the policy network into a serialized **ONNX** graph.
2.  **Onboard Inference:** Transfer the `.onnx` file to the robot's Jetson Orin NX.
3.  **Real-time Script:** Run a lightweight Python script that queries the real sensors (IMU, joint encoders) to build the observation vector $s_t$, passes it through the ONNX model using `onnxruntime`, and sends the output target actions directly to Layer 1 (CAN bus motor interfaces) at $100 \text{ Hz}$.
