"""Typed runtime configuration for attendance application."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Runtime knobs for camera loop and recognition flow."""

    # Root folder containing per-person subfolders (each folder name becomes the label).
    known_faces_dir: str = "known_faces"
    # OpenCV camera index (0 is usually the default webcam).
    camera_index: int = 0
    # Window title shown by OpenCV for the live preview.
    window_name: str = "Attendance System"
    # Scale factor for frames before detection; lower is faster but less accurate.
    frame_scale: float = 0.25
    # Continuous recognition duration before a face can trigger upload.
    recognition_delay_seconds: float = 3.0
    # Maximum face distance accepted as a match (lower is stricter).
    recognition_threshold: float = 0.6
    # Minimum confidence (0-1) required in addition to the distance threshold.
    recognition_min_confidence: float = 0.3
    # Run recognition every N frames to reduce CPU usage (1 = every frame).
    process_every_n_frames: int = 1
    # Limit number of faces processed per frame (0 = no limit).
    max_faces_per_frame: int = 0
    # Cooldown for upload queue dedupe window (seconds).
    upload_cooldown_seconds: float = 60.0
    # Maximum number of upload retries for a single row.
    upload_max_retries: int = 3
    # Initial backoff delay for upload retries (seconds).
    upload_backoff_base_seconds: float = 1.0
    # Maximum backoff delay for upload retries (seconds).
    upload_backoff_max_seconds: float = 8.0
    # Optional CSV file path used when Sheets uploads are unavailable.
    fallback_csv_path: str | None = None
    # Stop the webcam loop after the first successful upload.
    stop_after_success: bool = False
