import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_locus_description = get_package_share_directory('locus_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    urdf_file  = os.path.join(pkg_locus_description, 'urdf', 'locus_robot.urdf.xacro')
    world_file = os.path.join(pkg_locus_description, 'worlds', 'locus_world.sdf')

    robot_description = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )

    return LaunchDescription([

        # 1. Gazebo Harmonic
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={'gz_args': f'-r {world_file}'}.items()
        ),

        # 2. Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': True
            }],
            output='screen'
        ),

        # 3. Spawn robot
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-topic', 'robot_description',
                '-name', 'locus_robot',
                '-z', '0.1',
            ],
            output='screen'
        ),

        # 4. Bridge — only sensors, odom/tf come from ros2_control
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            ],
            output='screen'
        ),

        # 5. Fix lidar frame_id
        Node(
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
        ),

        # 6. Joint State Broadcaster
        TimerAction(
            period=3.0,
            actions=[
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
        ),

        # 7. Diff Drive Controller — publishes odom TF and /odom topic
        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=[
                        'diff_drive_controller',
                        '--controller-manager', '/controller_manager',
                        '--param-file',
                        os.path.join(
                            get_package_share_directory('locus_description'),
                            'config', 'locus_controllers.yaml'
                        )
                    ],
                    output='screen'
                )
            ]
        ),

        # 8. cmd_vel relay: Twist -> TwistStamped
        TimerAction(
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
        ),

    ])
