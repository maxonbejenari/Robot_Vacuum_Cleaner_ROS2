from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    
    robot_description_path = get_package_share_directory('robot_vacuum_description')
    robot_package = FindPackageShare('robot_vacuum_description')
    robot_name = 'robot_vacuum'
    robot_urdf_file_name = 'robot_vacuum.urdf.xacro'
    rviz_config_file_name = 'rviz_config.rviz'
    
    parent_of_share_path = os.path.dirname(robot_description_path)
    
    set_gz_sim_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[
            os.environ.get('GZ_SIM_RESOURCE_PATH', ' '),
            os.path.pathsep,
            parent_of_share_path
        ]
    )
    
    use_sim_time_declare = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use Gazebo clock if true'
    )
    
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    # Declare rviz arguments
    urdf_path_arg = DeclareLaunchArgument(
        'urdf_path',
        default_value=PathJoinSubstitution([
            robot_package,
            'urdf',
            robot_urdf_file_name
        ]),
        description='Path to the URDF file for the robot description.'
    )
    
    # for rviz config
    rviz_config_path_arg = DeclareLaunchArgument(
        'rviz_config_path',
        default_value=PathJoinSubstitution([
            robot_package,
            'rviz',
            rviz_config_file_name
        ]),
        description='Path to the RVIZ config file.'
    )
    
    # Get the robot description from the URDF file
    robot_description_content = ParameterValue(
        Command(['xacro ', LaunchConfiguration('urdf_path')]),
        value_type=str
    )
    
    # Robot state Publisher node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': use_sim_time,
            'frame_prefix': f'{robot_name}/'
        }]
    )
    
    # RVIZ node
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config_path')],
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )
    
    return LaunchDescription([
        urdf_path_arg,
        rviz_config_path_arg,
        use_sim_time_declare,
        set_gz_sim_resource_path,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz2_node
    ])