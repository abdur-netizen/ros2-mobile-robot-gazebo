import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('sim_mobile_robot')
    
    # Path configurations
    urdf_file = os.path.join(pkg_share, 'urdf', 'sim_robot_org.urdf')
    world_file = os.path.join(pkg_share, 'worlds', 'small_maze.sdf')
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'default.rviz')

    # Read URDF file contents
    with open(urdf_file, 'r') as infp:
        robot_description_config = infp.read()

    # 1. Robot State Publisher Node
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_config,
            'use_sim_time': True
        }]
    )

    # 2. Ignition Gazebo Launch
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    # 3. Spawn Robot in Gazebo (Elevated Z=0.2 to prevent ground/mesh self-collisions)
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'sim_mobile_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.2'
        ],
        output='screen'
    )

    # 4. ROS 2 <-> Gazebo Bridge Node
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Clock Bridge
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            # Velocity Commands Bridge
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            # Odometry Bridge
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            # TF Bridge
            '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
            # LiDAR Scan Bridge
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            # Joint States Bridge
            '/world/maze_world/model/sim_mobile_robot/joint_state@sensor_msgs/msg/JointState[ignition.msgs.Model'
        ],
        remappings=[
            ('/world/maze_world/model/sim_mobile_robot/joint_state', '/joint_states')
        ],
        output='screen'
    )

    # 5. RViz2 Node
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        node_robot_state_publisher,
        gz_sim,
        spawn_robot,
        bridge,
        rviz
    ])
