# Mobile Robots – laboratory 3 – Beacon-based global localization


## Introduction

In this assignment, you will implement global robot localization and investigate its characteristics. The localization data is provided by the Decawave/Qorvo radio-based localization system, which measures the distances between the robot and stationary reference markers ([Decawave/Qorvo system](https://www.qorvo.com/products/p/MDEK1001)).

The laboratory localization system consists of four fixed reference modules with known (x,y,z) coordinates (anchors) and a transceiver mounted on the robot (tag). During each measurement cycle, the tag measures its distance to the available anchors and estimates the robot's position using built-in localization algorithms. The laboratory setup provides access to both raw measurement data (a list of visible anchors' coordinates and the corresponding measured distances) and the position estimates calculated internally by the system, together with quality parameters.

Your task is to implement a custom global localization algorithm and evaluate its performance by comparing its results with the localization estimates provided by the system's built-in algorithm and the robot's odometry.

**Note:** When developing your localization algorithm, keep in mind that the list of received measurements may contain fewer than four reference markers in some measurement cycles. This means that distance measurements for one or more markers have failed.

**Documentation of localization modules**
- [Real Time Location Systems. An Introduction](https://kcir.pwr.edu.pl/~jjakubia/l15/docs/Application%20Note%20APS003.pdf)
- [Product Datasheet: DWM1001-DEV](https://kcir.pwr.edu.pl/~jjakubia/l15/docs/DWM1001-DEV%20Data%20Sheet.pdf)


# Preparation

Before the laboratory session, review the task description and the provided supplementary materials. You should also prepare the following:
1. Review the formulas used to determine position using the trilateration method.
2. Propose an algorithm for determining the robot's position based on measurements from four stationary reference points.
3. Propose a method for evaluating localization error.

# T1. Data Acquisition and Processing

1. Analyze the format of the messages published on the following topics:
   - `/pioneerX/tag_status` – raw distance measurements
   - `/pioneerX/tag_pose` – tag position estimate from the system's built-in localization algorithm (reference)
2. Implement a script that subscribes to both topics and processes the received messages.
3. Implement an algorithm to estimate the robot's position in the global coordinate system using the raw measurement data.

# T2. Evaluation of Localization Quality

1. Using the provided files, compare the position estimates calculated by your algorithm with those published on the `tag_pose` and `odom` topics.
2. Perform example test runs and compare all available localization methods. In addition to the methods mentioned above, include your own odometry implementation based on wheel positions and velocities.
3. Verify that your program works correctly by running it either directly on the robot or using recorded ROS bag files.

1. Using the provided files, compare the localization determined by the implemented algorithm with the one presented in the topics `tag_pose` and `odom`.
2. Perform example test runs and compare all existing localization methods (in addition to the above, also include your custom odometry calculated from wheel positions and velocities).
3. The program’s operation can be verified directly using the robot or with the help of recorded rosbag files ([rosbag files](https://kcir.pwr.edu.pl/~jjakubia/l15/lab_localization/)).

# Report

The lab report should be a repository including the developed code and the report in the [report/](report/) folder.

The report should contain:
- A description of the implemented localization algorithm, including the formulas used.
- Localization results obtained from the provided bag files.
- Results of the comparisons performed in T2, accompanied by a discussion of the results and conclusions.

Export the code and the report as zip or tar.gz  and submit the archive via eportal.

Note: Keep your submitted repository clean: do not include generated or temporary files or unnecessary binaries.
