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
    *,
    threshold: float = 0.6,
) -> str:
    """Return best-matched known name for a face encoding, else Unknown."""
    name, _ = resolve_match(
        face_encoding,
        known_face_encodings,
        known_face_names,
        threshold=threshold,
    )
    return name


def resolve_match(
    face_encoding: Any,
    known_face_encodings: list[Any],
    known_face_names: list[str],
    *,
    threshold: float = 0.6,
) -> tuple[str, float]:
    """Return best-matched name and confidence, else ("Unknown", 0.0)."""
    if not known_face_encodings or not known_face_names:
        return "Unknown", 0.0

    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
    best_match_index = min(range(len(face_distances)), key=face_distances.__getitem__)
    best_distance = float(face_distances[best_match_index])
    if best_distance <= threshold:
        confidence = max(0.0, min(1.0, 1.0 - (best_distance / threshold)))
        return known_face_names[best_match_index], confidence
    return "Unknown", 0.0
