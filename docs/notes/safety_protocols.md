# Technical Note: Go2-W Hardware Safety Protocols

Quadruped robots are powerful dynamic machines. High joint speeds, heavy chassis mass ($\approx 18 \text{ kg}$), and wheeled hub actuators represent immediate mechanical risks to fingers, workspace surroundings, and the robot's own aluminum framework. 

This document details the emergency operations and safety rules that must be followed during every software execution.

---

## 1. The Emergency Stop Command (Damp Mode)

In Unitree systems, the ultimate software safety state is **Damping**. Damp mode immediately cuts power to the leg joint motors, making the linkages loose and causing the robot to collapse under gravity.

If the robot behaves unpredictably (e.g., oscillating violently or running toward an obstacle), execute one of the following immediately:

### A. The Physical Remote Controller (Immediate Hand-Held E-Stop)
*   **Trigger Command:** Press the **L2 + B** button combination on the hand-held Unitree remote controller.
*   **Result:** The robot instantly cuts motor power and collapses safely to the ground. Keep the remote controller in your hand or within arm's reach during every live test.

### B. Python SDK Software E-Stop
If writing custom low-level or high-level control loops, wrap your main execution inside a `try/except` block to ensure a keyboard interrupt (`Ctrl + C`) triggers the damp command:

```python
from unitree_sdk2py.go2.sport.sport_client import SportClient

sport_client = SportClient()
sport_client.Init()

try:
    # Your active locomotion loop here
    pass
except KeyboardInterrupt:
    print("Emergency interrupt received! Cutting motor power...")
    sport_client.Damp()  # Transitions joints to soft damping mode
```

---

## 2. Low-Level Joint Gain Limits

When programming in low-level joint command mode (sending target positions $q$ and gains directly to joints), you must calculate output torques using closed-loop PD parameters:

$$ \tau = K_p (q_{target} - q) + K_d (\dot{q}_{target} - \dot{q}) + \tau_{ff} $$

To prevent drawing excessive currents or slamming joint linkages into their mechanical end-stops, strictly limit your software gains to the following bounds:

| Joint Type | Max Proportional Gain ($K_p$) | Max Derivative Gain ($K_d$) | Max Allowable Torque ($\tau$) |
| :--- | :--- | :--- | :--- |
| **Hip (HAA)** | $30.0 \text{ N}\cdot\text{m/rad}$ | $1.0 \text{ N}\cdot\text{m}\cdot\text{s/rad}$ | $\pm 5.0 \text{ N}\cdot\text{m}$ |
| **Thigh (HFE)**| $40.0 \text{ N}\cdot\text{m/rad}$ | $1.5 \text{ N}\cdot\text{m}\cdot\text{s/rad}$ | $\pm 10.0 \text{ N}\cdot\text{m}$ |
| **Knee (KFE)** | $40.0 \text{ N}\cdot\text{m/rad}$ | $1.5 \text{ N}\cdot\text{m}\cdot\text{s/rad}$ | $\pm 10.0 \text{ N}\cdot\text{m}$ |

### Safety Rules for Low-Level Code:
1.  **Never start testing with high gains:** Always begin testing a new controller with $K_p \le 5.0$ and $K_d \le 0.2$. Gradually increase gains only if the joints fail to support the robot's weight.
2.  **Verify Joint Angles in Code:** Wrap your target joint angles in boundary clamps to prevent commanding angles beyond the physical leg workspace.

---

## 3. Physical Workspace Setup

1.  **Suspension Stand (Highly Recommended for low-level tests):** When deploying a new controller or a trained Isaac Lab RL model for the first time on hardware, **suspend the robot's torso in the air** using a harness or place the chassis on a solid wooden block so the wheels and feet hang freely off the ground.
2.  **Clear Area:** Ensure a minimum of **$2.0 \text{ meters}$ of open space** in all directions when running locomotion commands on the ground.
3.  **Tire Check:** Before enabling wheeled-rolling mode, verify that the 7-inch pneumatic tires are inflated correctly and free of debris.
