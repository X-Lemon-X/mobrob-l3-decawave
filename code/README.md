# Code

Two ROS 2 packages (colcon workspace = this folder):

- `beacon_localization/` — trilateration from UWB ranges, wheel odometry,
  evaluation and plots. The core is plain Python and also runs without ROS.
- `decawave_msgs/` — message definitions reconstructed from the lab bags
  (`Anchor`, `AnchorArray`, `Tag`). Needed for `ros2 bag play` and for the
  node when the original package is not installed. **Do not build it on a
  lab robot that already has its own `decawave_msgs`.**

## 1. Bags

```bash
cd <repo>
mkdir -p bags && cd bags
for d in loc_5m_ret loc_square_left loc_square_right; do
  mkdir -p $d
  wget -q -P $d https://kcir.pwr.edu.pl/~jjakubia/l15/lab_localization/$d/metadata.yaml \
                https://kcir.pwr.edu.pl/~jjakubia/l15/lab_localization/$d/${d}_0.db3
done
```

## 2. Offline analysis (no ROS needed)

Requires Python 3 with numpy, scipy, matplotlib.

```bash
cd code/beacon_localization
python3 -m beacon_localization.analyze ../../bags/loc_5m_ret ../../bags/loc_square_left \
    ../../bags/loc_square_right --out ../../report/results
# variants:  --mode 3d   --tag-height 0.4   --loss soft_l1
```

Writes `results.md` (tables) and `<bag>_xy.png`, `<bag>_error.png`.

## 3. ROS 2 (tested on Jazzy)

```bash
cd code
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash

# terminal 1
ros2 run beacon_localization beacon_node --ros-args -p robot:=pioneer4 \
    -p tag_height:=0.3 -p output_dir:=results
# terminal 2 (same sourcing)
ros2 bag play ../bags/loc_square_right
```

The node:
- subscribes `/<robot>/tag_status`, `tag_pose`, `joint_states`, `odom`;
- publishes `/<robot>/beacon_pose` (`geometry_msgs/PoseStamped`, frame `map`)
  and `/<robot>/encoder_odom` (`nav_msgs/Odometry`);
- logs each fix with the distance to `tag_pose`;
- on Ctrl+C writes the same report as the offline analysis for the received data.

On the robot set `robot:=pioneerX` to the robot's name.

## Module map

| File | Role |
|---|---|
| `config.py` | all parameters (dataclasses) |
| `cdr.py`, `messages.py` | decode CDR bytes into plain dataclasses |
| `bag_reader.py` | read `.db3` bags with sqlite3 |
| `trilateration.py` | linear LS + nonlinear LS solver |
| `beacon_localizer.py` | skips repeated range sets, calls the solver |
| `odometry.py` | differential-drive odometry from encoder ticks |
| `trajectories.py` | builds trajectories of all methods |
| `evaluation.py` | time matching, rigid alignment, error metrics |
| `plots.py`, `analyze.py` | figures, `results.md`, CLI |
| `node.py` | ROS 2 node |
