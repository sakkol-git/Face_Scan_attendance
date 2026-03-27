"""Typed runtime configuration for attendance application."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Runtime knobs for camera loop and recognition flow."""

    known_faces_dir: str = "known_faces"
    camera_index: int = 0
    window_name: str = "Attendance System"
    scale_factor: float = 0.25
    recognition_delay_seconds: float = 3.0
    stop_after_success: bool = False
