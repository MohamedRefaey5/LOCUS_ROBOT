import os
from launch import LaunchDescription
from launch_ros.actions import Node, LifecycleNode
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


 def generate_launch_description():


    pkg = get_package_share_directory('locus_description')


    map_file = os.path.join(

        os.path.expanduser('~'),

        'ros_projects', 'LOCUS', 'maps', 'locus_map.yaml'

    )

    amcl_config   = os.path.join(pkg, 'config', 'amcl.yaml')


    # ------------------------------------------------------------------

    # 1. Map Server — loads the saved map and publishes /map topic

    #    Lifecycle node: must be configured and activated

    # ------------------------------------------------------------------

    map_server = LifecycleNode(

        package='nav2_map_server',

        executable='map_server',

        name='map_server',

        namespace='',

        parameters=[{

            'use_sim_time': True,

            'yaml_filename': map_file

        }],

        output='screen'

    ) 
    # ------------------------------------------------------------------
    # 2. AMCL — particle filter localization
    #    Subscribes to /scan and /odom, publishes map->odom TF
    # ------------------------------------------------------------------
    amcl = LifecycleNode(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        namespace='',
        parameters=[amcl_config],
        output='screen'
    )

    # ------------------------------------------------------------------
    # 3. Lifecycle Manager — manages map_server and amcl lifecycle
    #    Automatically configures and activates both nodes
    # ------------------------------------------------------------------
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server', 'amcl']
        }],
        output='screen'
    )

    return LaunchDescription([
        map_server,
        amcl,
        lifecycle_manager,
    ])
