"""Attendance time and deduplication logic."""

from __future__ import annotations

from datetime import datetime

marked_today: set[str] = set()


def _build_cutoff_time(reference: datetime) -> datetime:
    """Return the attendance cutoff for the provided date."""
    return reference.replace(hour=8, minute=15, second=0, microsecond=0)


def get_attendance_status(now: datetime | None = None) -> str:
    """Return attendance status based on the daily cutoff time.

    Args:
        now: Optional datetime value used for evaluation.

    Returns:
        "Present" when time is up to 08:15, otherwise "Late".
    """
    current_time = now or datetime.now()
    cutoff_time = _build_cutoff_time(current_time)
    return "Present" if current_time <= cutoff_time else "Late"


def should_mark(name: str) -> bool:
    """Track whether attendance was already marked for a name.

    Args:
        name: Recognized person identifier.

    Returns:
        True if this is the first mark for the name in this process; False otherwise.
    """
    if name in marked_today:
        return False

    marked_today.add(name)
    return True
