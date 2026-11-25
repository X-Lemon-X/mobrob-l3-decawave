from setuptools import find_packages, setup

package_name = "beacon_live_plot"

setup(
    name=package_name,
    version="0.0.1",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="student",
    maintainer_email="student@example.com",
    description="Live matplotlib view of beacon localization, tag_pose and wheel odometry.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "live_plot = beacon_live_plot.live_plot:main",
        ],
    },
)
