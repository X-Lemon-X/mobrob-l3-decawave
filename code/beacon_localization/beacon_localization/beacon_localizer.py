"""Turns tag_status messages into position fixes, skipping repeated data."""

from typing import Optional

import numpy as np

from .config import LocalizationConfig
from .messages import AnchorArray
from .trilateration import Fix, Trilaterator


def measurement_key(msg: AnchorArray) -> tuple:
    """Identifies a measurement; the tag republishes old ranges at 10 Hz."""
    return tuple((a.anchor_id, round(a.distance, 4)) for a in msg.anchors)


class BeaconLocalizer:
    def __init__(self, config: LocalizationConfig):
        self.solver = Trilaterator(config)
        self._last_key = None

    def process(self, msg: AnchorArray) -> Optional[Fix]:
        """Returns a new fix, or None when the data is repeated or unusable."""
        key = measurement_key(msg)
        if key == self._last_key:
            return None
        self._last_key = key
        valid = [a for a in msg.anchors if a.distance > 0.0]
        if not valid:
            return None
        anchors = np.array([a.position for a in valid])
        ranges = np.array([a.distance for a in valid])
        return self.solver.solve(msg.stamp, anchors, ranges)
