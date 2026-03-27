"""Record-shaping helpers for attendance rows."""

from __future__ import annotations

from datetime import datetime


def build_attendance_row(name: str, status: str, now: datetime | None = None) -> list[str]:
    """Build one row payload in [date, time, name, status] format."""
    timestamp = now or datetime.now()
    date_str = timestamp.strftime("%Y-%m-%d")
    time_str = timestamp.strftime("%H:%M:%S")
    return [date_str, time_str, name, status]
