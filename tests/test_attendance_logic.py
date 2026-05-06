from __future__ import annotations

import unittest
from datetime import datetime, timedelta

from attendance.logic import get_attendance_status, should_mark


class TestAttendanceLogic(unittest.TestCase):
    def test_get_attendance_status_present_before_cutoff(self) -> None:
        now = datetime(2026, 3, 27, 8, 0, 0)
        self.assertEqual(get_attendance_status(now), "Present")

    def test_get_attendance_status_present_at_cutoff(self) -> None:
        now = datetime(2026, 3, 27, 8, 15, 0)
        self.assertEqual(get_attendance_status(now), "Present")

    def test_get_attendance_status_late_after_cutoff(self) -> None:
        now = datetime(2026, 3, 27, 8, 15, 1)
        self.assertEqual(get_attendance_status(now), "Late")

    def test_should_mark_respects_cooldown(self) -> None:
        last_seen: dict[str, datetime] = {}
        now = datetime(2026, 3, 27, 8, 0, 0)

        self.assertTrue(should_mark("Alice", now=now, last_seen=last_seen, cooldown_seconds=60.0))
        last_seen["Alice"] = now

        too_soon = now + timedelta(seconds=30)
        self.assertFalse(should_mark("Alice", now=too_soon, last_seen=last_seen, cooldown_seconds=60.0))

        after_cooldown = now + timedelta(seconds=61)
        self.assertTrue(should_mark("Alice", now=after_cooldown, last_seen=last_seen, cooldown_seconds=60.0))

    def test_should_mark_independent_names(self) -> None:
        last_seen: dict[str, datetime] = {}
        now = datetime(2026, 3, 27, 8, 0, 0)
        self.assertTrue(should_mark("Alice", now=now, last_seen=last_seen, cooldown_seconds=60.0))
        self.assertTrue(should_mark("Bob", now=now, last_seen=last_seen, cooldown_seconds=60.0))


if __name__ == "__main__":
    unittest.main()
