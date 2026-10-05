import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'sim_mobile_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # ADD THIS LINE: Tells colcon to copy all .launch.py files from launch/ into install/share/
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        
        # Also ensure your URDF and RViz folders are included:
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'worlds'), glob(os.path.join('worlds', '*.sdf')))
        
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='abdur',
    maintainer_email='abdur@todo.todo',
    description='Simulated mobile robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'telemetry_node = sim_mobile_robot.telemetry:main',
            'headlight_node = sim_mobile_robot.headlight:main',
            'patrol_node = sim_mobile_robot.patrol:main',
        ],
    },
)
