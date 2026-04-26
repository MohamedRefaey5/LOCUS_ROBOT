import os
import xacro
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg = get_package_share_directory('locus_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world_file = os.path.join(pkg, 'worlds', 'locus_world.sdf')
    urdf_file  = os.path.join(pkg, 'urdf', 'locus_robot.urdf.xacro')
    controllers_yaml = os.path.join(pkg, 'config', 'locus_controllers.yaml')

    # Pre-process xacro at launch time — more reliable than Command substitution
    doc = xacro.process_file(urdf_file)
    robot_desc = doc.toprettyxml(indent='  ')

    # ------------------------------------------------------------------
    # 1. Gazebo Harmonic
    # ------------------------------------------------------------------
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    # ------------------------------------------------------------------
    # 2. Robot State Publisher
    #    Publishes TF transforms from URDF joint definitions
    # ------------------------------------------------------------------
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True
        }],
        output='screen'
    )

    # ------------------------------------------------------------------
    # 3. Spawn robot into Gazebo
    #    Using -string (pre-processed URDF string) is more reliable
    #    than -topic because it doesn't depend on topic timing
    # ------------------------------------------------------------------
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-string', robot_desc,
            '-name',   'locus_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.07',   # slightly above ground to avoid spawn collision
        ],
        output='screen'
    )

    # ------------------------------------------------------------------
    # 4. Load joint_state_broadcaster after spawn completes
    #    OnProcessExit ensures controllers load only after robot exists
    # ------------------------------------------------------------------
    load_joint_state_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=[
                        'joint_state_broadcaster',
                        '--controller-manager', '/controller_manager'
                    ],
                    output='screen'
                )
            ]
        )
    )

    # ------------------------------------------------------------------
    # 5. Load diff_drive_controller after joint_state_broadcaster
    #    Pass our yaml so wheel names and params are loaded correctly
    # ------------------------------------------------------------------
    load_diff_drive_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=[
                        'diff_drive_controller',
                        '--controller-manager', '/controller_manager',
                        '--param-file', controllers_yaml
                    ],
                    output='screen'
                )
            ]
        )
    )

    # ------------------------------------------------------------------
    # 6. Bridge Gazebo <-> ROS2
    #    /scan and /imu come from Gazebo sensors
    #    /clock must be bridged for use_sim_time to work
    #    NOTE: /odom and /tf come from diff_drive_controller directly
    #    into ROS2 — no bridge needed for those
    # ------------------------------------------------------------------
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
        ],
        output='screen'
    )

    # ------------------------------------------------------------------
    # 7. Static transform: fix LiDAR frame name
    #    Gazebo Harmonic auto-generates frame name from model hierarchy
    #    This zero-offset transform bridges the two names for RViz2
    # ------------------------------------------------------------------
    lidar_frame_fix = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='lidar_frame_fix',
        arguments=[
            '--x', '0', '--y', '0', '--z', '0',
            '--roll', '0', '--pitch', '0', '--yaw', '0',
            '--frame-id', 'lidar_link',
            '--child-frame-id', 'locus_robot/base_footprint/gpu_lidar'
        ],
        output='screen'
    )

    # ------------------------------------------------------------------
    # 8. cmd_vel relay
    #    Teleop publishes plain Twist on /cmd_vel
    #    diff_drive_controller expects TwistStamped
    #    This node converts between the two
    # ------------------------------------------------------------------
    cmd_vel_relay = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='locus_basics',
                executable='cmd_vel_relay',
                name='cmd_vel_relay',
                parameters=[{'use_sim_time': True}],
                output='screen'
            )
        ]
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        load_joint_state_broadcaster,
        load_diff_drive_controller,
        bridge,
        lidar_frame_fix,
        cmd_vel_relay,
    ])
