"""Rendu du texte tapé au clavier, pour qu'il reste une lettre.

Un adulte qui écrit depuis son téléphone tape souvent au clavier. Sorti tel
quel en police d'imprimante, ça ressemble à un ticket de caisse ; d'où une
police manuscrite si le système en a une, et des caractères assez grands pour
un enfant de 7 ans qui apprend encore à lire.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .config import Config
from .fonts import load_font

# Polices manuscrites courantes sous Linux, par ordre de préférence.
_HANDWRITING = (
    "/usr/share/fonts/truetype/ecolier/ecolier_court.ttf",
    "/usr/share/fonts/truetype/caveat/Caveat-Regular.ttf",
    "/usr/share/fonts/truetype/tuffy/Tuffy.ttf",
)

MAX_LINES = 60  # au-delà, on coupe : personne ne veut un mètre de papier


def _font(config: Config, size: int) -> ImageFont.FreeTypeFont:
    candidates = [config.mail.handwriting_font, *_HANDWRITING]
    for path in candidates:
        if path and Path(path).exists():
            return ImageFont.truetype(path, size)
    return load_font(size)


def clean(text: str) -> list[str]:
    """Retire les citations et la signature : on n'imprime que le message."""
    lines: list[str] = []
    for raw in text.replace("\r\n", "\n").split("\n"):
        line = raw.rstrip()
        if line.strip() == "--":
            break  # début de signature
        if line.startswith(">"):
            continue  # citation de la réponse précédente
        lines.append(line)
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)
    return lines


def wrap(
    lines: list[str], font: ImageFont.FreeTypeFont, width: int, draw: ImageDraw.ImageDraw
) -> list[str]:
    """Découpe à la largeur du ticket, sans couper les mots."""
    wrapped: list[str] = []
    for line in lines:
        if not line.strip():
            wrapped.append("")
            continue
        current = ""
        for word in line.split():
            candidate = f"{current} {word}".strip()
            if current and draw.textlength(candidate, font=font) > width:
                wrapped.append(current)
                current = word
            else:
                current = candidate
        wrapped.append(current)
    return wrapped


def render(text: str, config: Config, x_height_mm: float = 3.5) -> np.ndarray:
    """Rend un texte en masque d'encre à la largeur du ticket."""
    width = config.printer.dots_per_line
    dots_per_mm = config.printer.dots_per_mm
    size = max(12, int(round(x_height_mm * dots_per_mm / 0.55)))
    font = _font(config, size)

    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    margin = int(round(2 * dots_per_mm))
    lines = wrap(clean(text), font, width - 2 * margin, probe)[:MAX_LINES]
    if not lines:
        raise ValueError("message vide")

    step = int(round(size * 1.45))
    height = margin * 2 + step * len(lines)
    canvas = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(canvas)
    for index, line in enumerate(lines):
        draw.text((margin, margin + index * step), line, font=font, fill=0)
    return np.asarray(canvas) < 128
