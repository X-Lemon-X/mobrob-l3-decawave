# Decisions

Newest first. One entry per decision: what, why, and where it is described.

## 2026-11-25 — Initial implementation

- **Default solver is 2D with a fixed tag height (0.3 m)**, 3D kept as an option.
  Why: all anchors are at z = 1.6 m, so z is poorly observable and the built-in
  z jumps by >1.5 m; the sweep showed height changes move RMSE by only a few cm.
  → [beacon-localization.md](knowledge/beacon-localization.md#sensitivity-rmse-vs-tag_pose-m-2026-11-25)
- **Linear LS initial solution + nonlinear LS refinement (`scipy.optimize.least_squares`)**.
  Why: linear is closed-form and needs no guess; the refinement minimizes real range errors.
  → [beacon-localization.md](knowledge/beacon-localization.md)
- **Decode decawave messages from raw CDR bytes; ship our own reconstructed `decawave_msgs`**
  (answers how to read the bags without the original package). Why: the package is not
  available; raw decoding makes the node independent of the real field names.
  → [messages.md](knowledge/messages.md)
- **Skip repeated range sets.** Why: `tag_status` republishes old ranges at 10 Hz;
  counting them would fake a higher rate and weight static periods.
  → [decawave-setup.md](knowledge/decawave-setup.md#data-rates-and-quality-lab-bags)
- **`tag_pose` is the reference; odometry aligned by best-fit rigid transform.**
  Why: no ground truth available; odom frames have arbitrary origins.
  → [evaluation.md](knowledge/evaluation.md)
- **Bags stored in `bags/` (git-ignored via `*.db3`, `metadata.yaml`); report figures
  in `report/results/` are committed.** Why: assignment asks for a clean repo but the
  report needs the figures.
