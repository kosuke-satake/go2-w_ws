# Step 6: Onboard Jetson Deployment

This directory covers configurations and deployment workflows to run your custom ROS 2 driver nodes, SLAM maps, or trained AI control policies directly on the Go2-W's onboard **NVIDIA Jetson Orin NX** processor.

---

## 1. Remote SSH Execution & Syncing

The onboard Jetson acts as a standalone Linux computer on the local subnet (`192.168.123.15`). You can connect to it directly via SSH using the robot's network:

```bash
ssh unitree@192.168.123.15
```

### Syncing Files with `rsync`
Instead of copying files manually, you can automate synchronization using `rsync` from your Thinkpad terminal. This copies only the modified files to the Jetson:

```bash
rsync -avz --exclude '.venv' --exclude 'build' --exclude 'install' --exclude 'log' \
  ~/Developer/Projects/go2-w/go2-w_ws/ \
  unitree@192.168.123.15:~/go2-w_ws/
```

---

## 2. Onboard Compilation vs. Cross-Compilation

When deploying ROS 2 nodes to the Jetson:
*   **Onboard Compilation (Recommended):** Copy the source files to the Jetson and run `colcon build` directly on the Orin NX. Since the Jetson has a 6-core ARM CPU and GPU, it can compile python/C++ nodes quickly.
*   **Cross-Compilation:** Building code on your x86_64 Thinkpad for the arm64 architecture of the Jetson. This is only necessary for heavy C++ packages or complex neural network binaries.

---

## 3. Autostart & Systemd Services

To make your custom nodes run automatically whenever the robot dog boots up:
1.  Write a bash startup script to source ROS 2 and set the DDS environment.
2.  Define a Linux **systemd service** file (e.g., `go2_w_startup.service`) inside `/etc/systemd/system/` on the Jetson.
3.  Enable the service:
    ```bash
    sudo systemctl enable go2_w_startup.service
    ```
