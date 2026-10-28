# ROS 2 Mobile Robot Simulation (Gazebo + RViz2)

A ROS 2 Humble Python package for a simulated four-wheel differential-drive robot. The repository includes a URDF robot description, a Gazebo Sim maze world, a ROS–Gazebo bridge, an RViz2 configuration, keyboard teleoperation, a telemetry publisher, a headlight service example, and a patrol action server.

> **Status:** The repository files and packaging paths have been reviewed and corrected. The commands below are the intended workflow; run them on your ROS 2/Gazebo installation to confirm runtime behavior. Gazebo plugin compatibility can vary with the installed Gazebo Sim release.

## Features

- Four-wheel robot described in `urdf/sim_robot_org.urdf`.
- Differential-drive plugin accepting velocity commands on `/cmd_vel`.
- Simulated GPU LiDAR and ROS `sensor_msgs/msg/LaserScan` scan bridge on `/scan`.
- Gazebo Sim maze world in `worlds/small_maze.sdf`.
- ROS–Gazebo bridges for clock, velocity, odometry, TF, LiDAR, and joint states.
- RViz2 launch configuration in `rviz/default.rviz`.
- Keyboard teleoperation node (`keyboard_teleop`).
- Example ROS 2 telemetry topic, SetBool service, and patrol action server.

## Repository layout

```text
ros2-mobile-robot-gazebo/
├── README.md
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
│   └── sim_mobile_robot
├── launch/
│   └── sim_robot.launch.py
├── urdf/
│   └── sim_robot_org.urdf
├── worlds/
│   └── small_maze.sdf
├── rviz/
│   └── default.rviz
├── sim_mobile_robot/
│   ├── __init__.py
│   ├── telemetry.py
│   ├── headlight.py
│   ├── patrol.py
│   └── teleop.py
└── tests/
    └── test_teleop.py
```

The `resource/sim_mobile_robot` marker is required by the ament Python package index. The launch file loads the world from the installed `worlds/` directory, so the SDF must be installed there. Keep the filenames and paths consistent when changing the launch or setup files.

## Requirements

These instructions target **Ubuntu 22.04 + ROS 2 Humble**. The simulation uses the `ros_gz_*` packages and Ignition-style message names in its bridge configuration, so use a Gazebo Sim version compatible with your ROS 2 Humble installation.

Install ROS 2 Humble first, then install the package tools and runtime dependencies:

```bash
sudo apt update
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-rosdep \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-bridge \
  ros-humble-robot-state-publisher \
  ros-humble-rviz2 \
  ros-humble-turtlesim
```

If `rosdep` has not been initialized on this computer, run:

```bash
sudo rosdep init
rosdep update
```

If `sudo rosdep init` reports that it is already initialized, do not repeat it.

## Installation and build

Open a terminal and source ROS 2:

```bash
source /opt/ros/humble/setup.bash
```

Create a workspace and clone this repository into its `src` directory:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/abdur-netizen/ros2-mobile-robot-gazebo.git
cd ~/ros2_ws
```

Install any dependencies declared in the package manifest:

```bash
rosdep install --from-paths src --ignore-src -r -y
```

Build the package:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select sim_mobile_robot
source install/setup.bash
```

For each new terminal, source both environments before using the package:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

If the build reports a missing resource marker or missing launch/world file, check that the files shown in the repository layout exist and that you are building from `~/ros2_ws`, not from the package directory.

## Launch the simulation

In a terminal where ROS 2 and the workspace have been sourced:

```bash
ros2 launch sim_mobile_robot sim_robot.launch.py
```

The launch file is intended to start:
1. `robot_state_publisher` using the URDF.
2. Gazebo Sim with the maze world.
3. The robot spawn process.
4. The ROS–Gazebo parameter bridge.
5. RViz2 using `rviz/default.rviz`.

Wait for Gazebo to finish loading before sending motion commands. If Gazebo or a node exits, read the first error in that terminal; later messages may only be consequences.

## Drive the robot with the keyboard

Open a **second interactive terminal**. Source ROS 2 and the workspace, then run:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run sim_mobile_robot keyboard_teleop
```

Controls:

| Key | Action |
|---|---|
| `W` | Drive forward |
| `S` | Drive backward |
| `A` | Rotate left |
| `D` | Rotate right |
| `Space` | Publish a stop command |
| `Q` | Stop and quit |

Default speeds are 0.25 m/s linear and 0.8 rad/s angular. The selected command persists until another key is pressed, so press **Space** to stop. The node also publishes a zero command when it exits. Run it in a terminal that accepts keyboard input; do not run it in the background without a TTY.

To inspect the velocity stream in another terminal:

```bash
ros2 topic echo /cmd_vel
```

## Useful topics, services, and actions

Names are taken from the source files and launch configuration. A topic may not appear until the corresponding node or simulation is running.

| Interface | Type | Purpose |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Robot velocity command |
| `/odom` | `nav_msgs/msg/Odometry` | Simulated odometry |
| `/scan` | `sensor_msgs/msg/LaserScan` | LiDAR scan |
| `/tf` | `tf2_msgs/msg/TFMessage` | Transform stream |
| `/joint_states` | `sensor_msgs/msg/JointState` | Wheel joint states |
| `/clock` | `rosgraph_msgs/msg/Clock` | Simulation clock |
| `/robot_telemetry` | `std_msgs/msg/String` | Example heartbeat messages |
| `/toggle_headlights` | `std_srvs/srv/SetBool` | Example headlight state service |
| `/patrol_routine` | `turtlesim/action/RotateAbsolute` | Example patrol action interface |

Inspect the graph:

```bash
ros2 topic list
ros2 node list
ros2 service list
ros2 action list
```

Echo telemetry (start its node first):

```bash
ros2 run sim_mobile_robot telemetry_node
```

In a different terminal:

```bash
ros2 topic echo /robot_telemetry
```

Call the example headlight service (start its node first):

```bash
ros2 run sim_mobile_robot headlight_node
```

In another terminal:

```bash
ros2 service call /toggle_headlights std_srvs/srv/SetBool "{data: true}"
ros2 service call /toggle_headlights std_srvs/srv/SetBool "{data: false}"
```

**Important:** `headlight.py` currently changes an internal Boolean and returns a response. It does not switch a Gazebo light or hardware output.

Run the patrol action server in one terminal:

```bash
ros2 run sim_mobile_robot patrol_node
```

Send a goal from another terminal:

```bash
ros2 action send_goal /patrol_routine turtlesim/action/RotateAbsolute "{theta: 1.57}" --feedback
```

**Important:** The patrol server currently uses the Turtlesim `RotateAbsolute` action interface as a demonstration, but publishes `Twist` messages to the mobile robot. Its goal angle is not used to calculate the movement. This should be replaced with a robot-specific action definition before relying on patrol behavior.

## Code walkthrough

### `launch/sim_robot.launch.py`

Looks up the installed package share directory, constructs paths to the URDF, world, and RViz configuration, and reads the URDF into the `robot_description` parameter. It launches the robot-state publisher, Gazebo Sim, a robot-spawn process, a parameter bridge, and RViz2. The bridge directions are specified in the arguments: command velocity is sent toward Gazebo, while odometry, clock, TF, LiDAR, and joint states are bridged back to ROS 2. The joint-state topic is remapped to `/joint_states`.

### `urdf/sim_robot_org.urdf`

Defines a box-shaped `base_link`, four wheel links and continuous joints, and a fixed LiDAR frame. The Gazebo tags configure a GPU LiDAR sensor and the differential-drive and joint-state-publisher systems. The differential-drive plugin uses the wheel joints, wheel separation and wheel radius to convert `/cmd_vel` into wheel motion and publishes odometry/TF in Gazebo. Validate wheel orientation, inertial values, collision geometry, and plugin names in the actual simulator if the robot does not move correctly.

### `worlds/small_maze.sdf`

Defines the `maze_world`, physics, user-command, scene-broadcast and sensor systems, a directional light, a ground plane, and static perimeter/interior walls. The LiDAR sensor requires a functioning rendering/sensor system. The world name is also used by the joint-state topic path in the URDF and launch bridge; if you rename the world or spawned model, update those paths consistently.

### `sim_mobile_robot/telemetry.py`

Creates a node named `telemetry_publisher`. It advertises `/robot_telemetry` as a `std_msgs/msg/String` publisher with queue depth 10, creates a timer with a 2-second period, and publishes a heartbeat string with an incrementing counter. It is a demonstration of a periodic publisher, not real sensor or health telemetry.

### `sim_mobile_robot/headlight.py`

Creates a node named `headlight_service` and registers `/toggle_headlights` with the standard `SetBool` service type. A request with `data: true` sets the node's `lights_on` state to true; false sets it to false. The callback returns `success` and a human-readable message. No Gazebo service, light entity, or physical GPIO is controlled yet.

### `sim_mobile_robot/patrol.py`

Creates an asynchronous action server on `/patrol_routine` using `turtlesim/action/RotateAbsolute`. It publishes angular velocity 0.5 rad/s to `/cmd_vel`, sends five feedback updates using the interface's valid `delta` field, and awaits between updates so cancellation can be processed. A `finally` block publishes a zero `Twist` when the action completes or is canceled. Limitations: the requested `theta` is still ignored, and the fixed-duration rotation is not a true rotate-to-angle controller. Treat this as a prototype only, not a reliable safety-critical patrol controller.

### `sim_mobile_robot/teleop.py`

Runs in an interactive terminal, maps W/S/A/D and Space to linear/angular velocity pairs, and publishes `geometry_msgs/msg/Twist` on `/cmd_vel`. Q exits after sending a zero command; the terminal settings are restored in the cleanup path. Because the selected command persists, the user must press Space to stop after a movement key. This is a simple teaching controller, not a safety-rated teleoperation system.

## Troubleshooting

### Package cannot be found

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 pkg prefix sim_mobile_robot
```

If no prefix is returned, rebuild from the workspace root and check the build output.

### Launch fails to find the world

Check that `worlds/small_maze.sdf` exists in the source tree and was installed:

```ls ~/ros2_ws/src/ros2-mobile-robot-gazebo/worlds
ls ~/ros2_ws/install/sim_mobile_robot/share/sim_mobile_robot/worlds
```

### Robot appears but does not move

Check that the keyboard node is publishing and the bridge/plugin are running:

```bash
ros2 topic echo /cmd_vel
ros2 topic echo /odom
ros2 topic echo /scan
```

If `/cmd_vel` changes but odometry does not, inspect Gazebo plugin startup errors, wheel joint names, bridge directions, and Gazebo version compatibility.

### RViz2 reports a missing transform or robot model

Check that `robot_state_publisher` is running, `/tf` and `/joint_states` are present, and the RViz fixed frame exists. The provided RViz config uses `base_link` as the fixed frame; use `odom` only after confirming that the odometry-to-base transform is available.

### ROS-Gazebo bridge types fail to load

This project uses `ignition.msgs.*` bridge type strings. If your installed Gazebo uses `gz.msgs.*` names instead, update the bridge configuration for that distribution rather than mixing bridge syntax from different Gazebo releases.

## Tests

Run the small unit tests for keyboard key mapping:

```bash
cd ~/ros2_ws/src/ros2-mobile-robot-gazebo
python3 -m pytest -q
```

These tests cover key-to-velocity mapping only. They do not replace an end-to-end test of Gazebo, RViz2, the robot model, or the ROS–Gazebo bridge.

## Known limitations and next steps

- The headlight service is not connected to a simulated light.
- The patrol action uses a Turtlesim action type and does not yet use the requested angle to stop at a target heading.
- Keyboard control is terminal-based and not safety-rated.
- The launch stack and Gazebo plugin configuration must be tested on the target ROS 2/Gazebo installation.
- Add screenshots or short recordings of successful launch, RViz2, LiDAR data, odometry, and keyboard control after runtime validation.

## License

The package metadata declares Apache-2.0. Add the corresponding `LICENSE` file before distributing the project under that license.
