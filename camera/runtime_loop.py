"""Webcam attendance runtime loop."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

import cv2

from camera.frame_processor import FrameProcessingResult, process_frame

logger = logging.getLogger(__name__)


def run_webcam_loop(
    known_face_encodings: list[Any],
    known_face_names: list[str],
    camera_index: int,
    window_name: str,
    frame_scale: float,
    recognition_threshold: float,
    recognition_min_confidence: float,
    process_every_n_frames: int,
    max_faces_per_frame: int,
    recognition_delay_seconds: float,
    on_face_recognized: Callable[[str], str | tuple[str, bool] | None] | None,
) -> None:
    """Run webcam capture/recognition/rendering loop."""
    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"Unable to open camera index {camera_index}. Check connected devices and camera_index.")

    recognition_first_seen: dict[str, float] = {}
    frame_index = 0

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break

            frame_index += 1
            should_process = process_every_n_frames <= 1 or frame_index % process_every_n_frames == 0
            should_stop = False

            if should_process:
                result = _process_frame(
                    frame=frame,
                    known_face_encodings=known_face_encodings,
                    known_face_names=known_face_names,
                    frame_scale=frame_scale,
                    recognition_threshold=recognition_threshold,
                    recognition_min_confidence=recognition_min_confidence,
                    max_faces_per_frame=max_faces_per_frame,
                    recognition_delay_seconds=recognition_delay_seconds,
                    recognition_first_seen=recognition_first_seen,
                    current_time=time.monotonic(),
                    on_face_recognized=on_face_recognized,
                )
                should_stop = result.should_stop

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
    frame_scale: float,
    recognition_threshold: float,
    recognition_min_confidence: float,
    max_faces_per_frame: int,
    on_face_recognized: Callable[[str], str | tuple[str, bool] | None] | None,
    recognition_delay_seconds: float = 0.0,
    recognition_first_seen: dict[str, float] | None = None,
    current_time: float | None = None,
) -> FrameProcessingResult:
    """Process one frame and return whether caller should stop capture loop."""
    if recognition_first_seen is None:
        recognition_first_seen = {}
    if current_time is None:
        current_time = time.monotonic()
    return process_frame(
        frame=frame,
        known_face_encodings=known_face_encodings,
        known_face_names=known_face_names,
        frame_scale=frame_scale,
        recognition_threshold=recognition_threshold,
        max_faces_per_frame=max_faces_per_frame,
        on_face_recognized=on_face_recognized,
        recognition_delay_seconds=recognition_delay_seconds,
        recognition_first_seen=recognition_first_seen,
        current_time=current_time,
        recognition_min_confidence=recognition_min_confidence,
    )
