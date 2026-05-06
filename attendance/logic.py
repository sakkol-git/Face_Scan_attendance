"""Attendance time and deduplication logic."""

from __future__ import annotations

from datetime import datetime


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


def should_mark(
    name: str,
    *,
    now: datetime,
    last_seen: dict[str, datetime],
    cooldown_seconds: float,
) -> bool:
    """Return True when name is outside its cooldown window.

    Args:
        name: Recognized person identifier.
        now: Current timestamp for evaluation.
        last_seen: Mapping of name to last upload time.
        cooldown_seconds: Minimum seconds between uploads for one name.
    """
    last_marked = last_seen.get(name)
    if last_marked is None:
        return True
    return (now - last_marked).total_seconds() >= cooldown_seconds
