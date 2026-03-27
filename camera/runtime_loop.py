"""Webcam attendance runtime loop."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

import cv2

from camera.frame_processor import process_frame

logger = logging.getLogger(__name__)


def run_webcam_loop(
    known_face_encodings: list[Any],
    known_face_names: list[str],
    camera_index: int,
    window_name: str,
    scale_factor: float,
    recognition_delay_seconds: float,
    on_face_recognized: Callable[[str], bool | None] | None,
) -> None:
    """Run webcam capture/recognition/rendering loop."""
    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"Unable to open camera index {camera_index}. Check connected devices and camera_index.")

    recognition_first_seen: dict[str, float] = {}

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break

            should_stop = _process_frame(
                frame=frame,
                known_face_encodings=known_face_encodings,
                known_face_names=known_face_names,
                scale_factor=scale_factor,
                recognition_delay_seconds=recognition_delay_seconds,
                recognition_first_seen=recognition_first_seen,
                current_time=time.monotonic(),
                on_face_recognized=on_face_recognized,
            )

            cv2.imshow(window_name, frame)
            if should_stop:
                break
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except KeyboardInterrupt:
        logger.info("Webcam attendance stopped by user.")
    finally:
        capture.release()
        cv2.destroyAllWindows()


def _process_frame(
    frame: Any,
    known_face_encodings: list[Any],
    known_face_names: list[str],
    scale_factor: float,
    on_face_recognized: Callable[[str], bool | None] | None,
    recognition_delay_seconds: float = 0.0,
    recognition_first_seen: dict[str, float] | None = None,
    current_time: float | None = None,
) -> bool:
    """Process one frame and return whether caller should stop capture loop."""
    if recognition_first_seen is None:
        recognition_first_seen = {}
    if current_time is None:
        current_time = time.monotonic()
    return process_frame(
        frame=frame,
        known_face_encodings=known_face_encodings,
        known_face_names=known_face_names,
        scale_factor=scale_factor,
        on_face_recognized=on_face_recognized,
        recognition_delay_seconds=recognition_delay_seconds,
        recognition_first_seen=recognition_first_seen,
        current_time=current_time,
    )
