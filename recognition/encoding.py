"""Known face loading and preprocessing utilities."""

from __future__ import annotations

import hashlib
import logging
import pickle
from pathlib import Path
from typing import Any

import face_recognition

from recognition.file_sources import iter_face_dataset

logger = logging.getLogger(__name__)

CACHE_FILENAME = "encodings_cache.pkl"
CACHE_VERSION = 1


def load_known_faces(known_faces_dir: str | Path = "known_faces") -> tuple[list[Any], list[str]]:
    """Load face encodings and names from a directory of person subfolders.

    Args:
        known_faces_dir: Root folder that stores known-face subfolders.

    Returns:
        A tuple containing the list of face encodings and corresponding names.
    """
    folder = Path(known_faces_dir)
    encodings: list[Any] = []
    names: list[str] = []

    if not folder.exists() or not folder.is_dir():
        logger.warning("Known faces directory not found: %s", folder)
        return encodings, names

    cache_path = folder / CACHE_FILENAME
    try:
        dataset_hash = _build_dataset_hash(folder)
    except Exception as error:
        logger.warning("Failed to compute dataset hash: %s", error)
        dataset_hash = None

    if dataset_hash:
        cached = _load_cache(cache_path, dataset_hash)
        if cached is not None:
            return cached

    try:
        dataset = iter_face_dataset(folder)
    except Exception as error:
        logger.exception("Failed to list known face files in %s: %s", folder, error)
        return encodings, names

    for label, file_path in dataset:
        try:
            image = face_recognition.load_image_file(str(file_path))
            file_encodings = face_recognition.face_encodings(image)
            if not file_encodings:
                logger.warning("No face found in file: %s", file_path.name)
                continue
            if len(file_encodings) > 1:
                logger.warning("Multiple faces found in %s; using the first encoding.", file_path.name)

            encodings.append(file_encodings[0])
            names.append(label)
        except Exception as error:
            logger.exception("Failed to process %s: %s", file_path.name, error)

    logger.info("Loaded %d face encodings across %d labels.", len(encodings), len(set(names)))
    if dataset_hash:
        _save_cache(cache_path, dataset_hash, encodings, names)
    return encodings, names


def _build_dataset_hash(root: Path) -> str:
    """Return a hash representing the current dataset contents."""
    hasher = hashlib.sha256()
    for label, file_path in iter_face_dataset(root):
        try:
            stat = file_path.stat()
        except FileNotFoundError:
            continue
        relative_path = file_path.relative_to(root).as_posix()
        hasher.update(label.encode("utf-8"))
        hasher.update(relative_path.encode("utf-8"))
        hasher.update(str(stat.st_mtime_ns).encode("utf-8"))
        hasher.update(str(stat.st_size).encode("utf-8"))

    return hasher.hexdigest()


def _load_cache(cache_path: Path, dataset_hash: str) -> tuple[list[Any], list[str]] | None:
    if not cache_path.exists():
        return None
    try:
        with cache_path.open("rb") as handle:
            payload = pickle.load(handle)
    except Exception as error:
        logger.warning("Failed to load encoding cache: %s", error)
        return None

    if not isinstance(payload, dict):
        return None
    if payload.get("version") != CACHE_VERSION:
        return None
    if payload.get("dataset_hash") != dataset_hash:
        return None

    encodings = payload.get("encodings", [])
    names = payload.get("names", [])
    if not isinstance(encodings, list) or not isinstance(names, list):
        return None

    logger.info("Loaded %d cached face encodings.", len(encodings))
    return encodings, names


def _save_cache(cache_path: Path, dataset_hash: str, encodings: list[Any], names: list[str]) -> None:
    payload = {
        "version": CACHE_VERSION,
        "dataset_hash": dataset_hash,
        "encodings": encodings,
        "names": names,
    }
    try:
        with cache_path.open("wb") as handle:
            pickle.dump(payload, handle)
    except Exception as error:
        logger.warning("Failed to save encoding cache: %s", error)
