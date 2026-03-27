"""Rendering utilities for webcam overlays.

Why this module exists: drawing UI overlays is separate from camera IO and
recognition logic, which keeps responsibilities cohesive and testable.
"""

from __future__ import annotations

from typing import Any

import cv2


def draw_label(frame: Any, face_location: tuple[int, int, int, int], name: str, scale_factor: float) -> None:
    """Draw bounding box and person label on the full-size frame."""
    if scale_factor <= 0:
        raise ValueError("scale_factor must be greater than 0")

    resize_multiplier = int(1 / scale_factor)
    top, right, bottom, left = [value * resize_multiplier for value in face_location]

    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    cv2.putText(
        frame,
        name,
        (left, top - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2,
    )
