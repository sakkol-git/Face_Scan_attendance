from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from attendance.service import build_face_recognized_handler


class TestAttendanceService(unittest.TestCase):
    @patch("attendance.service.should_mark", return_value=False)
    def test_handler_skips_duplicates(self, mock_should_mark: MagicMock) -> None:
        handler = build_face_recognized_handler(sheet=MagicMock())

        should_stop = handler("Alice")

        self.assertFalse(should_stop)
        mock_should_mark.assert_called_once_with("Alice")

    def test_handler_skips_unknown(self) -> None:
        handler = build_face_recognized_handler(sheet=MagicMock())

        should_stop = handler("Unknown")

        self.assertFalse(should_stop)

    @patch("attendance.service.upload_to_sheets_async")
    @patch("attendance.service.get_attendance_status", return_value="Present")
    @patch("attendance.service.should_mark", return_value=True)
    def test_handler_default_continues_after_success(
        self,
        mock_should_mark: MagicMock,
        mock_get_status: MagicMock,
        mock_upload_async: MagicMock,
    ) -> None:
        sheet = MagicMock()
        handler = build_face_recognized_handler(sheet=sheet)

        should_stop = handler("Alice")

        self.assertFalse(should_stop)
        mock_should_mark.assert_called_once_with("Alice")
        mock_get_status.assert_called_once()
        mock_upload_async.assert_called_once_with(sheet, "Alice", "Present")

    @patch("attendance.service.upload_to_sheets_async")
    @patch("attendance.service.get_attendance_status", return_value="Present")
    @patch("attendance.service.should_mark", return_value=True)
    def test_handler_marks_and_stops_when_configured(
        self,
        mock_should_mark: MagicMock,
        mock_get_status: MagicMock,
        mock_upload_async: MagicMock,
    ) -> None:
        sheet = MagicMock()
        handler = build_face_recognized_handler(sheet=sheet, stop_after_success=True)

        should_stop = handler("Alice")

        self.assertTrue(should_stop)
        mock_should_mark.assert_called_once_with("Alice")
        mock_get_status.assert_called_once()
        mock_upload_async.assert_called_once_with(sheet, "Alice", "Present")

    @patch("attendance.service.upload_to_sheets_async")
    @patch("attendance.service.get_attendance_status", return_value="Late")
    @patch("attendance.service.should_mark", return_value=True)
    def test_handler_marks_without_stopping_when_configured(
        self,
        mock_should_mark: MagicMock,
        mock_get_status: MagicMock,
        mock_upload_async: MagicMock,
    ) -> None:
        sheet = MagicMock()
        handler = build_face_recognized_handler(sheet=sheet, stop_after_success=False)

        should_stop = handler("Bob")

        self.assertFalse(should_stop)
        mock_should_mark.assert_called_once_with("Bob")
        mock_get_status.assert_called_once()
        mock_upload_async.assert_called_once_with(sheet, "Bob", "Late")


if __name__ == "__main__":
    unittest.main()
