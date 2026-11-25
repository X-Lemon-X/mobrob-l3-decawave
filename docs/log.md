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

## 2026-11-25 — Lab 2 odometry comparison

**Done**
- Read lab 2 code and report (`mobrob-l2-odom`). Added velocity-based odometry
  (version B) and radius-calibrated tick odometry to the comparison; re-ran
  `results/` and `results_3d/`; updated report sections 2, 4, 5.

**Found**
- Lab 2 calibration (r_eff ≈ 95.2 mm) transfers: loop closure drops from
  12–43 cm to 0.5–8 cm. Q5 answered.

## 2026-11-25 — Live plot, cross-check, report complete

**Done**
- `live_plot` node (matplotlib, all methods live).
- `crosscheck.py`: odometry as second reference (lag, outliers, gaps) in `results.md`.
- `example_figure.py` → `report/figures/trilateration_example.png`.
- Report: sections 3–6 rewritten (cross-check, T2.3, discussion, conclusions).

**Found**
- `tag_pose` lags 0.2–0.5 s behind odometry and causes the ~1 m differences;
  our fixes stay < 0.5 m from odometry → [evaluation.md](knowledge/evaluation.md).
- Gaps of 1–10 s without new ranges (tag side).

**Next**
- Own runs on pioneer 2; measure tag height (Q1) and offset (Q3).
- Optional: odometry + UWB fusion (Kalman filter).
