# Step 2: ROS 2 Jazzy Middleware & Networking

This directory introduces the middleware layer using **ROS 2 Jazzy Jalisco**. We cover the foundational concepts of ROS 2 communication, CycloneDDS configuration, and spatial mapping pipelines.

---

## 1. ROS 2 Architecture for Quadruped Robotics

ROS 2 organizes the robot's software into independent modular blocks called **Nodes**. These nodes communicate asynchronously over a peer-to-peer network using specific communication patterns:

*   **Topics (Publish/Subscribe):** Continuous data streams (e.g., LiDAR point clouds published at $10 \text{ Hz}$, IMU state published at $200 \text{ Hz}$, joint state vectors).
*   **Services (Request/Response):** Synchronous execution commands (e.g., trigger a camera self-calibration, request the current battery level).
*   **Actions (Goal/Feedback/Result):** Long-running, interruptible tasks (e.g., navigate to a specific waypoint coordinates in a room).

For the Go2-W, a typical ROS 2 node diagram looks like this:

```
[3D LiDAR Node] ------(/cloud_in)------> [SLAM Mapping Node]
                                                  | (/map)
                                                  v
[Nav2 Navigation] <---(/cmd_vel)-------- [Path Planner Node]
        |
        v
[Unitree ROS Bridge] ---> (DDS Packets) ---> [Physical Robot Actuators]
```

---

## 2. CycloneDDS Configuration (Critical for Communication)

Unitree robots communicate internally and externally via DDS (Data Distribution Service). By default, ROS 2 Jazzy utilizes **FastDDS** or **CycloneDDS**. To ensure high-bandwidth sensor streams (like LiDAR or cameras) don't congest your network or lag control inputs, you must isolate and configure the DDS settings.

### Network Isolation via `cyclonedds.xml`
If multiple robots or computers run on the same Wi-Fi/Ethernet network without isolation, they will conflict, trying to bind to the same topics. To prevent this, configure a custom `cyclonedds.xml` file.

You set this file by exporting the environment variable in your terminal:
```bash
export CYCLONEDDS_URI=file:///absolute/path/to/cyclonedds.xml
```

A clean, production-grade `cyclonedds.xml` isolation template:
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<CycloneDDS xmlns="https://cdds.io/config" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://cdds.io/config https://raw.githubusercontent.com/eclipse-cyclonedds/cyclonedds/master/etc/cyclonedds.xsd">
  <Domain id="any">
    <General>
      <!-- Bind to the specific network interface of your workstation/robot -->
      <NetworkInterfaceAddress>lo</NetworkInterfaceAddress> 
      <AllowMulticast>false</AllowMulticast>
    </General>
    <Discovery>
      <!-- Explicitly define peer IP addresses if wlan/ethernet bandwidth is constrained -->
      <Peers>
        <Peer address="127.0.0.1"/>
      </Peers>
    </Discovery>
  </Domain>
</CycloneDDS>
```

---

## 3. Workspace Management & Colcon Builds

To build ROS 2 code, packages are organized in a workspace directory structure:
```
ros2_ws/
├── src/
│   ├── custom_interfaces/          # Custom message definitions
│   └── go2_w_controller/           # Custom Python/C++ control node
```

### Build Workflow
Before building, you must source the underlying ROS 2 Jazzy environment:
```bash
source /opt/ros/jazzy/setup.zsh
```

To compile and link the workspace, run `colcon build` from the workspace root:
```bash
colcon build --symlink-install
```
*   `--symlink-install` is highly recommended for Python nodes: it creates symbolic links to your scripts rather than copying them, allowing you to edit python files and run them instantly without re-compiling the workspace.

---

## 4. Spatial Mapping (SLAM) & Navigation (Nav2)

Once the ROS 2 communications are verified, you can interface with advanced spatial libraries:

1.  **SLAM (Simultaneous Localization and Mapping):**
    *   Feed the 3D LiDAR topic (typically `/point_cloud`) and the IMU topic (`/imu/data`) into a LiDAR-Odometry package such as **FAST-LIO** or **Cartographer**.
    *   The node computes the pose of the robot and constructs a 3D Point-Cloud or a 2D occupancy grid map of the environment.
2.  **Navigation (Nav2 Stack):**
    *   Reads the generated `/map` and localizes the robot within it.
    *   Costmaps are calculated to represent obstacle safety margins.
    *   Path planners compute smooth routes, and collision avoidance algorithms generate velocity vectors ($v_x, v_y, \omega_{yaw}$) that are output to the robot bridge, driving the Go2-W autonomously.
