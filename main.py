"""Webcam capture script entrypoint."""

from __future__ import annotations

from app.config import AppConfig
from app.orchestration import run_attendance_app


def main() -> None:
    """Start the webcam attendance preview loop."""
    run_attendance_app(AppConfig())


if __name__ == "__main__":
    main()
