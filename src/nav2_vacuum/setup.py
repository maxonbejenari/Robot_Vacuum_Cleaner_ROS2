from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'nav2_vacuum'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Required for ROS2 to find the package
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # Launch files
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*.py'))),

        # Config files — explicitly list each file instead of glob
        # glob sometimes misses files due to encoding or timing issues
        (os.path.join('share', package_name, 'config'), [
            'config/mapper_params.yaml',
            'config/nav2_params.yaml',
        ]),

        # Maps folder
        (os.path.join('share', package_name, 'maps'),
            glob(os.path.join('maps', '*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your@email.com',
    description='NAV2 vacuum cleaner robot package',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)