import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg = get_package_share_directory('locus_description')

    nav2_params = os.path.join(pkg, 'config', 'nav2_params.yaml')
    map_file    = os.path.join(
        os.path.expanduser('~'),
        'ros_projects', 'LOCUS', 'maps', 'locus_map.yaml'
    )

    return LaunchDescription([

        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[nav2_params, {'yaml_filename': map_file}],
            output='screen'
        ),

        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            parameters=[nav2_params],
            output='screen'
        ),

        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            parameters=[nav2_params],
            output='screen'
        ),

        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            parameters=[nav2_params],
            remappings=[('cmd_vel', '/diff_drive_controller/cmd_vel')],
            output='screen'
        ),

        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            parameters=[nav2_params],
            output='screen'
        ),

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            parameters=[nav2_params],
            output='screen'
        ),

        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            parameters=[nav2_params],
            output='screen'
        ),

        # Lifecycle Manager activates all nodes above
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            parameters=[{
                'use_sim_time': True,
                'autostart': True,
                'node_names': [
                    'map_server',
                    'amcl',
                    'planner_server',
                    'controller_server',
                    'behavior_server',
                    'bt_navigator',
                    'velocity_smoother',
                ]
            }],
            output='screen'
        ),
    ])
