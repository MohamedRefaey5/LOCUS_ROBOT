import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_locus_description = get_package_share_directory('locus_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    urdf_file = os.path.join(pkg_locus_description, 'urdf', 'locus_robot.urdf.xacro')
    robot_description = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )
    return LaunchDescription([

        # 1. Launch Gazebo Harmonic
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={'gz_args': '-r empty.sdf'}.items()
        ),

        # 2. Publish robot TF
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': True
            }],
            output='screen'
        ),

        # 3. Spawn robot in Gazebo
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

        # 4. Bridge ROS <-> Gazebo topics
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
                '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            ],
            output='screen'
        ),

        # 5. Fix lidar frame_id mismatch
        # Gazebo Harmonic ignores <frame_id> inside sensor and auto-generates
        # a long name from the model hierarchy. This zero-offset static transform
        # bridges the two names so RViz2 can display the scan correctly.
        # If Gazebo changes the auto-name, check with:
        #   ros2 topic echo /scan --field header --once
        # and update the last argument below to match.
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
	Node(
   	 package='topic_tools',
  	  executable='throttle',
   	 name='joint_states_throttle',
   	 arguments=[
       		'messages',
       		'/joint_states',
        	'50',
        	'/joint_states'
  	  ],
  	  output='screen'
	),
    ])
