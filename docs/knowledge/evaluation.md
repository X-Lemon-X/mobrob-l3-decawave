# Evaluation method and results (`beacon_localization/evaluation.py`, `analyze.py`)

## Reference
There is no ground truth. `tag_pose` (built-in algorithm) is the reference;
repeated samples are dropped. All errors are horizontal distances [m].

## Time matching
`sample_at`: a trajectory is interpolated linearly at the reference times
when its neighbouring samples are ≤ `max_sync_gap` (0.3 s) apart, otherwise
the nearest sample within 0.3 s is used.

## Frame alignment
Odometry (robot `odom` and ours) is mapped into the global frame by the
rigid 2D transform (rotation + translation, Kabsch/SVD) that best fits it to
`tag_pose` over the whole run. This is optimistic for odometry: it hides
part of the drift. Alternative not implemented: align on the first seconds
only.

## Metrics
- mean, RMSE, median, 95th percentile, max of the distance to `tag_pose`;
- static spread: RMS distance to the mean position before the robot moves
  (precision); `n/a` when there are < 2 new fixes in that period;
- closure: |end − start| of each trajectory (`loc_5m_ret` probably returns
  to the start; not confirmed).

## Results (2026-11-25, default config: 2d, h = 0.3 m)

RMSE to `tag_pose` [m]:

| Bag | beacon LS | odom (robot) | odom (ours) |
|---|---|---|---|
| `loc_5m_ret` | 0.278 | 0.217 | 0.216 |
| `loc_square_left` | 0.315 | 0.242 | 0.226 |
| `loc_square_right` | 0.200 | 0.154 | 0.149 |

Full tables and figures: [`report/results/results.md`](../../report/results/results.md).

## Observations
- Error spikes of all three methods happen at the same moments (e.g. 12 s,
  21 s, 35 s in `loc_5m_ret`). Odometry and our fixes are independent, so the
  spikes most likely come from `tag_pose` itself: it lags behind during
  fast motion or turns (looks like internal filtering). Not verified.
- Our fixes are noisier than `tag_pose` (no filtering) but follow the same
  path. Static spread: ours 0.072 m vs `tag_pose` 0.063 m in
  `loc_square_right`, 0.038 vs 0.005 m in `loc_square_left`.
- Odometry looks best only because of the best-fit alignment.

## Cross-check against wheel odometry (`crosscheck.py`, 2026-11-25)

Second reference: calibrated tick odometry (independent of UWB, no gaps).
Each UWB trajectory is rigid-aligned to it; the odometry is also shifted in time
(±1 s, 0.05 s steps) to find the best-fitting lag.

| Bag | `tag_pose` max / lag | beacon LS max / lag |
|---|---|---|
| `loc_5m_ret` | 1.012 m / +0.20 s | 0.488 m / −0.25 s |
| `loc_square_left` | 0.813 m / +0.50 s | 0.290 m / −0.40 s |
| `loc_square_right` | 0.578 m / +0.25 s | 0.428 m / −0.10 s |

`tag_pose` lags and has the large outliers; 17 of 19 beacon−tag_pose
differences > 0.5 m come < 1 s after a measurement gap (gaps 1–10 s, whole
seconds, robot drives up to 1.85 m meanwhile).
