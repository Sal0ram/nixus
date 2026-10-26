import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ros_gz_bridge.actions import RosGzBridge
from ros_gz_sim.actions import GzServer


def generate_launch_description():   
    
    # Declarations -------------------------------------------------------
    pkg_share = FindPackageShare(package='nixus').find("nixus")
    default_model_path = os.path.join(pkg_share, 'urdf', 'nixus_v2.urdf')
    ros_gz_sim_pkg_path = get_package_share_directory('ros_gz_sim')
    gz_launch_path = os.path.join(ros_gz_sim_pkg_path, 'launch', 'gz_sim.launch.py')
    
    joint_state_publisher_gui_arg = DeclareLaunchArgument(
        name='gui', default_value='True', description='Flag to enable joint_state_publisher_gui')
    joint_state_publisher_arg = DeclareLaunchArgument(
        name='model', default_value=default_model_path, description='Absolute path to robot model file')
    declare_world_sdf_file_cmd = DeclareLaunchArgument(
        'world_sdf_file', default_value=default_model_path, description='Path to the SDF world file')
    
    Command('gz sim empty.sdf')
    # General nodes -----------------------------------------------------
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': ParameterValue(Command(['xacro ', default_model_path]),value_type=str), 'use_sim_time': True}]
    )
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'robot_description': ParameterValue(Command(['xacro ', default_model_path]),value_type=str)}],
        condition=UnlessCondition(LaunchConfiguration('gui'))
    )
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(LaunchConfiguration('gui'))
    )
    
    # GAZEBO-related --------------------------------------------------------
    gazebo_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz_sim_pkg_path,'launch','gz_sim.launch.py')),
        
    )
    declare_world_sdf = GzServer(
        world_sdf_file='empty.sdf',
    )
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-entity', 'my_robot']
    )
 
    # Generate launch description --------------------------------------------------
    ld = LaunchDescription([
        joint_state_publisher_arg,
        joint_state_publisher_gui_arg,
        joint_state_publisher_node,
        joint_state_publisher_gui_node,
        robot_state_publisher_node,
        gazebo_include,
        declare_world_sdf,
        spawn_entity,
    ])

    
    return ld
    