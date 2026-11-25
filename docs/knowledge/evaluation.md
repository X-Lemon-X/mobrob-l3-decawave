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
