# Workspace Progress Log

This log documents the developmental milestones and configuration updates for the Unitree Go2-W wheeled-quadruped project. Entries are recorded in reverse chronological order.

---

## [2026-06-05] - Phase 1: Locomotion Control & Telemetry Scripts
*   **Milestone:** Completed custom high/low-level locomotion scripts, established CycloneDDS routing config, and verified linter configuration.
*   **Details:**
    *   Created `cyclonedds.xml` to bind DDS network traffic to the Wi-Fi network interface (`wlp0s20f3`) and peer directly with the Motion CPU and Jetson.
    *   Corrected Python SDK library import paths from `unitree_sdk2` to `unitree_sdk2py` across all scripts.
    *   Developed `01_learning_python_sdk/scripts/high_level_attitude.py` using the SportClient to stand the robot up and execute pitch, roll, and yaw sweeps.
    *   Developed `01_learning_python_sdk/scripts/low_level_leg_sine.py` to command a single joint (FL_calf) in a safe sine wave sweep while holding other joints and wheels damped.
    *   Configured `.vscode/settings.json` on the host and target to resolve Pylance import path resolution issues.
    *   Structured project development under the task-oriented branch `feat/locomotion-telemetry`.

---

## [2026-06-05] - Workspace Verification & SDK Installation
*   **Milestone:** Fully configured and verified the Python SDK environment on the Ubuntu Thinkpad.
*   **Details:**
    *   Resolved the CycloneDDS build dependency on Ubuntu 24.04 by compiling `cyclonedds` (release `0.10.x`) from source and installing it locally to `~/cyclonedds/install`.
    *   Linked and installed the `unitree_sdk2_python` library in editable mode (`pip install -e`) inside the project virtual environment `.venv`.
    *   Moved the local SDK copy to `~/Developer/Projects/go2-w/unitree_sdk2_python` to maintain clean directory separation.
    *   Established passwordless SSH key-based authentication between the developer Macbook and the Thinkpad, enabling direct, instant VS Code Remote-SSH sessions.
*   **Documentation Added:**
    *   [Environment Setup Note](file:///Users/kosuke/Developer/Projects/go2-w/go2-w_ws/docs/notes/01_env_setup.md)
    *   [Network Topology Map](file:///Users/kosuke/Developer/Projects/go2-w/go2-w_ws/docs/notes/network_topology.md)
    *   [Safety Protocols Reference](file:///Users/kosuke/Developer/Projects/go2-w/go2-w_ws/docs/notes/safety_protocols.md)

---

## [2026-05-29] - Repository Initialization
*   **Milestone:** Workspace structure and core configuration files initialized.
*   **Details:**
    *   Set up standard config templates: `.gitignore`, `.gitattributes`, `.editorconfig`, and `pyproject.toml` (for Ruff formatting).
    *   Wrote the foundational workspace memory guide detailing kinematics derivations ([GEMINI.md](file:///Users/kosuke/Developer/Projects/go2-w/go2-w_ws/GEMINI.md)).
