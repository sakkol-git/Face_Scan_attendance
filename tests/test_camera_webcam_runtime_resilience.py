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

        result = _process_frame(
            frame=frame,
            known_face_encodings=[],
            known_face_names=[],
            frame_scale=0.25,
            recognition_threshold=0.6,
            recognition_min_confidence=0.5,
            max_faces_per_frame=0,
            on_face_recognized=None,
        )

        self.assertFalse(result.should_stop)
        mock_face_locations.assert_called_once()
        mock_logger_exception.assert_called_once()

    @patch("camera.frame_processor.logger.exception")
    @patch("camera.frame_processor.resolve_match", return_value=("Alice", 0.9))
    @patch("camera.frame_processor.draw_face_overlay")
    @patch("camera.frame_processor.face_recognition.face_encodings", return_value=["enc"])
    @patch("camera.frame_processor.face_recognition.face_locations", return_value=[(1, 2, 3, 4)])
    def test_callback_exception_is_logged_and_loop_continues(
        self,
        mock_face_locations: MagicMock,
        mock_face_encodings: MagicMock,
        mock_draw_face_overlay: MagicMock,
        mock_resolve_match: MagicMock,
        mock_logger_exception: MagicMock,
    ) -> None:
        frame = np.zeros((10, 10, 3), dtype=np.uint8)
        callback = MagicMock(side_effect=RuntimeError("callback error"))

        result = _process_frame(
            frame=frame,
            known_face_encodings=["enc"],
            known_face_names=["Alice"],
            frame_scale=0.25,
            recognition_threshold=0.6,
            recognition_min_confidence=0.5,
            max_faces_per_frame=0,
            on_face_recognized=callback,
        )

        self.assertFalse(result.should_stop)
        callback.assert_called_once_with("Alice")
        mock_logger_exception.assert_called_once()


if __name__ == "__main__":
    unittest.main()