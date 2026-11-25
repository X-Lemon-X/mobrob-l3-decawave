# Beacon localization algorithm (`beacon_localization/trilateration.py`)

Computes the tag position from ranges `r_i` to anchors `a_i = (x_i, y_i, z_i)`.

## Measurement model

`r_i = || p - a_i || + noise`, with `p = (x, y, h)`.
Default mode `2d`: the tag height `h` is a fixed parameter
(`LocalizationConfig.tag_height`, default 0.3 m), and only (x, y) are
estimated. Reason: anchors are coplanar, see
[decawave-setup.md](decawave-setup.md#coordinate-frame).

## Step 1: linear initial solution (≥ 3 anchors)

Horizontal range: `q_i = r_i^2 - (h - z_i)^2 = (x - x_i)^2 + (y - y_i)^2`.
Subtracting the equation of anchor 0 from anchor i removes the quadratic terms:

`2(x_i - x_0) x + 2(y_i - y_0) y = q_0 - q_i + x_i^2 - x_0^2 + y_i^2 - y_0^2`

This gives `A [x y]^T = b` with N-1 rows, solved by `numpy.linalg.lstsq`.
Exact for 3 anchors, least squares for 4.

## Step 2: nonlinear least squares refinement

`min_{x,y} sum_i ( ||p - a_i|| - r_i )^2` with `scipy.optimize.least_squares`
(trust-region reflective), started at the linear solution. The linear
solution minimizes the error of squared ranges, which weights far anchors
too much; the refinement minimizes the actual range errors.

## Special cases
- Repeated range sets (same ids and distances as the last message) are
  skipped (`beacon_localizer.py`), because the tag republishes old data.
- 2 anchors: refinement started from the previous fix (two-circle
  intersection nearest to the last position). 0–1 anchors: no fix.
  Not seen in the lab bags (minimum was 3 anchors).
- Fixes with residual RMS > `max_residual_rms` (0.5 m) are rejected.
- Mode `3d`: z estimated as well, bounded to `z <= min(z_i) - 0.05`
  (tag below anchors) to resolve the mirror ambiguity.

## Parameters (`config.py`, `LocalizationConfig`)
`mode`, `tag_height`, `robust_loss` (`linear`, `soft_l1`, `huber`, `cauchy`),
`loss_scale`, `min_anchors`, `min_anchors_with_prior`, `max_residual_rms`.
CLI: `--mode`, `--tag-height`, `--loss`. ROS params: `mode`, `tag_height`,
`robust_loss`.

## Sensitivity (RMSE vs `tag_pose` [m], 2026-11-25)

| Variant | 5m_ret | square_left | square_right |
|---|---|---|---|
| 2d, h = 0.0 | 0.293 | 0.316 | 0.202 |
| 2d, h = 0.3 (default) | 0.278 | 0.315 | 0.200 |
| 2d, h = 0.6 | 0.269 | 0.314 | 0.202 |
| 3d | 0.266 | 0.316 | 0.221 |
| 2d, soft_l1 | 0.292 | 0.301 | 0.208 |
| 2d, huber | 0.296 | 0.300 | 0.213 |
| 2d, cauchy | 0.313 | 0.297 | 0.234 |

Differences are a few cm, smaller than the disagreement with `tag_pose`
itself, so the defaults stay. Robust losses help only `square_left`.

## Known limitations (as of 2026-11-25)
- No temporal filtering: each fix is independent, so the trajectory is
  noisier than `tag_pose` (which looks filtered).
- Tag height is assumed, not measured (Q1).
