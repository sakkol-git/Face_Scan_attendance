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


def iter_face_dataset(root: Path) -> list[tuple[str, Path]]:
    """Return (label, file_path) tuples for nested person folders."""
    dataset: list[tuple[str, Path]] = []
    if not root.exists() or not root.is_dir():
        return dataset

    for person_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        label = person_dir.name
        for file_path in sorted(person_dir.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in _IMAGE_EXTENSIONS:
                dataset.append((label, file_path))

    return dataset
