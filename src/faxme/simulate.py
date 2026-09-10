"""Fabrique une fausse photo de fiche manuscrite.

Sert à deux choses : développer le pipeline sans matériel, et vérifier en
test que la chaîne complète tient debout — y compris que la réglure orange
disparaît bien et que l'écriture noire survit.

Ce n'est pas un simulateur fidèle ; c'est un banc d'essai reproductible.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .cards import BAND, BAND_MM, GUIDE
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

    # Bande de reconnaissance et réglure orange, comme sur les vraies fiches.
    margin = 8.0
    draw.rectangle([0, 0, width, int(BAND_MM * px_per_mm)], fill=BAND)
    y = BAND_MM + 30.0
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
        origin_mm=(margin + 4, BAND_MM + 22),
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


def fake_drawing(
    config: Config,
    *,
    seed: int = 3,
    px_per_mm: float = 16.0,
    angle_deg: float = 1.2,
) -> Image.Image:
    """Un dessin d'enfant sur une feuille blanche : traits épais et aplats coloriés.

    Sert à vérifier ce qu'une lettre ne teste pas : la bascule automatique en
    tramage, et le fait qu'aucune couleur ne disparaisse faute de bande orange.
    """
    rng = np.random.default_rng(seed)
    width = int(round(config.card.width_mm * px_per_mm))
    height = int(round(config.card.height_mm * px_per_mm))
    sheet = Image.new("RGB", (width, height), (253, 252, 250))
    draw = ImageDraw.Draw(sheet)
    mm = px_per_mm
    crayon = max(2, int(round(1.2 * mm)))

    # Un ciel colorié : c'est cet aplat qui doit déclencher le tramage.
    for y in range(int(8 * mm), int(38 * mm), max(2, int(0.9 * mm))):
        draw.line([int(6 * mm), y + rng.integers(-2, 3), int(99 * mm), y],
                  fill=(126, 168, 214), width=max(1, int(0.7 * mm)))

    # Un soleil, colorié lui aussi.
    draw.ellipse([int(72 * mm), int(10 * mm), int(95 * mm), int(33 * mm)],
                 fill=(248, 214, 96), outline=(226, 160, 40), width=crayon)

    # La maison : murs, toit plein, porte, fenêtre.
    draw.rectangle([int(24 * mm), int(60 * mm), int(72 * mm), int(104 * mm)],
                   outline=(60, 55, 50), width=crayon)
    draw.polygon([(int(18 * mm), int(60 * mm)), (int(48 * mm), int(38 * mm)),
                  (int(78 * mm), int(60 * mm))], fill=(198, 92, 74), outline=(90, 40, 32))
    draw.rectangle([int(40 * mm), int(80 * mm), int(56 * mm), int(104 * mm)],
                   outline=(60, 55, 50), width=crayon)
    draw.rectangle([int(28 * mm), int(66 * mm), int(38 * mm), int(76 * mm)],
                   outline=(60, 55, 50), width=crayon)

    # De l'herbe hachurée et un bonhomme au trait.
    for x in range(int(6 * mm), int(99 * mm), max(2, int(2.2 * mm))):
        draw.line([x, int(112 * mm), x + rng.integers(-3, 4), int(104 * mm)],
                  fill=(104, 158, 92), width=max(1, int(0.8 * mm)))
    draw.ellipse([int(82 * mm), int(86 * mm), int(94 * mm), int(98 * mm)],
                 outline=(60, 55, 50), width=crayon)
    draw.line([int(88 * mm), int(98 * mm), int(88 * mm), int(112 * mm)],
              fill=(60, 55, 50), width=crayon)

    handwriting(draw, ["ma maison"], px_per_mm=px_per_mm,
                origin_mm=(14, 128), x_height_mm=4.5,
                line_step_mm=8.0, rng=rng)

    scene = Image.new(
        "RGB",
        (int(width * (1 + SCENE_MARGIN[0])), int(height * (1 + SCENE_MARGIN[1]))),
        (108, 96, 84),
    )
    rotated = sheet.rotate(angle_deg, resample=Image.Resampling.BICUBIC,
                           expand=True, fillcolor=(108, 96, 84))
    scene.paste(rotated, ((scene.width - rotated.width) // 2,
                          (scene.height - rotated.height) // 2))
    scene = _uneven_light(scene, rng)
    return _noise(scene.filter(ImageFilter.GaussianBlur(radius=0.6)), rng, sigma=3.0)


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
