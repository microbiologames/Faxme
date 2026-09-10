"""Enchaînement des étapes : une photo de fiche entre, un masque d'encre sort.

L'ordre est celui de CONCEPT.md §4.2, avec une nuance : on redresse en
niveaux de gris puis on rebinarise, plutôt que de faire tourner le masque.
Faire tourner un masque binaire crée des escaliers sur les traits fins ;
repasser par le gris les évite.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np
from PIL import Image

from . import imaging
from .config import Config
from .imaging import EmptyCard


@dataclass
class Stage:
    """Une étape du traitement, gardée pour la planche de contrôle."""

    name: str
    label: str
    image: Image.Image


@dataclass
class Result:
    ink: np.ndarray  # masque booléen à la largeur du ticket, True = encre
    stats: dict = field(default_factory=dict)
    stages: list[Stage] = field(default_factory=list)


def _as_image(array: np.ndarray) -> Image.Image:
    if array.dtype == bool:
        # L'encre en noir sur fond blanc, comme à l'impression.
        return Image.fromarray(np.where(array, 0, 255).astype(np.uint8))
    return Image.fromarray((np.clip(array, 0, 1) * 255).astype(np.uint8))


def process(photo: Image.Image, config: Config, *, keep_stages: bool = False) -> Result:
    """Traite une photo de fiche. Lève ``EmptyCard`` si la fiche est vide."""
    pipe = config.pipeline
    stages: list[Stage] = []

    def keep(name: str, label: str, data) -> None:
        if keep_stages:
            stages.append(
                Stage(name, label, data if isinstance(data, Image.Image) else _as_image(data))
            )

    keep("photo", "1. photo brute", photo)

    card = imaging.orient_and_crop(photo, config)
    keep("cadree", "2. recadrage fixe", card)

    channel = config.capture.gray_channel
    if channel == "auto":
        channel = "red" if imaging.has_guide_band(card, config) else "luma"
    gray = imaging.to_working_gray(card, replace(config, capture=replace(config.capture, gray_channel=channel)))
    keep("gris", f"3. niveaux de gris ({channel})", gray)

    px_per_mm = config.working_px_per_mm
    flat = imaging.normalize_illumination(gray, pipe.illumination_mm * px_per_mm)
    keep("eclairage", "4. éclairage normalisé", flat)

    mid_tone = imaging.mid_tone_ratio(flat)
    mode = pipe.render_mode
    if mode == "auto":
        mode = "dessin" if mid_tone > pipe.mid_tone_ratio else "trait"
    elif mode not in ("trait", "dessin"):
        raise ValueError(
            f"pipeline.render_mode doit valoir 'auto', 'trait' ou 'dessin', pas {mode!r}"
        )

    border_px = int(round(pipe.border_mm * px_per_mm))
    window = max(3, int(round(pipe.sauvola_window_mm * px_per_mm)) | 1)

    # Un masque d'encre grossier, qui sert à décider si la fiche est vide et où
    # se trouve ce qui a été écrit ou dessiné. En mode trait, c'est déjà le
    # rendu final ; en mode dessin, ce n'est qu'un repère de cadrage.
    ink = imaging.clear_border(imaging.sauvola(flat, window, pipe.sauvola_k), border_px)
    keep("binarise", f"5. binarisation ({mode})", ink)

    ink_ratio = float(ink.mean())
    if ink_ratio < pipe.min_ink_ratio:
        raise EmptyCard(
            f"fiche vide ou illisible : {ink_ratio:.4%} d'encre "
            f"(seuil {pipe.min_ink_ratio:.4%})"
        )

    angle = 0.0
    if mode == "trait":
        # Le redressement s'appuie sur l'alternance lignes écrites / interlignes.
        # Un dessin n'en a pas : le critère n'y voudrait rien dire, et la fiche
        # est de toute façon posée droite contre les butées.
        angle = imaging.estimate_skew(ink, pipe.deskew_max_deg)
        if abs(angle) >= 0.05:
            flat = imaging.rotate_gray(flat, angle)
            rotated_border = border_px + int(
                round(abs(np.sin(np.radians(angle))) * max(flat.shape))
            )
            ink = imaging.clear_border(
                imaging.sauvola(flat, window, pipe.sauvola_k), rotated_border
            )
        keep("redresse", f"6. redressé ({angle:+.1f}°)", ink)
    else:
        flat = imaging.clear_border_gray(flat, border_px)
        keep("redresse", "6. bord effacé", flat)

    top, bottom, left, right = _bounds(ink, config, pipe.fit)
    flat = flat[top:bottom, left:right]
    ink = ink[top:bottom, left:right]
    keep("cadre", f"7. cadrage ({pipe.fit})", ink if mode == "trait" else flat)

    width = config.printer.dots_per_line
    if mode == "trait":
        ink = imaging.downsample_ink(ink, width)
        ink = imaging.thicken_thin_strokes(ink, pipe.min_stroke_dots)
    else:
        # Le tramage se fait **à la résolution finale** : tramer avant de
        # réduire détruirait la trame en la moyennant.
        ink = imaging.dither(
            imaging.resize_gray(flat, width), pipe.dither_gamma, pipe.dither_solid_below
        )
    keep("ticket", f"8. à la largeur du ticket ({mode})", ink)

    dots_per_mm = config.printer.dots_per_mm
    thickness = imaging.stroke_thickness(ink)
    return Result(
        ink=ink,
        stats={
            "mode": mode,
            "channel": channel,
            "mid_tone": round(mid_tone, 4),
            "angle_deg": round(angle, 2),
            "ink_ratio": round(float(ink.mean()), 5),
            "ink_ratio_source": round(ink_ratio, 5),
            "stroke_dots": thickness,
            "stroke_mm": round(thickness / dots_per_mm, 2),
            "length_mm": round(ink.shape[0] / dots_per_mm, 1),
            "width_mm": round(ink.shape[1] / dots_per_mm, 1),
        },
        stages=stages,
    )


def _bounds(ink: np.ndarray, config: Config, fit: str) -> tuple[int, int, int, int]:
    """Le rectangle à garder, selon le mode de cadrage. Renvoie (haut, bas, gauche, droite)."""
    if fit == "card":
        return 0, ink.shape[0], 0, ink.shape[1]
    if fit not in ("trim", "ink"):
        raise ValueError(
            f"pipeline.fit doit valoir 'trim', 'card' ou 'ink', pas {fit!r}"
        )
    margin_px = int(round(config.pipeline.margin_mm * config.working_px_per_mm))
    left, top, right, bottom = imaging.ink_bounds(ink, margin_px)
    if fit == "trim":
        # Hauteur seulement : l'échelle horizontale reste celle de la fiche,
        # donc une minuscule fait toujours la même taille sur le ticket.
        left, right = 0, ink.shape[1]
    return top, bottom, left, right


def contact_sheet(stages: list[Stage], width: int = 1500) -> Image.Image:
    """Assemble les étapes côte à côte, pour diagnostiquer d'un coup d'œil."""
    from PIL import ImageDraw, ImageFont

    from .fonts import load_font

    if not stages:
        raise ValueError("aucune étape à afficher (keep_stages=False ?)")

    columns = min(4, len(stages))
    rows = (len(stages) + columns - 1) // columns
    cell_w = width // columns
    cell_h = int(cell_w * 1.35)
    label_h = 28
    font = load_font(18)

    sheet = Image.new("RGB", (cell_w * columns, (cell_h + label_h) * rows), "white")
    draw = ImageDraw.Draw(sheet)
    for index, stage in enumerate(stages):
        row, column = divmod(index, columns)
        x0, y0 = column * cell_w, row * (cell_h + label_h)
        thumb = stage.image.convert("RGB").copy()
        thumb.thumbnail((cell_w - 16, cell_h - 16), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x0 + (cell_w - thumb.width) // 2, y0 + label_h + 8))
        draw.text((x0 + 8, y0 + 6), stage.label, fill="black", font=font)
        draw.rectangle([x0, y0, x0 + cell_w - 1, y0 + cell_h + label_h - 1], outline="#cccccc")
    return sheet
