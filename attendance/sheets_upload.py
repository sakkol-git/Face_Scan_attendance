"""Upload execution helpers for attendance sheet writes."""

from __future__ import annotations

import logging
from typing import Any

import csv
from pathlib import Path

from attendance.sheets_records import build_attendance_row


def upload_row(sheet: Any, row: list[str], logger: logging.Logger) -> bool:
    """Append a prepared row and log failures without raising."""
    try:
        sheet.append_row(row)
    except Exception as error:
        logger.exception("Failed to upload attendance for %s: %s", row[2], error)
        return False
    return True


def upload_to_sheet(sheet: Any, name: str, status: str, logger: logging.Logger) -> bool:
    """Prepare and append one attendance record."""
    row = build_attendance_row(name=name, status=status)
    return upload_row(sheet, row, logger)


def append_row_to_csv(csv_path: str | Path, row: list[str], logger: logging.Logger) -> bool:
    """Append a row to a local CSV file for fallback persistence."""
    path = Path(csv_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(row)
    except Exception as error:
        logger.exception("Failed to append attendance to CSV %s: %s", path, error)
        return False
    return True
