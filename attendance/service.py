"""Application-level attendance orchestration.

Why this module exists: combines attendance policy and persistence side effects
behind one callback factory used by the webcam runtime.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from attendance.logic import get_attendance_status
from attendance.sheets import SheetUploadWorker


def build_face_recognized_handler(
    sheet: Any,
    *,
    stop_after_success: bool = False,
    upload_cooldown_seconds: float = 60.0,
    upload_max_retries: int = 3,
    upload_backoff_base_seconds: float = 1.0,
    upload_backoff_max_seconds: float = 8.0,
    fallback_csv_path: str | None = None,
    logger: logging.Logger | None = None,
) -> Callable[[str], tuple[str, bool]]:
    """Return callback invoked for each recognized face name.

    The callback applies deduplication, computes attendance status, performs
    asynchronous persistence, and returns whether scanning should stop.
    """
    runtime_logger = logger or logging.getLogger(__name__)
    marked: set[str] = set()
    worker = SheetUploadWorker(
        sheet,
        max_retries=upload_max_retries,
        backoff_base_seconds=upload_backoff_base_seconds,
        backoff_max_seconds=upload_backoff_max_seconds,
        dedupe_cooldown_seconds=upload_cooldown_seconds,
        fallback_csv_path=fallback_csv_path,
        worker_logger=runtime_logger,
    )

    def handle_recognized_face(name: str) -> tuple[str, bool]:
        if name == "Unknown":
            return "recognized", False
        now = datetime.now()
        if name in marked:
            return "uploaded", False

        status = get_attendance_status(now)
        if sheet is None and not fallback_csv_path:
            runtime_logger.warning("Attendance for %s (%s) not uploaded because sheet is unavailable.", name, status)
            return "recognized", False

        accepted = worker.enqueue(name, status)
        if accepted:
            marked.add(name)
            runtime_logger.info("Attendance queued for %s (%s).", name, status)
        else:
            runtime_logger.debug("Attendance skipped for %s due to in-flight/duplicate dedupe.", name)

        return "uploaded", stop_after_success

    return handle_recognized_face
