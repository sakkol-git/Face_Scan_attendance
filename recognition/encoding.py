"""Known face loading and preprocessing utilities."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import face_recognition

from recognition.file_sources import iter_face_files

logger = logging.getLogger(__name__)


def load_known_faces(known_faces_dir: str | Path = "known_faces") -> tuple[list[Any], list[str]]:
    """Load face encodings and names from a directory.

    Args:
        known_faces_dir: Folder that stores known-face images.

    Returns:
        A tuple containing the list of face encodings and corresponding names.
    """
    folder = Path(known_faces_dir)
    encodings: list[Any] = []
    names: list[str] = []

    if not folder.exists() or not folder.is_dir():
        logger.warning("Known faces directory not found: %s", folder)
        return encodings, names

    try:
        face_files = iter_face_files(folder)
    except Exception as error:
        logger.exception("Failed to list known face files in %s: %s", folder, error)
        return encodings, names

    for file_path in face_files:
        try:
            image = face_recognition.load_image_file(str(file_path))
            file_encodings = face_recognition.face_encodings(image)
            if not file_encodings:
                logger.warning("No face found in file: %s", file_path.name)
                continue

            encodings.append(file_encodings[0])
            names.append(file_path.stem)
        except Exception as error:
            logger.exception("Failed to process %s: %s", file_path.name, error)

    logger.info("Loaded %d student encodings.", len(names))
    return encodings, names
