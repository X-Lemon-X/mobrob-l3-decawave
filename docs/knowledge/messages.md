# Message formats (`code/decawave_msgs`, `beacon_localization/messages.py`)

The `decawave_msgs` package is not available publicly or in the bags
(metadata version 4 stores no definitions). The layout below was decoded
from the raw CDR bytes of the lab bags on 2026-11-25. Field names are our
guesses; the binary layout is verified (ranges computed from `tag_pose`
match the measured ranges to ±0.1 m).

## `/pioneerX/tag_status` — `decawave_msgs/msg/AnchorArray`

```
std_msgs/Header header
Anchor[] anchors          # 3 or 4 entries in the lab bags
```
`Anchor`:
```
std_msgs/Header header    # frame_id = anchor id, e.g. "1419"
float64 x, y, z           # anchor position [m]
float64 qf                # always 1.0
float64 distance          # measured range [m]
float64 distance_qf       # always 1.0
```

## `/pioneerX/tag_pose` — `decawave_msgs/msg/Tag`

```
std_msgs/Header header    # frame_id "/pioneer4/tag"
float64 x, y, z           # built-in position estimate [m]
float64 quality           # 0.0 .. 1.0
int32 anchor_count        # anchors used, 3 or 4
```

## Other topics
- `/pioneerX/odom` — `nav_msgs/Odometry`, robot odometry.
- `/pioneerX/joint_states` — `sensor_msgs/JointState`; `position` = raw
  16-bit encoder counters (left, right), `velocity` in mm/s (as in lab 2).

## How the code uses this
- Offline: `bag_reader.py` reads the `.db3` with `sqlite3` and decodes
  bytes with `cdr.py`/`messages.py`. No ROS needed.
- Online: `node.py` subscribes with `raw=True` and decodes the same bytes,
  so only the type *name* of the installed `decawave_msgs` must match.
- Our `code/decawave_msgs` package is needed for `ros2 bag play` (the
  player needs the type support) and for running the node at home.
