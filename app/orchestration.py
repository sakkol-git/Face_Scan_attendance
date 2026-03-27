"""Application orchestration entrypoint.

This module wires startup bootstrap, attendance callback policy, and webcam
runtime together while keeping `main.py` small and stable.
"""

from __future__ import annotations

from app.bootstrap import bootstrap_runtime
from app.config import AppConfig
from attendance.service import build_face_recognized_handler
from camera.webcam import run_webcam_attendance


def run_attendance_app(config: AppConfig) -> None:
    """Run one attendance session with the provided application configuration."""
    known_face_encodings, known_face_names, sheet = bootstrap_runtime(config.known_faces_dir)
    handle_recognized_face = build_face_recognized_handler(
        sheet,
        stop_after_success=config.stop_after_success,
    )

    run_webcam_attendance(
        known_face_encodings=known_face_encodings,
        known_face_names=known_face_names,
        camera_index=config.camera_index,
        window_name=config.window_name,
        scale_factor=config.scale_factor,
        recognition_delay_seconds=config.recognition_delay_seconds,
        on_face_recognized=handle_recognized_face,
    )
