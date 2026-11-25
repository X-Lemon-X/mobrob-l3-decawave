# Project log

Chronological record of meetings and work sessions, newest first.
Each entry: what happened, decisions, and next steps. Details live in the
linked pages; this file is the short version.

---

## 2026-11-25 — Initial implementation (with Claude)

**Done**
- Downloaded the 3 lab bags to `bags/`; decoded `decawave_msgs` from raw bytes → [messages.md](knowledge/messages.md)
- Trilateration (linear LS + nonlinear LS), encoder odometry, evaluation, plots → [beacon-localization.md](knowledge/beacon-localization.md), [encoder-odometry.md](knowledge/encoder-odometry.md), [evaluation.md](knowledge/evaluation.md)
- ROS 2 node `beacon_node` + reconstructed `decawave_msgs`; built and tested with `ros2 bag play` on Jazzy → [running.md](knowledge/running.md)
- Results and report draft in `report/`.

**Decisions** → [decisions.md](decisions.md#2026-11-25--initial-implementation): 2D with fixed tag height, raw CDR decoding, `tag_pose` as reference.

**Found**
- Ranges update at only 1.2–6.1 Hz although topics are 10 Hz.
- All anchors at z = 1.6 m → built-in z unusable.
- Error spikes of all methods coincide → `tag_pose` probably lags.

**Next**
- Measure tag height and offset on the robot (Q1, Q3).
- Check `decawave_msgs` on the robot (Q2) and run the node live.
- Record own runs if possible; fill authors and discussion in the report.
