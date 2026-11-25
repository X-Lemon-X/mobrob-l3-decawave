# Encoder odometry (`beacon_localization/odometry.py`)

Differential-drive dead reckoning from `joint_states`, ported from lab 2
(`mobrob-l2-odom`, `pioneer_odom/odom.py` and `report/report.md`). Three variants
are compared:

- `EncoderOdometry(cfg)` – version A, ticks with measured r = 97.5 mm ("odom (ours, ticks)").
- `EncoderOdometry(cfg, cfg.tick_calibration)` – ticks with lab 2 calibration
  1/1.0245, r_eff ≈ 95.2 mm ("odom (ours, ticks calibrated)").
- `VelocityOdometry(cfg)` – version B, `joint_states.velocity` is the linear
  wheel speed in **mm/s** (found in lab 2), Δs = v·Δt; no radius needed.

## Model
- Tick delta with 16-bit wrap: `((now - before + 32768) mod 65536) - 32768`.
- Wheel angle = ticks / (4 · 500 · 38.3 / 2π) rad; distance = angle · `wheel_radius`.
- `ds = (ds_L + ds_R)/2`, `dθ = (ds_R - ds_L)/wheel_base`,
  `x += ds·cos(θ + dθ/2)`, `y += ds·sin(θ + dθ/2)`.

## Parameters (`OdometryConfig`)
`gear_ratio` 38.3, `encoder_lines` 500, `quadrature` 4,
`wheel_radius` 0.0975 m, `wheel_base` 0.325 m (from lab 2: 375 mm minus wheel width 50 mm).

## Measured (2026-11-25)

| Bag | path ours [m] | path robot odom [m] | Σ|dθ| ours [rad] | Σ|dθ| robot [rad] |
|---|---|---|---|---|
| `loc_5m_ret` | 10.28 | 10.05 | 5.28 | 5.16 |
| `loc_square_left` | 4.87 | 4.77 | 7.95 | 7.71 |
| `loc_square_right` | 4.85 | 4.74 | 6.92 | 6.80 |

Ours (nominal ticks) is ~2 % longer and turns ~2–3 % more than the robot's own
odometry. Lab 2 found the same +2.4 % on both pioneer4 and pioneer5 bags and +3 %
in a tape-measured 1 m run: the effective rolling radius is smaller than the
measured one (tyre compression); the wheel base is fine. Answered in Q5.

Loop closure |end − start| [m] after the fix (2026-11-25):

| Bag | robot odom | ticks | ticks calibrated | velocity |
|---|---|---|---|---|
| `loc_5m_ret` | 0.340 | 0.432 | 0.054 | 0.068 |
| `loc_square_left` | 0.032 | 0.200 | 0.077 | 0.074 |
| `loc_square_right` | 0.052 | 0.121 | 0.005 | 0.017 |
