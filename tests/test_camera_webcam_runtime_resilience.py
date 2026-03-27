from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from camera.runtime_loop import _process_frame


class TestRunWebcamAttendanceResilience(unittest.TestCase):
    @patch("camera.frame_processor.logger.exception")
    @patch("camera.frame_processor.face_recognition.face_locations", side_effect=RuntimeError("temporary detector failure"))
    def test_frame_recognition_error_is_logged_and_loop_continues(
        self,
        mock_face_locations: MagicMock,
        mock_logger_exception: MagicMock,
    ) -> None:
        frame = np.zeros((10, 10, 3), dtype=np.uint8)

        should_stop = _process_frame(
            frame=frame,
            known_face_encodings=[],
            known_face_names=[],
            scale_factor=0.25,
            on_face_recognized=None,
        )

        self.assertFalse(should_stop)
        mock_face_locations.assert_called_once()
        mock_logger_exception.assert_called_once()

    @patch("camera.frame_processor.logger.exception")
    @patch("camera.frame_processor.resolve_name", return_value="Alice")
    @patch("camera.frame_processor.draw_label")
    @patch("camera.frame_processor.face_recognition.face_encodings", return_value=["enc"])
    @patch("camera.frame_processor.face_recognition.face_locations", return_value=[(1, 2, 3, 4)])
    def test_callback_exception_is_logged_and_loop_continues(
        self,
        mock_face_locations: MagicMock,
        mock_face_encodings: MagicMock,
        mock_draw_label: MagicMock,
        mock_resolve_name: MagicMock,
        mock_logger_exception: MagicMock,
    ) -> None:
        frame = np.zeros((10, 10, 3), dtype=np.uint8)
        callback = MagicMock(side_effect=RuntimeError("callback error"))

        should_stop = _process_frame(
            frame=frame,
            known_face_encodings=["enc"],
            known_face_names=["Alice"],
            scale_factor=0.25,
            on_face_recognized=callback,
        )

        self.assertFalse(should_stop)
        callback.assert_called_once_with("Alice")
        mock_logger_exception.assert_called_once()


if __name__ == "__main__":
    unittest.main()