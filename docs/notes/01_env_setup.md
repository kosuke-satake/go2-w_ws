# Technical Note 01: Environment Setup & SDK Installation

This note records the step-by-step procedure required to configure a fresh Ubuntu 24.04 environment to interface with the Unitree Go2-W Python SDK. Refer to this document to rebuild or clone the environment on a new machine.

---

## 1. System Specifications & Pre-requisites

The reference host environment was configured with the following characteristics:
*   **Operating System:** Ubuntu 24.04.4 LTS (Noble Numbat)
*   **Active Host Username:** `user`
*   **Target Development Directory:** `~/Developer/Projects/go2-w/`
*   **Core Systems Installed:** `git`, `python3-pip`, `python3-venv`, `cmake`, `build-essential`

---

## 2. Compiling Eclipse CycloneDDS from Source

The Unitree Python SDK relies on Python bindings for **CycloneDDS** (0.10.x). Python cannot build the bindings wheel if the underlying C++ CycloneDDS libraries are missing.

### Step-by-Step Compilation Protocol
Run the following commands to clone, configure, build, and install the library locally:

1.  **Clone the target release branch:**
    ```bash
    git clone https://github.com/eclipse-cyclonedds/cyclonedds.git ~/cyclonedds -b releases/0.10.x
    ```

2.  **Generate the build structure:**
    ```bash
    cd ~/cyclonedds
    mkdir -p build install
    cd build
    ```

3.  **Configure the build parameters via CMake:**
    Define the custom install directory using `-DCMAKE_INSTALL_PREFIX` so we do not pollute the Ubuntu system directories:
    ```bash
    cmake .. -DCMAKE_INSTALL_PREFIX=../install
    ```

4.  **Compile and install:**
    ```bash
    cmake --build . --target install
    ```
    This outputs the compiled headers and `.so` files directly into `/home/user/cyclonedds/install/`.

---

## 3. Creating the Workspace & Python Virtual Environment

To prevent conflicts with Ubuntu's system-managed Python packages, run all Python operations inside a local virtual environment (`.venv`).

1.  **Navigate to the workspace folder:**
    ```bash
    cd ~/Developer/Projects/go2-w/go2-w_ws
    ```

2.  **Initialize the virtual environment:**
    ```bash
    python3 -m venv .venv
    ```

3.  **Activate the virtual environment:**
    ```bash
    source .venv/bin/activate
    ```

---

## 4. Installing the Unitree SDK 2 Python Bindings

With the virtual environment active and CycloneDDS compiled, link the Unitree SDK repository using **pip editable mode** (`-e`). This allows you to modify the library code if needed without re-installing it.

1.  **Clone the SDK repository into your developer libraries folder:**
    ```bash
    cd ~/Developer/Projects/go2-w/
    git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
    ```

2.  **Export the CycloneDDS path and execute pip install:**
    Activate your workspace virtual environment, set the environment variable pointing to your custom CycloneDDS compilation path, and run the install:
    ```bash
    cd ~/Developer/Projects/go2-w/go2-w_ws
    source .venv/bin/activate
    
    # Point pip to the compiled C++ headers
    export CYCLONEDDS_HOME="/home/user/cyclonedds/install"
    
    # Install in editable mode
    pip install -e ~/Developer/Projects/go2-w/unitree_sdk2_python
    ```

### Verifying the Installation
To confirm the packages are successfully linked inside the virtual environment:
```bash
pip list
```
The output should list:
*   `unitree_sdk2py` pointing to the editable path `~/Developer/Projects/go2-w/unitree_sdk2_python`
*   `cyclonedds` (version `0.10.2` or equivalent)
*   `numpy` and `opencv-python`
