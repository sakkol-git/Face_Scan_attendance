"""Startup bootstrap helpers.

Why this module exists: centralizes startup side effects (logging, sheets
connection, known-face loading) so entrypoints remain concise.
"""

from __future__ import annotations

import logging
from typing import Any

from attendance.sheets import open_live_logs_sheet
from recognition.encoding import load_known_faces
from utils.logging_config import configure_logging

logger = logging.getLogger(__name__)


def bootstrap_runtime(known_faces_dir: str = "known_faces") -> tuple[list[Any], list[str], Any]:
    """Initialize logging, persistence connection, and known-face dataset."""
    configure_logging()

    try:
        sheet = open_live_logs_sheet()
    except Exception as error:
        logger.exception("Failed to open attendance sheet: %s", error)
        sheet = None

    known_face_encodings, known_face_names = load_known_faces(known_faces_dir)
    return known_face_encodings, known_face_names, sheet
