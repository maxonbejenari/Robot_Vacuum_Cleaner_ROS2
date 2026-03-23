#  Robot Vacuum Cleaner — Autonomous Mobile Robot

A fully simulated autonomous vacuum cleaner robot built with ROS2 Jazzy and Gazebo, featuring SLAM-based mapping, NAV2 navigation, and YOLO object detection.

---

##  Table of Contents

- [Overview](#overview)
- [Demo](#demo)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [YOLO Object Detection](#yolo-object-detection)
- [NAV2 Navigation](#nav2-navigation)
- [Roadmap](#roadmap)

---

## Overview

This project is a prototype autonomous vacuum cleaner robot developed entirely in simulation. The robot was designed in **Onshape**, converted to URDF using **onshape-to-robot**, simulated in **Gazebo**, and equipped with:

- **SLAM Toolbox** for real-time mapping and localization
- **NAV2** for autonomous point-to-point navigation
- **YOLOv8** for real-time object detection, trained on custom classes (e.g. cube detection)

The goal is to simulate the full software stack of a commercial robot vacuum cleaner — from sensor fusion and mapping to coverage path planning and autonomous navigation.

---

## Demo

>  SLAM mapping the room in real time

>  Autonomous navigation with NAV2

>  YOLO object detection on camera feed


## Tech Stack

| Component | Technology |
|---|---|
| Robot Design | [Onshape](https://www.onshape.com/) CAD |
| URDF Generation | [onshape-to-robot](https://github.com/Rhoban/onshape-to-robot) |
| Simulation | [Gazebo Harmonic](https://gazebosim.org/) |
| Robot Middleware | [ROS2 Jazzy](https://docs.ros.org/en/jazzy/) |
| SLAM | [SLAM Toolbox 2.8.x](https://github.com/SteveMacenski/slam_toolbox) |
| Navigation | [NAV2](https://nav2.org/) |
| Object Detection | [YOLOv8](https://github.com/ultralytics/ultralytics) |
| Controller | MPPI Controller (Model Predictive Path Integral) |
| Path Planner | NavFn (A*) |

---

## Project Structure

```
robot_vacuum_ws/
└── src/
    ├── robot_description/          # Robot URDF, Gazebo world, launch files
    │   ├── launch/
    │   │   ├── gz_custom.launch.py # Main simulation launch
    │   │   └── rviz.launch.py      # RViz visualization
    |   |   |__ gz_empty.launch.py  # Empty world gazebo launch
    │   ├── urdf/
    │   │   ├── robot_vacuum.urdf.xacro
    │   │   ├── models/             # base, wheels, camera, lidar
    │   │   └── gazebo/             # Gazebo plugins and properties
    │   ├── worlds/
    │   │   └── living_room.sdf     # Custom simulation environment
    │   └── yaml/
    │       └── gazebo_bridge.yaml  # ROS2 ↔ Gazebo topic bridge config
    │
    ├── yolo_pkg/                   # YOLO object detection node
    │   └── yolo_pkg/
    │       ├── yolo_node.py        # ROS2 node — runs inference on camera feed
    │       └── data_collector.py   # Collects training data from simulation
    │
    └── nav2_vacuum/                # NAV2 navigation package
        ├── config/
        │   ├── mapper_params.yaml  # SLAM Toolbox configuration
        │   └── nav2_params.yaml    # Full NAV2 stack configuration
        ├── maps/
        │   ├── my_map.yaml         # Saved map metadata
        │   └── my_map.pgm          # Saved map image
        └── launch/
            ├── slam.launch.py      # SLAM mapping mode
            └── nav2.launch.py      # Navigation with saved map
```

---

## Getting Started

### Prerequisites

- Ubuntu 24.04
- ROS2 Jazzy
- Gazebo Harmonic
- Python 3.10+

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/robot_vacuum_cleaner.git
cd robot_vacuum_ws

# Install ROS2 dependencies
sudo apt update
sudo apt install \
  ros-jazzy-slam-toolbox \
  ros-jazzy-nav2-bringup \
  ros-jazzy-nav2-common \
  ros-jazzy-teleop-twist-keyboard \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-ros-gz-sim -y

# Install Python dependencies
pip install ultralytics opencv-python

# Build the workspace
colcon build
source install/setup.bash
```

---

## Usage

### 1. Launch Simulation

```bash
ros2 launch robot_description gz_custom.launch.py
```

### 2. SLAM Mapping — Build the Map

```bash
# Terminal 2 — start SLAM
ros2 launch nav2_vacuum slam.launch.py

# Terminal 3 — control robot manually to explore the room
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Terminal 4 — save the map when done
ros2 run nav2_map_server map_saver_cli -f src/nav2_vacuum/maps/my_map
```

### 3. Autonomous Navigation — Use Saved Map

```bash
# Terminal 2 — start NAV2 with saved map
ros2 launch nav2_vacuum nav2.launch.py
```

In RViz:
1. Click **2D Pose Estimate** → click on the map where the robot is located
2. Click **2D Goal Pose** → click on any free (white) area on the map
3. The robot navigates autonomously, avoiding obstacles in real time

### 4. YOLO Object Detection

```bash
# Terminal 2 — start YOLO detection node
ros2 run yolo_pkg detect
```

The node subscribes to `/camera/image_raw` and publishes detections in real time.

---

## YOLO Object Detection

The YOLO model was trained on custom data collected directly from the Gazebo simulation using the `data_collector.py` node.

### Training the Model

```bash
# Collect training data from simulation
ros2 run yolo_pkg data_collector

# Train YOLOv8 on collected data
yolo train data=dataset.yaml model=yolov8n.pt epochs=50 imgsz=640
```
## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

Built as a learning project to explore the full robotics software stack — from mechanical design to autonomous navigation.
