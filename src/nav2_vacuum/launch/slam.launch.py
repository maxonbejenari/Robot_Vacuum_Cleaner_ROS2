import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription 
from launch.actions import DeclareLaunchArgument, EmitEvent, LogInfo, RegisterEventHandler
from launch.conditions import IfCondition
from launch.events import matches_action
from launch.substitutions import AndSubstitution, LaunchConfiguration, NotSubstitution
from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition

def generate_launch_description():
    
    autostart = LaunchConfiguration('autostart')
    use_lifecycle_manager = LaunchConfiguration('use_lifecycle_manager')
    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_params_file = LaunchConfiguration('slam_params_file')
    
    declare_autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Autostart slam_toolbox'
    )
    
    declare_use_lifecycle_manager = DeclareLaunchArgument(
        'use_lifecycle_manager',
        default_value='false',
        description="Use nav2 lifecycle manager"
    )
    
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='use gazebo sim time'
    )
    
    declare_slam_params_file = DeclareLaunchArgument(
        'slam_params_file',
        default_value=os.path.join(
            get_package_share_directory('nav2_vacuum'),
            'config',
            'mapper_params.yaml'
        ),
        description='Path to yaml with SLAM parameters'
    )
    
    slam_toolbox_node = LifecycleNode(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        namespace='',
        output='screen',
        parameters=[
            slam_params_file,
            {
                'use_lifecycle_manager': use_lifecycle_manager,
                'use_sim_time': use_sim_time,
            }
        ],
    )
    
    configure_event = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=matches_action(slam_toolbox_node),
            transition_id=Transition.TRANSITION_CONFIGURE),
            condition=IfCondition(AndSubstitution(autostart, NotSubstitution(use_lifecycle_manager)))
    )
    
    activate_event = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=slam_toolbox_node,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                LogInfo(msg='The Node is configured, activate...'),
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(slam_toolbox_node),
                        transition_id=Transition.TRANSITION_ACTIVATE
                    )
                )
            ]
        ),
        condition=IfCondition(
            AndSubstitution(autostart, NotSubstitution(use_lifecycle_manager))
        )
    )
    
    ld = LaunchDescription()
    ld.add_action(declare_autostart)
    ld.add_action(declare_use_lifecycle_manager)
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_slam_params_file)
    ld.add_action(slam_toolbox_node)
    ld.add_action(configure_event)  
    ld.add_action(activate_event) 
    return ld