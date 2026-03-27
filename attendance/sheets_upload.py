"""Upload execution helpers for attendance sheet writes."""

from __future__ import annotations

import logging
from typing import Any

from attendance.sheets_records import build_attendance_row


def upload_row(sheet: Any, row: list[str], logger: logging.Logger) -> None:
    """Append a prepared row and log failures without raising."""
    try:
        sheet.append_row(row)
    except Exception as error:
        logger.exception("Failed to upload attendance for %s: %s", row[2], error)


def upload_to_sheet(sheet: Any, name: str, status: str, logger: logging.Logger) -> None:
    """Prepare and append one attendance record."""
    row = build_attendance_row(name=name, status=status)
    upload_row(sheet, row, logger)
