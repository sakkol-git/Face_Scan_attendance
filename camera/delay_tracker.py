"""Recognition delay state helpers."""

from __future__ import annotations


def should_trigger_callback(
    name: str,
    *,
    recognition_delay_seconds: float,
    recognition_first_seen: dict[str, float],
    current_time: float,
) -> bool:
    """Return whether callback should run based on continuous recognition delay."""
    first_seen = recognition_first_seen.setdefault(name, current_time)
    elapsed = current_time - first_seen
    return recognition_delay_seconds <= 0 or elapsed >= recognition_delay_seconds


def clear_stale_names(recognition_first_seen: dict[str, float], names_in_frame: set[str]) -> None:
    """Remove tracked names that are no longer present in the current frame."""
    stale_names = [tracked_name for tracked_name in recognition_first_seen if tracked_name not in names_in_frame]
    for tracked_name in stale_names:
        del recognition_first_seen[tracked_name]
