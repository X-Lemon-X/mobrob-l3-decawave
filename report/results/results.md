# Results

Localization config: `LocalizationConfig(mode='2d', tag_height=0.3, max_anchor_z_margin=0.05, robust_loss='linear', loss_scale=0.1, min_anchors=3, min_anchors_with_prior=2, max_residual_rms=0.5)`

## loc_5m_ret

![trajectories](loc_5m_ret_xy.png)

![errors](loc_5m_ret_error.png)

Distance to `tag_pose` [m] (odometry aligned to `tag_pose` by a best-fit rigid transform):

| method | samples | mean | RMSE | median | p95 | max |
|---|---|---|---|---|---|---|
| beacon LS (2d) | 201 | 0.230 | 0.278 | 0.210 | 0.541 | 1.188 |
| odom (robot) | 201 | 0.173 | 0.217 | 0.150 | 0.386 | 1.046 |
| odom (ours, encoders) | 201 | 0.179 | 0.216 | 0.167 | 0.344 | 1.005 |

Static spread = RMS distance to the mean position before the robot starts moving (5.6 s). Closure = |end - start|.

| method | samples | rate [Hz] | static spread [m] | closure [m] |
|---|---|---|---|---|
| tag_pose (built-in) | 201 | 4.1 | n/a | 0.251 |
| beacon LS (2d) | 201 | 4.1 | n/a | 0.309 |
| odom (robot) | 573 | 10.0 | 0.000 | 0.340 |
| odom (ours, encoders) | 573 | 10.0 | 0.000 | 0.432 |

## loc_square_left

![trajectories](loc_square_left_xy.png)

![errors](loc_square_left_error.png)

Distance to `tag_pose` [m] (odometry aligned to `tag_pose` by a best-fit rigid transform):

| method | samples | mean | RMSE | median | p95 | max |
|---|---|---|---|---|---|---|
| beacon LS (2d) | 35 | 0.200 | 0.315 | 0.113 | 0.768 | 1.086 |
| odom (robot) | 35 | 0.158 | 0.242 | 0.105 | 0.548 | 0.853 |
| odom (ours, encoders) | 35 | 0.146 | 0.226 | 0.096 | 0.501 | 0.830 |

Static spread = RMS distance to the mean position before the robot starts moving (4.3 s). Closure = |end - start|.

| method | samples | rate [Hz] | static spread [m] | closure [m] |
|---|---|---|---|---|
| tag_pose (built-in) | 35 | 1.2 | 0.005 | 0.852 |
| beacon LS (2d) | 35 | 1.2 | 0.038 | 0.196 |
| odom (robot) | 350 | 10.0 | 0.000 | 0.032 |
| odom (ours, encoders) | 350 | 10.0 | 0.000 | 0.200 |

## loc_square_right

![trajectories](loc_square_right_xy.png)

![errors](loc_square_right_error.png)

Distance to `tag_pose` [m] (odometry aligned to `tag_pose` by a best-fit rigid transform):

| method | samples | mean | RMSE | median | p95 | max |
|---|---|---|---|---|---|---|
| beacon LS (2d) | 144 | 0.159 | 0.200 | 0.122 | 0.375 | 0.779 |
| odom (robot) | 144 | 0.131 | 0.154 | 0.114 | 0.275 | 0.584 |
| odom (ours, encoders) | 144 | 0.127 | 0.149 | 0.112 | 0.274 | 0.556 |

Static spread = RMS distance to the mean position before the robot starts moving (2.9 s). Closure = |end - start|.

| method | samples | rate [Hz] | static spread [m] | closure [m] |
|---|---|---|---|---|
| tag_pose (built-in) | 144 | 6.1 | 0.063 | 0.137 |
| beacon LS (2d) | 145 | 6.1 | 0.072 | 0.220 |
| odom (robot) | 314 | 10.0 | 0.000 | 0.052 |
| odom (ours, encoders) | 314 | 10.0 | 0.000 | 0.121 |
