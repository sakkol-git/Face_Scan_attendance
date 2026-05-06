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
        upload_cooldown_seconds=config.upload_cooldown_seconds,
        upload_max_retries=config.upload_max_retries,
        upload_backoff_base_seconds=config.upload_backoff_base_seconds,
        upload_backoff_max_seconds=config.upload_backoff_max_seconds,
        fallback_csv_path=config.fallback_csv_path,
    )

    run_webcam_attendance(
        known_face_encodings=known_face_encodings,
        known_face_names=known_face_names,
        camera_index=config.camera_index,
        window_name=config.window_name,
        frame_scale=config.frame_scale,
        recognition_delay_seconds=config.recognition_delay_seconds,
        recognition_threshold=config.recognition_threshold,
        recognition_min_confidence=config.recognition_min_confidence,
        process_every_n_frames=config.process_every_n_frames,
        max_faces_per_frame=config.max_faces_per_frame,
        on_face_recognized=handle_recognized_face,
    )
