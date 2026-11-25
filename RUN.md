# How to run

Three ROS 2 packages live in [code/](code/) (the colcon workspace):
`beacon_localization` (our node + analysis), `decawave_msgs` (message
definitions rebuilt from the bags) and `pioneer_odom` (original lab 2 node).
Details and module map: [code/README.md](code/README.md).

## 1. Offline analysis (no ROS needed)

Python 3 with numpy, scipy, matplotlib.

```bash
cd code/beacon_localization
python3 -m beacon_localization.analyze ../../bags/loc_5m_ret ../../bags/loc_square_left \
    ../../bags/loc_square_right --out ../../report/results
# variants:  --mode 3d   --tag-height 0.4   --loss soft_l1
```

Writes `results.md` and `<bag>_xy.png`, `<bag>_error.png`. Compared methods:
`tag_pose` (reference), our beacon LS, robot `odom`, our odometry from ticks,
ticks with the lab 2 radius calibration, and wheel velocities.

## 2. Build (ROS 2 Jazzy)

```bash
cd code
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install            # on a PC that already has decawave_msgs:
                                          #   add --packages-skip decawave_msgs
source install/setup.bash
```

Every new terminal: `source /opt/ros/jazzy/setup.bash && source code/install/setup.bash`.

## 3. Comparison node with a rosbag

```bash
# terminal 1
cd code
ros2 run beacon_localization beacon_node --ros-args -p robot:=pioneer4 \
    -p tag_height:=0.3 -p output_dir:=results
# terminal 2
ros2 bag play bags/loc_square_right
```

When the bag ends press **Ctrl+C** in terminal 1: it prints the tables and
writes `results.md` + plots to `output_dir` (relative to the directory the
node was started in).

The node:
- subscribes `/<robot>/tag_status`, `tag_pose`, `joint_states`, `odom`;
- publishes `/<robot>/beacon_pose` (`geometry_msgs/PoseStamped`, frame `map`)
  and `/<robot>/encoder_odom` (`nav_msgs/Odometry`, uncalibrated ticks);
- logs each fix with its distance to `tag_pose`.

The calibrated and velocity odometry appear only in the report written on Ctrl+C.

## 4. Live on a robot (example: pioneer 2)

**Connect.** Same network as the robot, then:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=<robot's domain id>   # ask in the lab
ros2 topic list | grep -i 2
```

Use the prefix you see (`pioneer2`, or `pp2` as in lab 2) as `robot:=` below.
Check the data and the message definition:

```bash
ros2 topic hz /pioneer2/tag_status
ros2 interface show decawave_msgs/msg/AnchorArray
```

If `interface show` works, the PC already has `decawave_msgs`: build with
`--packages-skip decawave_msgs` (section 2).

**Run the node** (live output in this terminal):

```bash
cd code
ros2 run beacon_localization beacon_node --ros-args -p robot:=pioneer2 \
    -p tag_height:=0.3 -p output_dir:=results_pioneer2
```

**Watch other topics** (each in its own sourced terminal, optional):

```bash
ros2 topic echo /pioneer2/beacon_pose     # our trilateration
ros2 topic echo /pioneer2/encoder_odom    # our odometry
ros2 topic echo /pioneer2/tag_pose        # built-in estimate
```

**Record the run** to analyse it offline later (section 1):

```bash
cd data
ros2 bag record -o run1_pioneer2 /pioneer2/tag_status /pioneer2/tag_pose \
    /pioneer2/odom /pioneer2/joint_states
```

Drive the robot, then Ctrl+C the node → `code/results_pioneer2/results.md`.

While at the robot, measure the tag height (Q1) and the tag offset from the
wheel axle centre (Q3), see [docs/open-questions.md](docs/open-questions.md).

## 5. Original lab 2 odometry node

It listens on `/pp5/...`, so remap:

```bash
ros2 run pioneer_odom odom --ros-args \
    -r /pp5/odom:=/pioneer4/odom -r /pp5/joint_states:=/pioneer4/joint_states
```

On Ctrl+C it saves `odom_paths.png`.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `ros2 topic list` is empty | wrong `ROS_DOMAIN_ID` or different network |
| topics listed, node prints nothing | wrong `robot:=` name |
| `odom` arrives, `tag_status` does not | our `decawave_msgs` differs from the robot's – use theirs (`--packages-skip decawave_msgs`) or send `ros2 topic info -v /pioneer2/tag_status` |
| `ModuleNotFoundError: decawave_msgs` | `source code/install/setup.bash` missing |
