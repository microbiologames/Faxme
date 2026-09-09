"""Assemblage du ticket : en-tête + lettre, puis les différentes sorties.

L'en-tête est **dessiné dans le raster**, et non envoyé en texte ESC/POS.
Une seule voie de rendu, donc : ce que montre l'aperçu est exactement ce qui
sortira de l'imprimante, police comprise. C'est ce qui permet de juger le
rendu avant même d'avoir acheté l'imprimante.
"""

from __future__ import annotations

from datetime import datetime

import numpy as np
from PIL import Image, ImageDraw

from .config import Config
from .fonts import load_font

_JOURS = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
_MOIS = (
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
)


def french_date(when: datetime) -> str:
    return (
        f"{_JOURS[when.weekday()]} {when.day} {_MOIS[when.month - 1]} "
        f"· {when.hour}h{when.minute:02d}"
    )


def render(
    ink: np.ndarray,
    config: Config,
    *,
    sender: str | None = None,
    when: datetime | None = None,
) -> np.ndarray:
    """Ajoute l'en-tête au-dessus de la lettre. Renvoie le raster complet."""
    conf = config.ticket
    width = config.printer.dots_per_line
    dots_per_mm = config.printer.dots_per_mm

    if not conf.header:
        return ink

    sender = sender if sender is not None else conf.sender
    when = when or datetime.now()

    big = load_font(int(round(conf.header_height_mm * dots_per_mm)), bold=True)
    small = load_font(int(round(conf.header_height_mm * dots_per_mm * 0.5)))

    pad = int(round(1.5 * dots_per_mm))
    header_height = pad + big.size + int(round(0.8 * dots_per_mm)) + small.size + pad

    canvas = Image.new("L", (width, header_height), 255)
    draw = ImageDraw.Draw(canvas)
    draw.text((0, pad), f"DE {sender.upper()}", font=big, fill=0)
    draw.text((0, pad + big.size + int(round(0.8 * dots_per_mm))), french_date(when),
              font=small, fill=0)
    rule = int(round(0.4 * dots_per_mm))
    draw.rectangle([0, header_height - rule, width - 1, header_height - 1], fill=0)

    header = np.asarray(canvas) < 128
    gap = np.zeros((int(round(3 * dots_per_mm)), width), dtype=bool)
    body = _pad_to_width(ink, width)
    return np.vstack([header, gap, body])


def _pad_to_width(ink: np.ndarray, width: int) -> np.ndarray:
    """Centre la lettre si elle est plus étroite que le ticket."""
    if ink.shape[1] == width:
        return ink
    if ink.shape[1] > width:
        return ink[:, :width]
    padded = np.zeros((ink.shape[0], width), dtype=bool)
    left = (width - ink.shape[1]) // 2
    padded[:, left : left + ink.shape[1]] = ink
    return padded


# --- sorties -----------------------------------------------------------------


def to_image(ink: np.ndarray) -> Image.Image:
    """Le raster exact, tel qu'il part à l'imprimante (1 bit, noir = encre)."""
    return Image.fromarray(np.where(ink, 0, 255).astype(np.uint8)).convert("1")


# Le thermique ne sort pas un noir pur : un gris très foncé rend l'aperçu honnête.
_PAPER = (250, 248, 243)
_THERMAL = (32, 32, 32)


def paper_preview(ink: np.ndarray, config: Config, px_per_mm: float = 12.0) -> Image.Image:
    """Le ticket posé sur son rouleau de 80 mm, à l'échelle."""
    roll_mm = 80.0
    print_mm = config.printer.width_mm
    length_mm = ink.shape[0] / config.printer.dots_per_mm

    margin_mm = 6.0
    page_w = int(round((roll_mm + 2 * margin_mm) * px_per_mm))
    page_h = int(round((length_mm + 2 * margin_mm) * px_per_mm))
    page = Image.new("RGB", (page_w, page_h), (225, 223, 218))

    paper = Image.new("RGB", (int(round(roll_mm * px_per_mm)), int(round(length_mm * px_per_mm))), _PAPER)
    ticket = to_image(ink).convert("RGB").resize(
        (int(round(print_mm * px_per_mm)), paper.height), Image.Resampling.LANCZOS
    )
    ticket = _tint(ticket)
    paper.paste(ticket, ((paper.width - ticket.width) // 2, 0))
    page.paste(paper, (int(round(margin_mm * px_per_mm)), int(round(margin_mm * px_per_mm))))
    return page


def _tint(image: Image.Image) -> Image.Image:
    """Remplace le noir pur par le gris du thermique et le blanc par le papier."""
    array = np.asarray(image.convert("L"), dtype=np.float32)[:, :, None] / 255.0
    paper = np.array(_PAPER, dtype=np.float32)
    ink = np.array(_THERMAL, dtype=np.float32)
    blended = ink + (paper - ink) * array
    return Image.fromarray(blended.astype(np.uint8))


def true_size_page(ink: np.ndarray, config: Config, dpi: int = 300) -> Image.Image:
    """Une page A4 avec le ticket à sa taille physique réelle.

    À imprimer sur n'importe quelle imprimante ordinaire, **à 100 %**, pour
    juger la lisibilité en vrai avant d'acheter une thermique. La réglette
    de 50 mm imprimée à côté sert à vérifier que la mise à l'échelle du
    pilote d'impression ne t'a pas menti.
    """
    px_per_mm = dpi / 25.4
    page = Image.new("L", (int(round(210 * px_per_mm)), int(round(297 * px_per_mm))), 255)
    draw = ImageDraw.Draw(page)

    title = load_font(int(round(4.5 * px_per_mm)), bold=True)
    body = load_font(int(round(3.0 * px_per_mm)))
    draw.text((int(15 * px_per_mm), int(12 * px_per_mm)), "Faxme — ticket à taille réelle", font=title, fill=0)
    draw.text(
        (int(15 * px_per_mm), int(20 * px_per_mm)),
        "Imprimer à 100 %, sans « ajuster à la page ».\n"
        "La réglette ci-dessous doit mesurer exactement 50 mm.",
        font=body,
        fill=0,
    )

    # Réglette de contrôle : 50 mm, graduée tous les 10 mm.
    ruler_y = int(35 * px_per_mm)
    ruler_x = int(15 * px_per_mm)
    draw.line([ruler_x, ruler_y, ruler_x + int(50 * px_per_mm), ruler_y], fill=0, width=max(1, int(0.3 * px_per_mm)))
    for millimetre in range(0, 51, 10):
        x = ruler_x + int(millimetre * px_per_mm)
        draw.line([x, ruler_y - int(1.5 * px_per_mm), x, ruler_y + int(1.5 * px_per_mm)], fill=0, width=max(1, int(0.3 * px_per_mm)))
    draw.text((ruler_x + int(52 * px_per_mm), ruler_y - int(2 * px_per_mm)), "50 mm", font=body, fill=0)

    # Le ticket, à l'échelle exacte.
    target_w = int(round(config.printer.width_mm * px_per_mm))
    target_h = int(round(ink.shape[0] / config.printer.dots_per_mm * px_per_mm))
    ticket = to_image(ink).convert("L").resize((target_w, target_h), Image.Resampling.LANCZOS)
    top = int(45 * px_per_mm)
    if top + target_h > page.height - int(10 * px_per_mm):
        # Lettre plus longue qu'une page : on prévient plutôt que de rogner en silence.
        draw.text((ruler_x, top - int(4 * px_per_mm)),
                  "(ticket plus long que la page, tronqué)", font=body, fill=0)
        ticket = ticket.crop((0, 0, target_w, page.height - int(10 * px_per_mm) - top))
    page.paste(ticket, (ruler_x, top))
    draw.rectangle(
        [ruler_x - 2, top - 2, ruler_x + target_w + 1, top + ticket.height + 1],
        outline=200,
    )
    return page
