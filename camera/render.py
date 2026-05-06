"""Rendering utilities for webcam overlays.

Why this module exists: drawing UI overlays is separate from camera IO and
recognition logic, which keeps responsibilities cohesive and testable.
"""

from __future__ import annotations

from typing import Any, Literal

import cv2


FaceState = Literal["unknown", "recognized", "uploaded"]


def draw_face_overlay(
    frame: Any,
    face_location: tuple[int, int, int, int],
    name: str | None,
    state: FaceState,
    confidence: float | None,
    scale_factor: float,
) -> None:
    """Draw bounding box and label on the full-size frame."""
    if scale_factor <= 0:
        raise ValueError("scale_factor must be greater than 0")

    resize_multiplier = int(1 / scale_factor)
    top, right, bottom, left = [value * resize_multiplier for value in face_location]

    color = _state_color(state)
    label = _state_label(name, state, confidence)

    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    cv2.putText(
        frame,
        label,
        (left, top - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2,
        cv2.LINE_AA,
    )


def _state_color(state: FaceState) -> tuple[int, int, int]:
    if state == "unknown":
        return (0, 0, 255)
    if state == "uploaded":
        return (0, 255, 0)
    return (0, 255, 255)


def _state_label(name: str | None, state: FaceState, confidence: float | None) -> str:
    if state == "unknown" or not name:
        return "Unknown"
    suffix = ""
    if confidence is not None:
        percent = int(round(confidence * 100))
        suffix = f" {percent}%"
    if state == "uploaded":
        return f"{name} [OK]{suffix}"
    return f"{name}{suffix}"
