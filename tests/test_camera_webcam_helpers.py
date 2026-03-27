from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from camera.matching import resolve_name
from camera.preprocess import to_rgb


class TestCameraWebcamHelpers(unittest.TestCase):
    def test_to_rgb_returns_contiguous_rgb_frame(self) -> None:
        bgr = np.array([[[0, 1, 2], [10, 11, 12]]], dtype=np.uint8)

        rgb = to_rgb(bgr)

        self.assertEqual(rgb.dtype, np.uint8)
        self.assertTrue(rgb.flags["C_CONTIGUOUS"])
        self.assertEqual(rgb.tolist(), [[[2, 1, 0], [12, 11, 10]]])

    @patch("camera.matching.face_recognition.compare_faces")
    @patch("camera.matching.face_recognition.face_distance")
    def test_resolve_name_returns_known_match(
        self,
        mock_face_distance: MagicMock,
        mock_compare_faces: MagicMock,
    ) -> None:
        mock_compare_faces.return_value = [False, True]
        mock_face_distance.return_value = [0.9, 0.4]

        result = resolve_name(
            face_encoding="candidate",
            known_face_encodings=["enc-1", "enc-2"],
            known_face_names=["Alice", "Bob"],
        )

        self.assertEqual(result, "Bob")

    @patch("camera.matching.face_recognition.compare_faces")
    @patch("camera.matching.face_recognition.face_distance")
    def test_resolve_name_returns_unknown_when_no_match(
        self,
        mock_face_distance: MagicMock,
        mock_compare_faces: MagicMock,
    ) -> None:
        mock_compare_faces.return_value = [False, False]
        mock_face_distance.return_value = [0.9, 0.8]

        result = resolve_name(
            face_encoding="candidate",
            known_face_encodings=["enc-1", "enc-2"],
            known_face_names=["Alice", "Bob"],
        )

        self.assertEqual(result, "Unknown")


if __name__ == "__main__":
    unittest.main()
