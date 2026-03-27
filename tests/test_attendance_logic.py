from __future__ import annotations

import unittest
from datetime import datetime

from attendance.logic import get_attendance_status, marked_today, should_mark


class TestAttendanceLogic(unittest.TestCase):
    def setUp(self) -> None:
        marked_today.clear()

    def tearDown(self) -> None:
        marked_today.clear()

    def test_get_attendance_status_present_before_cutoff(self) -> None:
        now = datetime(2026, 3, 27, 8, 0, 0)
        self.assertEqual(get_attendance_status(now), "Present")

    def test_get_attendance_status_present_at_cutoff(self) -> None:
        now = datetime(2026, 3, 27, 8, 15, 0)
        self.assertEqual(get_attendance_status(now), "Present")

    def test_get_attendance_status_late_after_cutoff(self) -> None:
        now = datetime(2026, 3, 27, 8, 15, 1)
        self.assertEqual(get_attendance_status(now), "Late")

    def test_should_mark_returns_true_then_false_for_same_name(self) -> None:
        self.assertTrue(should_mark("Alice"))
        self.assertFalse(should_mark("Alice"))

    def test_should_mark_independent_names(self) -> None:
        self.assertTrue(should_mark("Alice"))
        self.assertTrue(should_mark("Bob"))


if __name__ == "__main__":
    unittest.main()
