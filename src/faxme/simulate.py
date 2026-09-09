"""Fabrique une fausse photo de fiche manuscrite.

Sert à deux choses : développer le pipeline sans matériel, et vérifier en
test que la chaîne complète tient debout — y compris que la réglure orange
disparaît bien et que l'écriture noire survit.

Ce n'est pas un simulateur fidèle ; c'est un banc d'essai reproductible.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .cards import GUIDE
from .config import Config
from .fonts import load_font

DEFAULT_TEXT = [
    "Salut Léo !",
    "Aujourd'hui j'ai",
    "perdu une dent.",
    "Tu viens jouer",
    "mercredi ?",
    "Nino",
]


def handwriting(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    *,
    px_per_mm: float,
    origin_mm: tuple[float, float],
    x_height_mm: float,
    line_step_mm: float,
    rng: np.random.Generator,
) -> None:
    """Écrit des lignes avec un tremblement de main, caractère par caractère."""
    # DejaVu place la hauteur d'x autour de 0,55 em.
    size = int(round(x_height_mm * px_per_mm / 0.55))
    font = load_font(size)
    for index, line in enumerate(lines):
        x = origin_mm[0] * px_per_mm + rng.normal(0, 0.4 * px_per_mm)
        baseline = (origin_mm[1] + index * line_step_mm) * px_per_mm
        for character in line:
            jitter_y = rng.normal(0, 0.25 * px_per_mm)
            draw.text((x, baseline + jitter_y), character, font=font, fill=(20, 20, 30))
            x += draw.textlength(character, font=font) * rng.uniform(0.95, 1.08)


def fake_photo(
    config: Config,
    *,
    text: list[str] | None = None,
    x_height_mm: float = 3.0,
    pen_mm: float = 0.7,
    angle_deg: float = 1.8,
    seed: int = 7,
    px_per_mm: float = 16.0,
) -> Image.Image:
    """Rend une photo plausible : fiche réglée, écriture, éclairage inégal, flou."""
    rng = np.random.default_rng(seed)
    card_config = config.card
    width = int(round(card_config.width_mm * px_per_mm))
    height = int(round(card_config.height_mm * px_per_mm))

    card = Image.new("RGB", (width, height), (252, 251, 248))
    draw = ImageDraw.Draw(card)

    # Réglure orange, comme sur les vraies fiches.
    margin = 8.0
    y = margin + 22.0
    while y <= card_config.height_mm - margin - 2:
        draw.line([int(margin * px_per_mm), int(y * px_per_mm),
                   int((card_config.width_mm - margin) * px_per_mm), int(y * px_per_mm)],
                  fill=GUIDE, width=max(1, int(0.25 * px_per_mm)))
        y += card_config.ruling_mm
    draw.rectangle(
        [int(margin * px_per_mm), int(margin * px_per_mm),
         int((card_config.width_mm - margin) * px_per_mm),
         int((card_config.height_mm - margin) * px_per_mm)],
        outline=GUIDE, width=max(1, int(0.25 * px_per_mm)),
    )

    handwriting(
        draw,
        DEFAULT_TEXT if text is None else text,
        px_per_mm=px_per_mm,
        origin_mm=(margin + 4, margin + 18),
        x_height_mm=x_height_mm,
        line_step_mm=card_config.ruling_mm,
        rng=rng,
    )

    # Un feutre dépose un trait plus épais que le rendu d'une police. On
    # épaissit jusqu'à atteindre la largeur visée, mesurée avec l'outil du
    # pipeline lui-même plutôt qu'estimée à la louche.
    card = _thicken_to(card, target_px=pen_mm * px_per_mm)

    # La fiche posée de travers sur le fond, puis l'éclairage et le flou.
    scene = Image.new(
        "RGB",
        (int(width * (1 + SCENE_MARGIN[0])), int(height * (1 + SCENE_MARGIN[1]))),
        (108, 96, 84),
    )
    rotated = card.rotate(angle_deg, resample=Image.Resampling.BICUBIC,
                          expand=True, fillcolor=(108, 96, 84))
    scene.paste(rotated, ((scene.width - rotated.width) // 2,
                          (scene.height - rotated.height) // 2))
    scene = _uneven_light(scene, rng)
    scene = scene.filter(ImageFilter.GaussianBlur(radius=0.6))
    return _noise(scene, rng, sigma=3.0)


def _thicken_to(card: Image.Image, target_px: float) -> Image.Image:
    """Épaissit le trait par passes de 1 pixel jusqu'à la largeur visée."""
    from .imaging import stroke_thickness

    best, best_error = card, abs(stroke_thickness(np.asarray(card.convert("L")) < 128) - target_px)
    for _ in range(12):
        card = card.filter(ImageFilter.MinFilter(size=3))
        ink = np.asarray(card.convert("L")) < 128
        if not ink.any():
            break
        error = abs(stroke_thickness(ink) - target_px)
        if error < best_error:
            best, best_error = card, error
        else:
            break
    return best


def _uneven_light(image: Image.Image, rng: np.random.Generator) -> Image.Image:
    """Dégradé diagonal marqué : c'est exactement ce que la normalisation doit gommer."""
    array = np.asarray(image, dtype=np.float32)
    h, w = array.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    gain = 1.18 - 0.45 * (xx / w) - 0.30 * (yy / h)
    return Image.fromarray(np.clip(array * gain[:, :, None], 0, 255).astype(np.uint8))


def _noise(image: Image.Image, rng: np.random.Generator, sigma: float) -> Image.Image:
    array = np.asarray(image, dtype=np.float32)
    return Image.fromarray(
        np.clip(array + rng.normal(0, sigma, array.shape), 0, 255).astype(np.uint8)
    )


# La scène est fabriquée avec ces marges autour de la fiche ; le recadrage
# "calibré" du pipeline en découle directement.
SCENE_MARGIN = (0.25, 0.18)


def crop_for(config: Config, angle_deg: float = 1.8) -> tuple[float, float, float, float]:
    """Le recadrage fixe correspondant à la scène simulée.

    L'équivalent, pour le banc d'essai, de la calibration faite une fois à
    l'installation. Comme en vrai, on calibre **à l'intérieur** du papier :
    le rectangle est rentré de ce que la fiche déborde en tournant, plus un
    millimètre de sécurité. Viser le bord exact revient à cadrer la table.
    """
    fx = 1.0 / (1.0 + SCENE_MARGIN[0])
    fy = 1.0 / (1.0 + SCENE_MARGIN[1])
    overhang = abs(np.sin(np.radians(angle_deg)))
    inset_x = (overhang * config.card.height_mm + 1.0) / config.card.width_mm * fx
    inset_y = (overhang * config.card.width_mm + 1.0) / config.card.height_mm * fy
    return (
        (1 - fx) / 2 + inset_x,
        (1 - fy) / 2 + inset_y,
        (1 + fx) / 2 - inset_x,
        (1 + fy) / 2 - inset_y,
    )
