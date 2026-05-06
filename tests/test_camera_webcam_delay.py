from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from camera.runtime_loop import _process_frame


class TestWebcamRecognitionDelay(unittest.TestCase):
    @patch("camera.frame_processor.resolve_match", return_value=("Alice", 0.9))
    @patch("camera.frame_processor.draw_face_overlay")
    @patch("camera.frame_processor.face_recognition.face_encodings", return_value=["enc"])
    @patch("camera.frame_processor.face_recognition.face_locations", return_value=[(1, 2, 3, 4)])
    def test_callback_runs_after_continuous_delay(
        self,
        mock_face_locations: MagicMock,
        mock_face_encodings: MagicMock,
        mock_draw_face_overlay: MagicMock,
        mock_resolve_match: MagicMock,
    ) -> None:
        frame = np.zeros((10, 10, 3), dtype=np.uint8)
        callback = MagicMock(return_value=("uploaded", True))
        recognition_first_seen: dict[str, float] = {}

        self.assertFalse(
            _process_frame(
                frame=frame,
                known_face_encodings=["enc"],
                known_face_names=["Alice"],
                frame_scale=0.25,
                recognition_threshold=0.6,
                recognition_min_confidence=0.5,
                max_faces_per_frame=0,
                on_face_recognized=callback,
                recognition_delay_seconds=3.0,
                recognition_first_seen=recognition_first_seen,
                current_time=10.0,
            ).should_stop
        )
        self.assertFalse(
            _process_frame(
                frame=frame,
                known_face_encodings=["enc"],
                known_face_names=["Alice"],
                frame_scale=0.25,
                recognition_threshold=0.6,
                recognition_min_confidence=0.5,
                max_faces_per_frame=0,
                on_face_recognized=callback,
                recognition_delay_seconds=3.0,
                recognition_first_seen=recognition_first_seen,
                current_time=12.0,
            ).should_stop
        )
        self.assertTrue(
            _process_frame(
                frame=frame,
                known_face_encodings=["enc"],
                known_face_names=["Alice"],
                frame_scale=0.25,
                recognition_threshold=0.6,
                recognition_min_confidence=0.5,
                max_faces_per_frame=0,
                on_face_recognized=callback,
                recognition_delay_seconds=3.0,
                recognition_first_seen=recognition_first_seen,
                current_time=13.0,
            ).should_stop
        )
        callback.assert_called_once_with("Alice")

    @patch("camera.frame_processor.resolve_match", return_value=("Alice", 0.9))
    @patch("camera.frame_processor.draw_face_overlay")
    @patch("camera.frame_processor.face_recognition.face_encodings", return_value=["enc"])
    @patch("camera.frame_processor.face_recognition.face_locations")
    def test_delay_cache_resets_when_face_disappears(
        self,
        mock_face_locations: MagicMock,
        mock_face_encodings: MagicMock,
        mock_draw_face_overlay: MagicMock,
        mock_resolve_match: MagicMock,
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
                frame_scale=0.25,
                recognition_threshold=0.6,
                recognition_min_confidence=0.5,
                max_faces_per_frame=0,
                on_face_recognized=callback,
                recognition_delay_seconds=3.0,
                recognition_first_seen=recognition_first_seen,
                current_time=10.0,
            ).should_stop
        )
        self.assertIn("Alice", recognition_first_seen)

        self.assertFalse(
            _process_frame(
                frame=frame,
                known_face_encodings=["enc"],
                known_face_names=["Alice"],
                frame_scale=0.25,
                recognition_threshold=0.6,
                recognition_min_confidence=0.5,
                max_faces_per_frame=0,
                on_face_recognized=callback,
                recognition_delay_seconds=3.0,
                recognition_first_seen=recognition_first_seen,
                current_time=20.0,
            ).should_stop
        )
        self.assertEqual(recognition_first_seen, {})

        self.assertFalse(
            _process_frame(
                frame=frame,
                known_face_encodings=["enc"],
                known_face_names=["Alice"],
                frame_scale=0.25,
                recognition_threshold=0.6,
                recognition_min_confidence=0.5,
                max_faces_per_frame=0,
                on_face_recognized=callback,
                recognition_delay_seconds=3.0,
                recognition_first_seen=recognition_first_seen,
                current_time=21.0,
            ).should_stop
        )
        callback.assert_not_called()


if __name__ == "__main__":
    unittest.main()
