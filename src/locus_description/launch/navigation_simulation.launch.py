import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg = get_package_share_directory('locus_description')

    return LaunchDescription([

        # Gazebo + robot + sensors
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg, 'launch', 'gazebo.launch.py')
            )
        ),

        # Nav2 full stack (AMCL + planners + controllers)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg, 'launch', 'navigation.launch.py')
            )
        ),

        # RViz2
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg, 'launch', 'rviz.launch.py')
            )
        ),
    ])
