# Running the code

See [`code/README.md`](../../code/README.md) for the commands. Short version:

- Offline analysis, no ROS needed (Python 3 + numpy, scipy, matplotlib):
  `cd code/beacon_localization && python3 -m beacon_localization.analyze ../../bags/loc_5m_ret ...`
- ROS 2 (tested on Jazzy, 2026-11-25): `cd code && colcon build --symlink-install`,
  `source install/setup.bash`, `ros2 run beacon_localization beacon_node --ros-args -p robot:=pioneer4`,
  and `ros2 bag play bags/<bag>` in a second terminal. On Ctrl+C the node writes
  `results/results.md` and figures for the received data.
- The live node and offline analysis gave identical numbers on
  `loc_square_right` (tested 2026-11-25).
