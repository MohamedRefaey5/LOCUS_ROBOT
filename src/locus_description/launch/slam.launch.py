import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    pkg_locus = get_package_share_directory('locus_description')
    pkg_slam  = get_package_share_directory('slam_toolbox')

    slam_config = os.path.join(pkg_locus, 'config', 'slam_toolbox.yaml')

    return LaunchDescription([

        # Use slam_toolbox's own launch file — handles lifecycle correctly
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_slam, 'launch', 'online_sync_launch.py')
            ),
            launch_arguments={
                'slam_params_file': slam_config,
                'use_sim_time': 'true'
            }.items()
        ),

    ])
