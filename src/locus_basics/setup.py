from setuptools import find_packages, setup

package_name = 'locus_basics'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='phoenix',
    maintainer_email='mohamed.120230004@ejust.edu.eg',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'velocity_publisher = locus_basics.velocity_publisher:main',
            'velocity_subscriber = locus_basics.velocity_subscriber:main',
            'cmd_vel_relay = locus_basics.cmd_vel_relay:main',
        ],
    },
)
