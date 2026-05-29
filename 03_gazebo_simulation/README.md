# Step 3: Gazebo Physics Simulation

This directory covers simulating the Unitree Go2-W inside **Gazebo**. Gazebo provides a traditional CPU/GPU-hybrid physics environment that is fully integrated with ROS 2.

---

## 1. Visualizing vs. Simulating the Robot Model

To simulate the Go2-W, we must describe its mechanical linkages, joint limits, mass distributions, and visual shells. This is achieved using two core XML standards:

1.  **URDF (Unified Robot Description Format):** A structured XML schema detailing a tree-like chain of rigid body links connected by joint axes.
2.  **Xacro (XML Macros):** A templating engine for URDF. Because quadrupeds have four symmetric legs, coding each link manually creates thousands of lines of duplicate XML. Xacro lets us write a single leg macro and instantiate it four times:
    ```xml
    <!-- Instantiate Left-Front, Right-Front, Left-Rear, Right-Rear Legs -->
    <xacro:leg prefix="lf" target_x="0.18" target_y="0.08"/>
    <xacro:leg prefix="rf" target_x="0.18" target_y="-0.08"/>
    ...
    ```

---

## 2. Anatomy of a Rigid Link

Every rigid link in a robot description contains three core child tags. These must be defined accurately for the simulator to compute correct physics:

*   **`<visual>`:** Defines the 3D meshes (usually high-resolution `.dae` Collada or `.stl` files) representing what the robot looks like. This has no effect on physical contact.
*   **`<collision>`:** Defines the physical geometry used by the collision detection solver. To maximize computation speed, collision geometries use simple primitives (spheres, boxes, cylinders) rather than heavy 3D CAD meshes.
*   **`<inertial>`:** The actual physics descriptor. It contains:
    *   **Mass ($m$):** The total weight of the link in kilograms.
    *   **Center of Mass (CoM):** Coordinates $[x, y, z]$ of the balancing pivot.
    *   **Inertia Tensor ($I$):** A symmetric $3\times3$ rotational mass distribution matrix representing the link's resistance to angular acceleration:
        $$ \mathbf{I} = \begin{bmatrix} I_{xx} & I_{xy} & I_{xz} \\ I_{yx} & I_{yy} & I_{yz} \\ I_{zx} & I_{zy} & I_{zz} \end{bmatrix} $$

---

## 3. Joint Controllers (`ros2_control`)

To drive the joints in Gazebo, we interface with **`ros2_control`**. This framework loads specialized hardware plugins that map standard ROS 2 commands to the simulated joint motors.

For the Go2-W, the joints are configured under two controllers:
1.  **Leg Joints Controller:** Uses a `JointTrajectoryController` or custom effort interface to actuate joint angles (HAA, HFE, KFE) using PD loops.
2.  **Wheel Motors Controller:** Uses a `VelocityController` to drive the continuous revolute wheel joints, allowing the wheels to maintain a target angular speed ($\omega$).

---

## 4. Spawning in Gazebo Workflow
To spin up a simulation, the ROS 2 launch sequence:
1.  Processes the Xacro macro files to output a flat URDF file.
2.  Launches the Gazebo simulator server and client GUI.
3.  Runs a `spawn_entity` node that reads the URDF file and places the Go2-W model into the virtual coordinates.
4.  Initializes the `controller_manager` node to bind joint and wheel controllers, opening topics like `/cmd_vel` for steering.
