from setuptools import find_packages, setup

package_name = "beacon_localization"

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
    description="Global localization from Decawave UWB ranges and its evaluation.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "beacon_node = beacon_localization.node:main",
            "analyze = beacon_localization.analyze:main",
        ],
    },
)
