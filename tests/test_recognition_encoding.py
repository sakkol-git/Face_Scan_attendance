from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from recognition.encoding import load_known_faces


class TestRecognitionEncoding(unittest.TestCase):
    @patch("recognition.encoding.logger.warning")
    def test_load_known_faces_returns_empty_when_directory_missing(self, mock_logger_warning) -> None:
        encodings, names = load_known_faces("/tmp/non-existent-known-faces-dir")
        self.assertEqual(encodings, [])
        self.assertEqual(names, [])
        mock_logger_warning.assert_called_once()

    @patch("recognition.encoding.logger.exception")
    @patch("recognition.encoding.logger.warning")
    @patch("recognition.encoding.face_recognition.face_encodings")
    @patch("recognition.encoding.face_recognition.load_image_file")
    def test_load_known_faces_skips_invalid_and_keeps_valid(
        self,
        mock_load_image_file,
        mock_face_encodings,
        mock_logger_warning,
        mock_logger_exception,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            valid = folder / "alice.jpg"
            no_face = folder / "bob.jpg"
            bad = folder / "charlie.jpg"
            nested = folder / "nested"

            valid.write_text("x", encoding="utf-8")
            no_face.write_text("x", encoding="utf-8")
            bad.write_text("x", encoding="utf-8")
            nested.mkdir()

            mock_load_image_file.side_effect = lambda file_path: file_path

            def fake_face_encodings(image):
                if image.endswith("alice.jpg"):
                    return [["enc-alice"]]
                if image.endswith("bob.jpg"):
                    return []
                raise ValueError("decode failed")

            mock_face_encodings.side_effect = fake_face_encodings

            encodings, names = load_known_faces(folder)

        self.assertEqual(encodings, [["enc-alice"]])
        self.assertEqual(names, ["alice"])
        mock_logger_warning.assert_called()
        mock_logger_exception.assert_called_once()

    @patch("recognition.encoding.face_recognition.face_encodings", return_value=[["enc-alice"]])
    @patch("recognition.encoding.face_recognition.load_image_file")
    def test_load_known_faces_ignores_non_image_files(
        self,
        mock_load_image_file,
        mock_face_encodings,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            (folder / "alice.jpg").write_text("x", encoding="utf-8")
            (folder / "readme.txt").write_text("x", encoding="utf-8")

            encodings, names = load_known_faces(folder)

        self.assertEqual(encodings, [["enc-alice"]])
        self.assertEqual(names, ["alice"])
        mock_load_image_file.assert_called_once()
        mock_face_encodings.assert_called_once()

    @patch("recognition.encoding.iter_face_files", side_effect=PermissionError("denied"))
    @patch("recognition.encoding.logger.exception")
    def test_load_known_faces_handles_listing_failure(
        self,
        mock_logger_exception,
        mock_iter_face_files,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            encodings, names = load_known_faces(temp_dir)

        self.assertEqual(encodings, [])
        self.assertEqual(names, [])
        mock_iter_face_files.assert_called_once()
        mock_logger_exception.assert_called_once()


if __name__ == "__main__":
    unittest.main()
