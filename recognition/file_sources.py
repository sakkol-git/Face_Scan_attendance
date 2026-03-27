"""Filesystem helpers for known-face sources."""

from __future__ import annotations

from pathlib import Path

_IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def iter_face_files(folder: Path) -> list[Path]:
    """Return sorted face image files from a folder (top-level only)."""
    return sorted(
        file_path
        for file_path in folder.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in _IMAGE_EXTENSIONS
    )
