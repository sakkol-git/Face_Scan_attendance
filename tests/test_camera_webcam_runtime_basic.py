from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from camera import webcam


class TestRunWebcamAttendanceBasic(unittest.TestCase):
    @patch("camera.runtime_loop.cv2.VideoCapture")
    def test_raises_when_camera_unavailable(self, mock_video_capture: MagicMock) -> None:
        capture = MagicMock()
        capture.isOpened.return_value = False
        mock_video_capture.return_value = capture

        with self.assertRaises(RuntimeError):
            webcam.run_webcam_attendance(
                known_face_encodings=[],
                known_face_names=[],
                camera_index=1,
            )

        capture.release.assert_called_once()

    @patch("camera.runtime_loop.cv2.destroyAllWindows")
    @patch("camera.runtime_loop.cv2.VideoCapture")
    @patch("camera.runtime_loop._process_frame", side_effect=KeyboardInterrupt)
    def test_keyboard_interrupt_exits_cleanly(
        self,
        mock_process_frame: MagicMock,
        mock_video_capture: MagicMock,
        mock_destroy_windows: MagicMock,
    ) -> None:
        capture = MagicMock()
        capture.isOpened.return_value = True
        capture.read.return_value = (True, np.zeros((10, 10, 3), dtype=np.uint8))
        mock_video_capture.return_value = capture

        webcam.run_webcam_attendance(known_face_encodings=[], known_face_names=[], camera_index=0)

        capture.release.assert_called_once()
        mock_destroy_windows.assert_called_once()

    @patch("camera.runtime_loop.cv2.destroyAllWindows")
    @patch("camera.runtime_loop.cv2.waitKey", return_value=-1)
    @patch("camera.runtime_loop.cv2.imshow")
    @patch("camera.runtime_loop.cv2.VideoCapture")
    @patch("camera.runtime_loop._process_frame", return_value=True)
    def test_callback_true_stops_loop(
        self,
        mock_process_frame: MagicMock,
        mock_video_capture: MagicMock,
        mock_imshow: MagicMock,
        mock_wait_key: MagicMock,
        mock_destroy_windows: MagicMock,
    ) -> None:
        capture = MagicMock()
        capture.isOpened.return_value = True
        capture.read.side_effect = [
            (True, np.zeros((10, 10, 3), dtype=np.uint8)),
            (True, np.zeros((10, 10, 3), dtype=np.uint8)),
        ]
        mock_video_capture.return_value = capture

        webcam.run_webcam_attendance(known_face_encodings=["enc"], known_face_names=["Alice"], camera_index=0)

        self.assertEqual(capture.read.call_count, 1)
        mock_process_frame.assert_called_once()
        capture.release.assert_called_once()
        mock_destroy_windows.assert_called_once()


if __name__ == "__main__":
    unittest.main()
