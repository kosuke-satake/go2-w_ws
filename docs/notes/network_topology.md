# Technical Note: Go2-W Network Topology & DDS Routing

locomotion and sensing on the Unitree Go2-W are distributed across several onboard processors communicating over an internal local area network. Understanding the IP map and DDS configurations is essential for routing sensor topics and locomotion command packages.

---

## 1. Network IP Mapping

By default, the Go2-W operates on the **`192.168.123.0/24`** subnet when connected via Ethernet or the onboard Wi-Fi Access Point.

```
       +-----------------------------------------------------------+
       |                  Unitree Go2-W Robot                      |
       |                                                           |
       |  +--------------------+        +-----------------------+  |
       |  | Motion CPU         |        | Onboard Jetson        |  |
       |  | (Locomotion/SDK)   | <====> | (LiDAR, Camera, ROS)  |  |
       |  | IP: 192.168.123.161|        | IP: 192.168.123.15    |  |
       |  +--------------------+        +-----------------------+  |
       +-----------------------------------------------------------+
                                  ^
                                  |
                                  v  (Wi-Fi: wlp0s20f3 / Ethernet)
                       +---------------------+
                       | Developer Thinkpad  |
                       | IP: 192.168.123.x   |
                       +---------------------+
```

| Device Name | IP Address | Primary Role |
| :--- | :--- | :--- |
| **Motion CPU** | `192.168.123.161` | Runs real-time balance algorithms and low-level CAN bus motor interfaces. Standard SDK port target. |
| **Onboard Jetson** | `192.168.123.15` | NVIDIA Jetson Orin NX. Processes exteroceptive data (3D LiDAR, cameras) and runs the onboard ROS 2 nodes. |
| **Developer Thinkpad** | `192.168.123.X` | Assigned dynamically by the robot's DHCP server when connected to the robot's Wi-Fi AP or Ethernet port. |

---

## 2. CycloneDDS & Port Routing

ROS 2 and the Unitree SDK communicate over **DDS (Data Distribution Service)**. DDS uses multicast IP addresses to automatically discover other nodes on the network.

### Standard Port Ranges
DDS discovery and user data packets occupy ports determined by the **DDS Domain ID**. The default domain ID for ROS 2 is `0`.

The standard mathematical mapping for DDS ports:
*   **Multicast Discovery Port:** $7400 + (250 \times \text{Domain ID})$ (for Domain `0` = `7400`)
*   **Unicast Data Port:** $7410 + (250 \times \text{Domain ID}) + (2 \times \text{Participant ID})$

If you are running tests on a local network with other robots or developers, configure the environment variable `ROS_DOMAIN_ID` to isolate your node streams:
```bash
export ROS_DOMAIN_ID=15  # Avoids collision with default domain 0
```

---

## 3. CycloneDDS Configuration File (`cyclonedds.xml`)

To bind your Python SDK scripts to the correct network interface and prevent high-bandwidth camera/LiDAR data from saturating your control connection, configure a custom local loopback xml configuration.

Create a `cyclonedds.xml` file inside your workspace config and export its path before launching scripts:

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<CycloneDDS xmlns="https://cdds.io/config">
  <Domain id="any">
    <General>
      <!-- wlp0s20f3 is the Thinkpad Wi-Fi interface connected to the robot -->
      <NetworkInterfaceAddress>wlp0s20f3</NetworkInterfaceAddress>
      <AllowMulticast>true</AllowMulticast>
    </General>
    <Discovery>
      <Peers>
        <!-- Route unicast packets directly to the Motion CPU and Jetson -->
        <Peer address="192.168.123.161"/>
        <Peer address="192.168.123.15"/>
      </Peers>
    </Discovery>
  </Domain>
</CycloneDDS>
```

Export the configuration in your terminal prior to running scripts:
```bash
export CYCLONEDDS_URI=file:///home/user/Developer/Projects/go2-w/go2-w_ws/cyclonedds.xml
```
