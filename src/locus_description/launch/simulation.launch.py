import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    pkg = get_package_share_directory('locus_description')

    # Include the full Gazebo launch
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'gazebo.launch.py')
        )
    )

    # Include the RViz2 display launch
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'rviz.launch.py')
        )
    )

    return LaunchDescription([
        gazebo_launch,
        rviz_launch,
    ])
