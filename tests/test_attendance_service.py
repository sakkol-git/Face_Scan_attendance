from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from attendance.service import build_face_recognized_handler


class TestAttendanceService(unittest.TestCase):
    @patch("attendance.service.SheetUploadWorker")
    @patch("attendance.service.should_mark", return_value=False)
    def test_handler_skips_duplicates(
        self,
        mock_should_mark: MagicMock,
        mock_worker_class: MagicMock,
    ) -> None:
        worker_instance = MagicMock()
        mock_worker_class.return_value = worker_instance
        handler = build_face_recognized_handler(sheet=MagicMock())

        state, should_stop = handler("Alice")

        self.assertEqual(state, "uploaded")
        self.assertFalse(should_stop)
        mock_should_mark.assert_called_once()
        worker_instance.enqueue.assert_not_called()

    @patch("attendance.service.SheetUploadWorker")
    def test_handler_skips_unknown(self, mock_worker_class: MagicMock) -> None:
        worker_instance = MagicMock()
        mock_worker_class.return_value = worker_instance
        handler = build_face_recognized_handler(sheet=MagicMock())

        state, should_stop = handler("Unknown")

        self.assertEqual(state, "recognized")
        self.assertFalse(should_stop)
        worker_instance.enqueue.assert_not_called()

    @patch("attendance.service.SheetUploadWorker")
    @patch("attendance.service.get_attendance_status", return_value="Present")
    @patch("attendance.service.should_mark", return_value=True)
    def test_handler_default_continues_after_success(
        self,
        mock_should_mark: MagicMock,
        mock_get_status: MagicMock,
        mock_worker_class: MagicMock,
    ) -> None:
        worker_instance = MagicMock()
        mock_worker_class.return_value = worker_instance
        sheet = MagicMock()
        handler = build_face_recognized_handler(sheet=sheet)

        state, should_stop = handler("Alice")

        self.assertEqual(state, "uploaded")
        self.assertFalse(should_stop)
        mock_should_mark.assert_called_once()
        mock_get_status.assert_called_once()
        worker_instance.enqueue.assert_called_once_with("Alice", "Present")

    @patch("attendance.service.SheetUploadWorker")
    @patch("attendance.service.get_attendance_status", return_value="Present")
    @patch("attendance.service.should_mark", return_value=True)
    def test_handler_marks_and_stops_when_configured(
        self,
        mock_should_mark: MagicMock,
        mock_get_status: MagicMock,
        mock_worker_class: MagicMock,
    ) -> None:
        worker_instance = MagicMock()
        mock_worker_class.return_value = worker_instance
        sheet = MagicMock()
        handler = build_face_recognized_handler(sheet=sheet, stop_after_success=True)

        state, should_stop = handler("Alice")

        self.assertEqual(state, "uploaded")
        self.assertTrue(should_stop)
        mock_should_mark.assert_called_once()
        mock_get_status.assert_called_once()
        worker_instance.enqueue.assert_called_once_with("Alice", "Present")

    @patch("attendance.service.SheetUploadWorker")
    @patch("attendance.service.get_attendance_status", return_value="Late")
    @patch("attendance.service.should_mark", return_value=True)
    def test_handler_marks_without_stopping_when_configured(
        self,
        mock_should_mark: MagicMock,
        mock_get_status: MagicMock,
        mock_worker_class: MagicMock,
    ) -> None:
        worker_instance = MagicMock()
        mock_worker_class.return_value = worker_instance
        sheet = MagicMock()
        handler = build_face_recognized_handler(sheet=sheet, stop_after_success=False)

        state, should_stop = handler("Bob")

        self.assertEqual(state, "uploaded")
        self.assertFalse(should_stop)
        mock_should_mark.assert_called_once()
        mock_get_status.assert_called_once()
        worker_instance.enqueue.assert_called_once_with("Bob", "Late")


if __name__ == "__main__":
    unittest.main()
