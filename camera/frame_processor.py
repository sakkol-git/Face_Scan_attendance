"""Per-frame recognition and callback processing."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import face_recognition

from camera.delay_tracker import clear_stale_names, should_trigger_callback
from camera.matching import resolve_name
from camera.preprocess import scale_frame, to_rgb
from camera.render import draw_label


logger = logging.getLogger(__name__)


def process_frame(
    frame: Any,
    known_face_encodings: list[Any],
    known_face_names: list[str],
    scale_factor: float,
    on_face_recognized: Callable[[str], bool | None] | None,
    recognition_delay_seconds: float,
    recognition_first_seen: dict[str, float],
    current_time: float,
) -> bool:
    """Process one frame and return whether caller should stop capture loop."""
    try:
        small_frame = scale_frame(frame, scale_factor)
        rgb_small = to_rgb(small_frame)

        face_locations = face_recognition.face_locations(rgb_small)
        if not face_locations:
            recognition_first_seen.clear()
            return False

        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)
    except Exception as error:
        logger.exception("Frame recognition failed: %s", error)
        return False

    names_in_frame: set[str] = set()

    for face_encoding, face_location in zip(face_encodings, face_locations):
        name = resolve_name(face_encoding, known_face_encodings, known_face_names)
        draw_label(frame, face_location, name, scale_factor)

        if name != "Unknown":
            names_in_frame.add(name)

        if on_face_recognized is None or name == "Unknown":
            continue

        if not should_trigger_callback(
            name,
            recognition_delay_seconds=recognition_delay_seconds,
            recognition_first_seen=recognition_first_seen,
            current_time=current_time,
        ):
            continue

        try:
            callback_result = on_face_recognized(name)
        except Exception as error:
            logger.exception("on_face_recognized callback failed for %s: %s", name, error)
            callback_result = False

        if callback_result is True:
            return True

    clear_stale_names(recognition_first_seen, names_in_frame)
    return False
