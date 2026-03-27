"""Face matching helpers for webcam runtime."""

from __future__ import annotations

from typing import Any

import face_recognition


def normalize_known_faces(
    known_face_encodings: list[Any],
    known_face_names: list[str],
) -> tuple[list[Any], list[str]]:
    """Return aligned encoding/name lists trimmed to same length."""
    if len(known_face_encodings) == len(known_face_names):
        return known_face_encodings, known_face_names

    usable_count = min(len(known_face_encodings), len(known_face_names))
    return known_face_encodings[:usable_count], known_face_names[:usable_count]


def resolve_name(
    face_encoding: Any,
    known_face_encodings: list[Any],
    known_face_names: list[str],
) -> str:
    """Return best-matched known name for a face encoding, else Unknown."""
    if not known_face_encodings or not known_face_names:
        return "Unknown"

    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
    if True not in matches:
        return "Unknown"

    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
    best_match_index = min(range(len(face_distances)), key=face_distances.__getitem__)
    if matches[best_match_index]:
        return known_face_names[best_match_index]
    return "Unknown"
