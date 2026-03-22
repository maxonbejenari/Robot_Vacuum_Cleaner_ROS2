import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, TimerAction,
                            IncludeLaunchDescription)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from lifecycle_msgs.msg import Transition


def generate_launch_description():

    nav2_vacuum_dir = get_package_share_directory('nav2_vacuum')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    map_yaml_file = os.path.join(
        nav2_vacuum_dir, 'maps', 'my_map.yaml'
    )
    nav2_params_file = os.path.join(
        nav2_vacuum_dir, 'config', 'nav2_params.yaml'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use Gazebo simulation clock'
    )

    # Step 1 — Start map_server first as standalone node
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            nav2_params_file,
            {
                'use_sim_time': use_sim_time,
                'yaml_filename': map_yaml_file,
            }
        ],
    )

    # Step 2 — Configure and activate map_server after 3 seconds
    configure_map_server = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_map',
                output='screen',
                parameters=[{
                    'use_sim_time': use_sim_time,
                    'autostart': True,
                    'node_names': ['map_server'],
                }],
            )
        ]
    )

    # Step 3 — Start AMCL after map_server is active (8 seconds total)
    amcl_node = TimerAction(
        period=8.0,
        actions=[
            Node(
                package='nav2_amcl',
                executable='amcl',
                name='amcl',
                output='screen',
                parameters=[
                    nav2_params_file,
                    {'use_sim_time': use_sim_time}
                ],
            )
        ]
    )

    # Step 4 — Activate AMCL after it starts (12 seconds total)
    activate_amcl = TimerAction(
        period=12.0,
        actions=[
            Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_localization',
                output='screen',
                parameters=[{
                    'use_sim_time': use_sim_time,
                    'autostart': True,
                    'node_names': ['amcl'],
                }],
            )
        ]
    )

    # Step 5 — Start full NAV2 navigation after localization is ready
    nav2_navigation = TimerAction(
        period=20.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
                ),
                launch_arguments={
                    'use_sim_time': use_sim_time,
                    'params_file': nav2_params_file,
                    'autostart': 'true',
                }.items()
            )
        ]
    )

    return LaunchDescription([
        declare_use_sim_time,
        map_server_node,       # starts immediately
        configure_map_server,  # activates map_server at 3s
        amcl_node,             # starts amcl at 8s
        activate_amcl,         # activates amcl at 12s
        nav2_navigation,       # starts full navigation at 20s
    ])