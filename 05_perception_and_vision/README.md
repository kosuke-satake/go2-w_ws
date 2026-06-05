# Step 5: Perception & Vision Pipelines

This directory covers processing exteroceptive sensor streams from the Unitree Go2-W, including the wide-angle camera and the 3D LiDAR.

---

## 1. 3D LiDAR Point Cloud Processing

The Go2-W is equipped with an onboard 3D LiDAR that outputs high-frequency range measurements. This data is converted by the LiDAR driver node into a **Point Cloud** published on standard ROS 2 topics (e.g., `/point_cloud` or `/velodyne_points` containing `sensor_msgs/msg/PointCloud2` message types).

### Processing Pipelines
To use this point cloud data for obstacle negotiation:
1.  **Voxel Grid Filtering:** Downsamples the point cloud coordinates to reduce CPU load.
2.  **Pass-Through Filtering:** Clips point coordinates outside the robot's region of interest (e.g., ignoring points too high or too far away).
3.  **Ground Plane Segmentation:** Separates the floor points (using algorithms like RANSAC plane fitting) from actual obstacles like walls or chairs.

---

## 2. Onboard Camera & Vision Models

The wide-angle HD camera streams video frames. These are captured by the SDK listener and can be processed using:
*   **OpenCV:** For image correction, thresholding, and camera calibration parameters.
*   **YOLO (You Only Look Once):** For real-time object detection (detecting targets, humans, or waypoints) running on either your Thinkpad or the robot's Jetson processor.

---

## 3. Implementation Roadmap
1.  **`05_perception_and_vision/src/point_cloud_filter.py`:** Write a ROS 2 node to subscribe to the raw point cloud topic, apply a voxel downsampling filter, and republish the filtered cloud.
2.  **`05_perception_and_vision/src/target_tracker.py`:** Implement a simple target tracking node using OpenCV to locate a colored ball and calculate relative Cartesian coordinates for the sport client to track.
