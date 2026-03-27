"""Webcam attendance rendering loop."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from camera.matching import normalize_known_faces
from camera.qt_runtime import configure_qt_font_dir, ensure_opencv_qt_fonts
from camera.runtime_loop import run_webcam_loop

configure_qt_font_dir()

import cv2

logger = logging.getLogger(__name__)

ensure_opencv_qt_fonts(cv2)


def run_webcam_attendance(
    known_face_encodings: list[Any],
    known_face_names: list[str],
    camera_index: int = 0,
    window_name: str = "Attendance System",
    scale_factor: float = 0.25,
    recognition_delay_seconds: float = 3.0,
    on_face_recognized: Callable[[str], bool | None] | None = None,
) -> None:
    """Run webcam loop and draw recognized faces.

    Args:
        known_face_encodings: Known face vectors.
        known_face_names: Name labels aligned with known_face_encodings.
        camera_index: OpenCV camera source index.
        window_name: Display window title.
        scale_factor: Frame downscaling for performance.
        recognition_delay_seconds: Continuous recognition time before callback.
        on_face_recognized: Optional callback called for each recognized name.
            Return True from callback to stop the webcam loop.
    """
    normalized_encodings, normalized_names = normalize_known_faces(known_face_encodings, known_face_names)
    if len(normalized_encodings) != len(known_face_encodings) or len(normalized_names) != len(known_face_names):
        logger.warning(
            "Known face data mismatch (encodings=%d, names=%d). Using first %d entries.",
            len(known_face_encodings),
            len(known_face_names),
            len(normalized_encodings),
        )
    run_webcam_loop(
        known_face_encodings=normalized_encodings,
        known_face_names=normalized_names,
        camera_index=camera_index,
        window_name=window_name,
        scale_factor=scale_factor,
        recognition_delay_seconds=recognition_delay_seconds,
        on_face_recognized=on_face_recognized,
    )
