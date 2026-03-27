"""Frame preprocessing utilities.

Why this module exists: resizing and color conversion are hot-path operations in
camera loops, so keeping them isolated makes optimization and testing easier.
"""

from __future__ import annotations

from typing import Any

import cv2


def scale_frame(frame: Any, scale_factor: float) -> Any:
    """Return a resized frame to reduce recognition workload per iteration."""
    if scale_factor <= 0:
        raise ValueError("scale_factor must be greater than 0")
    return cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)


def to_rgb(frame: Any) -> Any:
    """Return a contiguous RGB frame required by ``face_recognition``/dlib."""
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
