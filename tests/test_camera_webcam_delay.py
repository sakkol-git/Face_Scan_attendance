from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from camera.runtime_loop import _process_frame


class TestWebcamRecognitionDelay(unittest.TestCase):
    @patch("camera.frame_processor.resolve_name", return_value="Alice")
    @patch("camera.frame_processor.draw_label")
    @patch("camera.frame_processor.face_recognition.face_encodings", return_value=["enc"])
    @patch("camera.frame_processor.face_recognition.face_locations", return_value=[(1, 2, 3, 4)])
    def test_callback_runs_after_continuous_delay(
        self,
        mock_face_locations: MagicMock,
        mock_face_encodings: MagicMock,
        mock_draw_label: MagicMock,
        mock_resolve_name: MagicMock,
    ) -> None:
        frame = np.zeros((10, 10, 3), dtype=np.uint8)
        callback = MagicMock(return_value=True)
        recognition_first_seen: dict[str, float] = {}

        self.assertFalse(
            _process_frame(
                frame=frame,
                known_face_encodings=["enc"],
                known_face_names=["Alice"],
                scale_factor=0.25,
                on_face_recognized=callback,
                recognition_delay_seconds=3.0,
                recognition_first_seen=recognition_first_seen,
                current_time=10.0,
            )
        )
        self.assertFalse(
            _process_frame(
                frame=frame,
                known_face_encodings=["enc"],
                known_face_names=["Alice"],
                scale_factor=0.25,
                on_face_recognized=callback,
                recognition_delay_seconds=3.0,
                recognition_first_seen=recognition_first_seen,
                current_time=12.0,
            )
        )
        self.assertTrue(
            _process_frame(
                frame=frame,
                known_face_encodings=["enc"],
                known_face_names=["Alice"],
                scale_factor=0.25,
                on_face_recognized=callback,
                recognition_delay_seconds=3.0,
                recognition_first_seen=recognition_first_seen,
                current_time=13.0,
            )
        )
        callback.assert_called_once_with("Alice")

    @patch("camera.frame_processor.resolve_name", return_value="Alice")
    @patch("camera.frame_processor.draw_label")
    @patch("camera.frame_processor.face_recognition.face_encodings", return_value=["enc"])
    @patch("camera.frame_processor.face_recognition.face_locations")
    def test_delay_cache_resets_when_face_disappears(
        self,
        mock_face_locations: MagicMock,
        mock_face_encodings: MagicMock,
        mock_draw_label: MagicMock,
        mock_resolve_name: MagicMock,
    ) -> None:
        frame = np.zeros((10, 10, 3), dtype=np.uint8)
        callback = MagicMock(return_value=True)
        recognition_first_seen: dict[str, float] = {}
        mock_face_locations.side_effect = [[(1, 2, 3, 4)], [], [(1, 2, 3, 4)]]

        self.assertFalse(
            _process_frame(
                frame=frame,
                known_face_encodings=["enc"],
                known_face_names=["Alice"],
                scale_factor=0.25,
                on_face_recognized=callback,
                recognition_delay_seconds=3.0,
                recognition_first_seen=recognition_first_seen,
                current_time=10.0,
            )
        )
        self.assertIn("Alice", recognition_first_seen)

        self.assertFalse(
            _process_frame(
                frame=frame,
                known_face_encodings=["enc"],
                known_face_names=["Alice"],
                scale_factor=0.25,
                on_face_recognized=callback,
                recognition_delay_seconds=3.0,
                recognition_first_seen=recognition_first_seen,
                current_time=20.0,
            )
        )
        self.assertEqual(recognition_first_seen, {})

        self.assertFalse(
            _process_frame(
                frame=frame,
                known_face_encodings=["enc"],
                known_face_names=["Alice"],
                scale_factor=0.25,
                on_face_recognized=callback,
                recognition_delay_seconds=3.0,
                recognition_first_seen=recognition_first_seen,
                current_time=21.0,
            )
        )
        callback.assert_not_called()


if __name__ == "__main__":
    unittest.main()
