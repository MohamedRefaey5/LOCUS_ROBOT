import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    pkg_locus_description = get_package_share_directory('locus_description')
    # Use ros_gz_sim instead of gazebo_ros
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    urdf_file = os.path.join(pkg_locus_description, 'urdf', 'locus_robot.urdf.xacro')
    
    # Jazzy/Harmonic uses .sdf or .world files. 
    # If your world file is empty, 'empty.sdf' is a safe default for Harmonic.
    world_file = os.path.join(pkg_locus_description, 'worlds', 'empty.world') 

    robot_description = Command(['xacro ', urdf_file])

    return LaunchDescription([

        # 1. Launch Gazebo Harmonic (Jazzy's default)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
            ),
            # '-r' tells Gazebo to run the physics immediately
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

        # 3. Spawn robot in Gazebo Sim
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
        
        # 4. Bridge (Crucial for Jazzy!)
        # This allows ROS 2 and Gazebo to talk to each other
        # In your launch file:
	Node(
    	package='ros_gz_bridge',
    	executable='parameter_bridge',
    	arguments=[
        	'/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        	'/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        	'/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        	'/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
        	'/imu@sensor_msgs/msg/Imu[gz.msgs.IMU'
    	],
    	output='screen'
	)
    ])
