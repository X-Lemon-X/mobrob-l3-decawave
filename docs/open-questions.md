# Open questions

When a question is answered, write the answer next to it (or move it to
`decisions.md`) and update the linked proposal.

## Open

| # | Question | Default assumed in proposals | Affects |
|---|---|---|---|
| Q1 | What is the real mounting height of the tag on the robot? | 0.3 m (`tag_height`) | beacon-localization |
| Q2 | What are the real field names of `decawave_msgs` on the lab robots (`ros2 interface show decawave_msgs/msg/AnchorArray`)? | Node uses raw bytes, so only type names must match; our package only needed off-robot | messages, node |
| Q3 | Where is the tag relative to the robot rotation centre? | Offset ignored (0) | evaluation |
| Q4 | Does `loc_5m_ret` end at its start point? | Assumed yes when reading the closure column | evaluation |
| Q6 | What does `tag_pose.quality` mean and should low-quality samples be excluded? | All samples used (`min_reference_quality` = 0.0) | evaluation |
| Q7 | Report authors and language? | English, authors to fill in | report |

## Answered

| # | Question | Answer |
|---|---|---|
| Q5 | Are `wheel_radius` = 0.0975 m and `wheel_base` = 0.325 m right for pioneer4? | Wheel base yes; radius no – lab 2 report: effective radius ≈ 95.2 mm (ticks ×1/1.0245), velocity is in mm/s. Both added as variants (2026-11-25) → [encoder-odometry.md](knowledge/encoder-odometry.md) |
