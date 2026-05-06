"""Per-frame recognition and callback processing."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

import face_recognition

from camera.delay_tracker import clear_stale_names, should_trigger_callback
from camera.matching import resolve_match
from camera.preprocess import scale_frame, to_rgb
from camera.render import FaceState, draw_face_overlay


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class FaceRecognitionResult:
    name: str | None
    state: FaceState
    confidence: float | None

    def as_dict(self) -> dict[str, str | None]:
        return {"name": self.name, "state": self.state}


@dataclass(frozen=True, slots=True)
class FrameProcessingResult:
    should_stop: bool
    results: list[FaceRecognitionResult]


def process_frame(
    frame: Any,
    known_face_encodings: list[Any],
    known_face_names: list[str],
    frame_scale: float,
    recognition_threshold: float,
    recognition_min_confidence: float,
    max_faces_per_frame: int,
    on_face_recognized: Callable[[str], FaceState | tuple[FaceState, bool] | None] | None,
    recognition_delay_seconds: float,
    recognition_first_seen: dict[str, float],
    current_time: float,
) -> FrameProcessingResult:
    """Process one frame and return results plus stop signal."""
    try:
        small_frame = scale_frame(frame, frame_scale)
        rgb_small = to_rgb(small_frame)

        face_locations = face_recognition.face_locations(rgb_small)
        if not face_locations:
            recognition_first_seen.clear()
            return FrameProcessingResult(False, [])

        if max_faces_per_frame > 0:
            face_locations = face_locations[:max_faces_per_frame]

        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)
    except Exception as error:
        logger.exception("Frame recognition failed: %s", error)
        return FrameProcessingResult(False, [])

    names_in_frame: set[str] = set()
    results: list[FaceRecognitionResult] = []

    should_stop = False
    for face_encoding, face_location in zip(face_encodings, face_locations):
        name, confidence = resolve_match(
            face_encoding,
            known_face_encodings,
            known_face_names,
            threshold=recognition_threshold,
        )
        if name != "Unknown" and confidence < recognition_min_confidence:
            name = "Unknown"
            confidence = None
        state: FaceState = "unknown" if name == "Unknown" else "recognized"
        if name == "Unknown":
            confidence = None

        if name != "Unknown":
            names_in_frame.add(name)

        if on_face_recognized is not None and name != "Unknown":
            if should_trigger_callback(
                name,
                recognition_delay_seconds=recognition_delay_seconds,
                recognition_first_seen=recognition_first_seen,
                current_time=current_time,
            ):
                try:
                    callback_result = on_face_recognized(name)
                    if isinstance(callback_result, tuple):
                        callback_state, callback_stop = callback_result
                    else:
                        callback_state, callback_stop = callback_result, False

                    if callback_state in ("recognized", "uploaded"):
                        state = callback_state
                    if callback_stop:
                        should_stop = True
                except Exception as error:
                    logger.exception("on_face_recognized callback failed for %s: %s", name, error)

        results.append(
            FaceRecognitionResult(
                None if name == "Unknown" else name,
                state,
                confidence,
            )
        )
        draw_face_overlay(
            frame,
            face_location,
            None if name == "Unknown" else name,
            state,
            confidence,
            frame_scale,
        )

    clear_stale_names(recognition_first_seen, names_in_frame)
    return FrameProcessingResult(should_stop, results)
