"""Chargement de police, avec repli si DejaVu n'est pas installé."""

from __future__ import annotations

from pathlib import Path

from PIL import ImageFont

_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans{bold}.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans{bold2}.ttf",
    "/Library/Fonts/Arial{bold3}.ttf",
)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for pattern in _CANDIDATES:
        path = pattern.format(
            bold="-Bold" if bold else "",
            bold2="-Bold" if bold else "-Regular",
            bold3=" Bold" if bold else "",
        )
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)
