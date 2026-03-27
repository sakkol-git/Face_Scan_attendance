"""Application-level attendance orchestration.

Why this module exists: combines attendance policy and persistence side effects
behind one callback factory used by the webcam runtime.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from attendance.logic import get_attendance_status, should_mark
from attendance.sheets import upload_to_sheets_async


def build_face_recognized_handler(
    sheet: Any,
    *,
    stop_after_success: bool = False,
    logger: logging.Logger | None = None,
) -> Callable[[str], bool]:
    """Return callback invoked for each recognized face name.

    The callback applies deduplication, computes attendance status, performs
    asynchronous persistence, and returns whether scanning should stop.
    """
    runtime_logger = logger or logging.getLogger(__name__)

    def handle_recognized_face(name: str) -> bool:
        if name == "Unknown":
            return False

        if not should_mark(name):
            return False

        status = get_attendance_status()
        if sheet is not None:
            upload_to_sheets_async(sheet, name, status)
            runtime_logger.info("Attendance marked for %s (%s).", name, status)
        else:
            runtime_logger.warning("Attendance for %s (%s) not uploaded because sheet is unavailable.", name, status)

        return stop_after_success

    return handle_recognized_face
