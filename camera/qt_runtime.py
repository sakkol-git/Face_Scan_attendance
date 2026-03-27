"""Runtime helpers for OpenCV Qt font configuration.

These helpers isolate environment and filesystem side effects required by some
Linux OpenCV/Qt builds so camera modules can stay focused on frame processing.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from types import ModuleType

_FONT_DIR_CANDIDATES: tuple[Path, ...] = (
    Path("/usr/share/fonts/truetype/dejavu"),
    Path("/usr/share/fonts/dejavu"),
    Path("/usr/share/fonts/truetype/freefont"),
)


def configure_qt_font_dir() -> None:
    """Set ``QT_QPA_FONTDIR`` to a valid system path when not already set."""
    if os.environ.get("QT_QPA_FONTDIR"):
        return

    for font_dir in _FONT_DIR_CANDIDATES:
        if font_dir.is_dir():
            os.environ["QT_QPA_FONTDIR"] = str(font_dir)
            return


def ensure_opencv_qt_fonts(cv2_module: ModuleType) -> None:
    """Populate OpenCV Qt font folder from system fonts if it is missing/empty."""
    cv2_dir = Path(cv2_module.__file__).resolve().parent
    qt_fonts_dir = cv2_dir / "qt" / "fonts"

    if qt_fonts_dir.is_dir() and any(qt_fonts_dir.iterdir()):
        return

    for source_dir in _FONT_DIR_CANDIDATES:
        if not source_dir.is_dir():
            continue

        fonts = sorted(source_dir.glob("*.ttf"))
        if not fonts:
            continue

        qt_fonts_dir.mkdir(parents=True, exist_ok=True)
        for source_font in fonts[:8]:
            target_font = qt_fonts_dir / source_font.name
            if target_font.exists():
                continue

            try:
                os.symlink(source_font, target_font)
            except OSError:
                shutil.copy2(source_font, target_font)

        os.environ.setdefault("QT_QPA_FONTDIR", str(source_dir))
        return
