# Decawave lab setup and data

The lab has four fixed UWB anchors and one tag on the robot. The tag
measures ranges to the anchors by two-way ranging and also computes its own
position. Everything below was measured from the three lab bags on
2026-11-25 (`loc_5m_ret`, `loc_square_left`, `loc_square_right`, robot
`pioneer4`, recorded 2024-11-19).

## Coordinate frame

Global frame = the frame of the anchor coordinates in `tag_status`.
x, y horizontal, z up, metres. Anchor `1419` is the origin.

| Anchor id | x [m] | y [m] | z [m] |
|---|---|---|---|
| `1419` | 0.000 | 0.000 | 1.6 |
| `0FB6` | 7.233 | 0.000 | 1.6 |
| `51B8` | -2.090 | 7.228 | 1.6 |
| `5898` | 3.760 | 9.134 | 1.6 |

All anchors are at the same height. Consequence: the tag height `z` is
poorly observable (it only enters through second-order terms), and a 3D
solution has a mirror ambiguity about the plane z = 1.6 m.

Robot `odom` is in its own frame with an arbitrary origin (e.g. starts at
(4.697, -2.624) in `loc_5m_ret`). It must be aligned to the global frame
before comparison, see [evaluation.md](evaluation.md#frame-alignment).

## Ranging principle

Two-way ranging (TWR): the anchor sends a message, the tag replies, the
anchor measures the round trip `T_round = 2*T_tof + T_reply` and
`d = c * T_tof`. No clock synchronization between tag and anchor is needed.
Source: APS003, see [sources.md](../sources.md).

## Data rates and quality (lab bags)

| Bag | duration [s] | msgs per topic | new range sets | 3-anchor msgs |
|---|---|---|---|---|
| `loc_5m_ret` | 57.2 | 573 | 201 (≈4.1 Hz) | 5 |
| `loc_square_left` | 34.9 | 350 | 35 (≈1.2 Hz) | 0 |
| `loc_square_right` | 31.3 | 314 | 145 (≈6.1 Hz) | 6 |

- All topics are published at 10 Hz, but `tag_status` repeats the last
  range set until a new one arrives. Only the "new range sets" are real
  measurements. In `loc_square_left` there is a gap covering about one
  side of the square.
- `tag_pose` changes exactly when the range set changes (same counts).
- `tag_pose.quality` is often 0.0 (110 of 573 msgs in `loc_5m_ret`) even
  when the position looks reasonable. Meaning not documented.
- `tag_pose.z` ranges from -0.07 to 1.50 m within one bag, so the built-in
  z is not usable.
- Range residuals of our 2D solution: median RMS 0.07–0.15 m per bag.

## Known limitations (as of 2026-11-25)
- The true tag mounting height on the robot is unknown, see
  [Q1](../open-questions.md).
- The tag offset from the robot rotation centre is unknown (Q3). It adds up
  to that offset to every comparison with odometry.
