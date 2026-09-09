"""De la photo de fiche au masque d'encre.

Volontairement **sans OpenCV** : numpy et Pillow suffisent pour tout ce qui
suit, s'installent en quelques secondes sur un Raspberry Pi et pèsent une
fraction de ``opencv-python``.

Le pipeline complet est décrit dans CONCEPT.md §4.2. Chaque fonction ici fait
une étape et une seule, pour pouvoir être regardée isolément dans la planche
de contrôle produite par ``faxme rendre --etapes``.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter

from .config import Config


class EmptyCard(Exception):
    """La fente est vide, ou la fiche n'a rien dessus."""


# --- géométrie ---------------------------------------------------------------


def orient_and_crop(photo: Image.Image, config: Config) -> Image.Image:
    """Applique la rotation puis le recadrage fixe calibrés à l'installation."""
    capture = config.capture
    if capture.rotate_quarters % 4:
        photo = photo.rotate(-90 * (capture.rotate_quarters % 4), expand=True)
    left, top, right, bottom = capture.crop
    if not (0.0 <= left < right <= 1.0 and 0.0 <= top < bottom <= 1.0):
        raise ValueError(f"recadrage invalide : {capture.crop}")
    w, h = photo.size
    box = (round(left * w), round(top * h), round(right * w), round(bottom * h))
    return photo.crop(box)


def to_working_gray(card: Image.Image, config: Config) -> np.ndarray:
    """Ramène la fiche à la résolution de travail, en niveaux de gris 0..1.

    Le sous-échantillonnage précoce est ce qui rend le traitement rapide sur
    un Pi : on n'a jamais besoin de plus de trois fois la résolution finale.
    """
    channel = config.capture.gray_channel
    if channel == "red":
        card = card.convert("RGB").getchannel("R")
    elif channel == "luma":
        card = card.convert("L")
    else:
        raise ValueError(
            f"capture.gray_channel doit valoir 'red' ou 'luma', pas {channel!r}"
        )
    width = config.working_width
    height = max(1, round(width * card.size[1] / card.size[0]))
    card = card.resize((width, height), Image.Resampling.LANCZOS)
    return np.asarray(card, dtype=np.float32) / 255.0


# --- éclairage et binarisation ----------------------------------------------


def normalize_illumination(gray: np.ndarray, radius_px: float) -> np.ndarray:
    """Divise l'image par une version très floue d'elle-même.

    Le flou approxime l'éclairage (dégradé de la LED, ombre de la potence,
    lumière du jour par la fenêtre) ; la division le supprime et ne laisse
    que ce qui varie vite, c'est-à-dire l'encre.
    """
    if radius_px < 1:
        return gray
    background = Image.fromarray((gray * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(radius=radius_px)
    )
    background = np.asarray(background, dtype=np.float32) / 255.0
    # Le plancher évite une division par ~0 dans les zones très sombres.
    return np.clip(gray / np.maximum(background, 0.05), 0.0, 1.0)


def _box_stats(a: np.ndarray, radius: int) -> tuple[np.ndarray, np.ndarray]:
    """Moyenne et écart-type locaux sur une fenêtre carrée, par image intégrale.

    En float64 volontairement : une image intégrale en float32 perd trop de
    précision sur plusieurs millions de pixels et fait apparaître des bandes.
    """
    a64 = a.astype(np.float64)
    integral = np.pad(a64.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    integral_sq = np.pad((a64 * a64).cumsum(0).cumsum(1), ((1, 0), (1, 0)))

    h, w = a.shape
    y0 = np.clip(np.arange(h) - radius, 0, h)
    y1 = np.clip(np.arange(h) + radius + 1, 0, h)
    x0 = np.clip(np.arange(w) - radius, 0, w)
    x1 = np.clip(np.arange(w) + radius + 1, 0, w)

    def window_sum(table: np.ndarray) -> np.ndarray:
        return (
            table[np.ix_(y1, x1)]
            - table[np.ix_(y0, x1)]
            - table[np.ix_(y1, x0)]
            + table[np.ix_(y0, x0)]
        )

    count = ((y1 - y0)[:, None] * (x1 - x0)[None, :]).astype(np.float64)
    mean = window_sum(integral) / count
    variance = np.maximum(window_sum(integral_sq) / count - mean * mean, 0.0)
    return mean.astype(np.float32), np.sqrt(variance).astype(np.float32)


def sauvola(gray: np.ndarray, window_px: int, k: float) -> np.ndarray:
    """Binarisation adaptative de Sauvola. Renvoie un masque booléen (True = encre).

    Adaptative parce qu'un seuil global échoue dès qu'un coin de la fiche est
    plus sombre que l'autre — ce qui est le cas permanent sous une potence.

    Sur une zone vierge, on pourrait craindre que le seuil se rabatte sur la
    moyenne locale et que le bruit du capteur passe pour de l'encre. Le terme
    en ``k`` l'empêche : quand l'écart-type local est quasi nul, il abaisse le
    seuil à ``mean * (1 - k)``, très en dessous du grain. Vérifié jusqu'à un
    bruit de sigma 10 et sur du papier sombre (tests/test_pipeline.py) ; c'est
    pourquoi il n'y a pas de garde-fou supplémentaire ici.
    """
    radius = max(1, window_px // 2)
    mean, std = _box_stats(gray, radius)
    # R = dynamique maximale de l'écart-type ; 0.5 pour des valeurs dans 0..1.
    threshold = mean * (1.0 + k * (std / 0.5 - 1.0))
    return gray < threshold


def clear_border(ink: np.ndarray, border_px: int) -> np.ndarray:
    """Efface une bande sur le pourtour, où seule traîne la découpe du papier."""
    if border_px <= 0:
        return ink
    cleaned = ink.copy()
    cleaned[:border_px, :] = False
    cleaned[-border_px:, :] = False
    cleaned[:, :border_px] = False
    cleaned[:, -border_px:] = False
    return cleaned


# --- redressement ------------------------------------------------------------


def estimate_skew(ink: np.ndarray, max_deg: float, coarse_step: float = 0.5) -> float:
    """Estime l'inclinaison de l'écriture par profil de projection.

    Quand les lignes de texte sont horizontales, la somme d'encre par ligne
    de pixels alterne fortement entre lignes écrites et interlignes : sa
    variance est maximale. On cherche l'angle qui maximise cette variance.
    """
    if max_deg <= 0 or not ink.any():
        return 0.0

    # Une petite version suffit largement et rend la recherche instantanée.
    small = Image.fromarray((ink * 255).astype(np.uint8))
    scale = 500 / max(small.size)
    if scale < 1:
        small = small.resize(
            (max(1, int(small.size[0] * scale)), max(1, int(small.size[1] * scale))),
            Image.Resampling.BILINEAR,
        )

    def score(angle: float) -> float:
        rotated = small.rotate(angle, resample=Image.Resampling.BILINEAR, fillcolor=0)
        profile = np.asarray(rotated, dtype=np.float32).sum(axis=1)
        return float(np.var(profile))

    candidates = np.arange(-max_deg, max_deg + 1e-9, coarse_step)
    best = max(candidates, key=score)
    fine = np.arange(best - coarse_step, best + coarse_step + 1e-9, coarse_step / 5)
    return float(max(fine, key=score))


def rotate_gray(gray: np.ndarray, angle_deg: float) -> np.ndarray:
    """Redresse l'image en niveaux de gris (et non le masque : on rebinarise après)."""
    if abs(angle_deg) < 0.05:
        return gray
    image = Image.fromarray((gray * 255).astype(np.uint8))
    rotated = image.rotate(
        angle_deg, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=255
    )
    return np.asarray(rotated, dtype=np.float32) / 255.0


# --- cadrage et mise à l'échelle finale --------------------------------------


def ink_bounds(ink: np.ndarray, margin_px: int) -> tuple[int, int, int, int]:
    """Boîte englobante de l'encre, élargie d'une marge, bornée à l'image."""
    rows = np.flatnonzero(ink.any(axis=1))
    cols = np.flatnonzero(ink.any(axis=0))
    if rows.size == 0 or cols.size == 0:
        raise EmptyCard("aucune encre détectée")
    top, bottom = int(rows[0]), int(rows[-1]) + 1
    left, right = int(cols[0]), int(cols[-1]) + 1
    h, w = ink.shape
    return (
        max(0, left - margin_px),
        max(0, top - margin_px),
        min(w, right + margin_px),
        min(h, bottom + margin_px),
    )


def downsample_ink(ink: np.ndarray, target_width: int, coverage: float = 0.35) -> np.ndarray:
    """Réduit le masque d'encre à la largeur du ticket.

    On moyenne la couverture d'encre sur chaque point de destination puis on
    seuille bas (35 %) : un trait fin qui ne couvrirait qu'un tiers du point
    final survit, là où un simple échantillonnage l'aurait effacé.
    """
    height, width = ink.shape
    if width == target_width:
        return ink
    target_height = max(1, round(height * target_width / width))
    grey = Image.fromarray((ink * 255).astype(np.uint8)).resize(
        (target_width, target_height), Image.Resampling.BOX
    )
    return np.asarray(grey, dtype=np.float32) / 255.0 >= coverage


def dilate(ink: np.ndarray, dots: int) -> np.ndarray:
    """Épaissit le trait de ``dots`` points."""
    if dots <= 0:
        return ink
    image = Image.fromarray((ink * 255).astype(np.uint8))
    thicker = image.filter(ImageFilter.MaxFilter(size=2 * dots + 1))
    return np.asarray(thicker) > 127


def thicken_thin_strokes(ink: np.ndarray, min_dots: int, max_passes: int = 2) -> np.ndarray:
    """Épaissit **seulement** si le trait est trop fin pour l'impression.

    Un trait de feutre large n'a pas besoin d'aide, et le dilater ferait se
    boucher les boucles. Un trait de stylo bille fin, lui, se casse à
    l'impression s'il ne fait qu'un ou deux points : on lui ajoute ce qu'il
    faut, et rien de plus.
    """
    for _ in range(max_passes):
        if not ink.any() or stroke_thickness(ink) >= min_dots:
            break
        ink = dilate(ink, 1)
    return ink


# --- mesures -----------------------------------------------------------------


def _run_lengths(ink: np.ndarray) -> np.ndarray:
    """Longueurs des segments d'encre continus sur chaque ligne."""
    padded = np.pad(ink, ((0, 0), (1, 1)))
    diff = np.diff(padded.astype(np.int8), axis=1)
    starts = np.argwhere(diff == 1)
    ends = np.argwhere(diff == -1)
    if len(starts) != len(ends) or len(starts) == 0:
        return np.empty(0, dtype=np.int64)
    return ends[:, 1] - starts[:, 1]


def stroke_thickness(ink: np.ndarray) -> float:
    """Épaisseur médiane du trait, en points.

    C'est la mesure qui compte : ce qui casse à l'impression thermique n'est
    pas la taille des lettres mais la finesse du trait (CONCEPT.md §4.1).

    On mélange les segments horizontaux et verticaux avant de prendre la
    médiane. Un trait produit un segment long dans son sens et beaucoup de
    segments courts en travers : les courts dominent, et la médiane tombe
    donc sur l'épaisseur, quelle que soit l'orientation de l'écriture.
    """
    runs = np.concatenate([_run_lengths(ink), _run_lengths(ink.T)])
    return float(np.median(runs)) if runs.size else 0.0
