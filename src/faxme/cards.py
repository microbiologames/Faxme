"""Génération des fiches A6 que l'enfant remplit.

Tout ce qui est pré-imprimé (réglure, cadre, mentions) l'est dans un orange
très clair dont la composante rouge est saturée. Le pipeline ne lisant que le
canal rouge (cf. ``capture.gray_channel``), ces repères apparaissent blancs et
**ne partent donc jamais sur le ticket** : l'enfant est guidé, le destinataire
ne reçoit que l'écriture.

Conséquence à respecter : le feutre doit être noir ou bleu foncé, jamais rouge
ni orange, sinon il disparaîtrait exactement de la même façon.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from .config import Config
from .fonts import load_font

# Rouge saturé à 255 : invisible dans le canal rouge, visible à l'œil.
GUIDE = (255, 186, 158)
BAND = (255, 168, 130)
CUT = (215, 215, 215)

# Hauteur de la bande orange pleine largeur imprimée en haut des fiches réglées.
# C'est à elle que la boîte reconnaît une fiche guidée et sait qu'elle doit lire
# le canal rouge. Généreuse à dessein : le recadrage rogne quelques millimètres
# du haut, et il doit en rester assez pour la reconnaître à coup sûr.
BAND_MM = 14.0


def card(config: Config, dpi: int = 300) -> Image.Image:
    """Une fiche A6 réglée, prête à écrire."""
    card_config = config.card
    px = dpi / 25.4
    width = int(round(card_config.width_mm * px))
    height = int(round(card_config.height_mm * px))
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    margin = 8.0
    thin = max(1, int(round(0.25 * px)))

    # Bande de reconnaissance. Ne rien y écrire : c'est elle que la boîte lit
    # pour savoir qu'il s'agit d'une fiche réglée.
    draw.rectangle([0, 0, width, int(BAND_MM * px)], fill=BAND)

    # Cadre de la zone écrite.
    draw.rectangle(
        [int(margin * px), int((BAND_MM + 4) * px),
         width - int(margin * px), height - int(margin * px)],
        outline=GUIDE, width=thin,
    )

    inner_left = int(margin * px) + int(2 * px)
    inner_right = width - int(margin * px) - int(2 * px)

    label = load_font(int(round(4.0 * px)), bold=True)
    draw.text((inner_left, int((BAND_MM + 6) * px)), "POUR", font=label, fill=GUIDE)
    # Une ligne pour le prénom, juste sous la mention.
    name_line = BAND_MM + 16.0
    draw.line([inner_left + int(18 * px), int(name_line * px), inner_right, int(name_line * px)],
              fill=GUIDE, width=thin)

    # Réglure : des lignes larges, pour que le papier apprenne à écrire gros.
    y = BAND_MM + 30.0
    while y <= card_config.height_mm - margin - 2:
        draw.line([inner_left, int(y * px), inner_right, int(y * px)], fill=GUIDE, width=thin)
        y += card_config.ruling_mm

    # Repères d'angle, pour poser la fiche bien à plat contre les butées.
    tick = int(4 * px)
    for x_edge, y_edge in ((0, 0), (width, 0), (0, height), (width, height)):
        sx = 1 if x_edge == 0 else -1
        sy = 1 if y_edge == 0 else -1
        draw.line([x_edge, y_edge + sy * tick, x_edge, y_edge], fill=GUIDE, width=thin * 2)
        draw.line([x_edge + sx * tick, y_edge, x_edge, y_edge], fill=GUIDE, width=thin * 2)
    return image


def blank_card(config: Config, dpi: int = 300) -> Image.Image:
    """Une fiche A6 entièrement blanche, pour les dessins.

    Rigoureusement rien d'imprimé, pas même un repère d'angle : sans bande
    orange, la boîte lit la photo en luminance et garde donc toutes les
    couleurs du crayon. Un repère imprimé, lui, finirait sur le ticket.
    """
    px = dpi / 25.4
    return Image.new(
        "RGB",
        (int(round(config.card.width_mm * px)), int(round(config.card.height_mm * px))),
        "white",
    )


def sheet(config: Config, dpi: int = 300, blank: bool = False) -> Image.Image:
    """Quatre fiches A6 sur une A4, avec les traits de coupe."""
    px = dpi / 25.4
    page = Image.new("RGB", (int(round(210 * px)), int(round(297 * px))), "white")
    one = blank_card(config, dpi) if blank else card(config, dpi)
    for column in range(2):
        for row in range(2):
            page.paste(one, (column * one.width, row * one.height))
    draw = ImageDraw.Draw(page)
    draw.line([one.width, 0, one.width, page.height], fill=CUT, width=max(1, int(0.2 * px)))
    draw.line([0, one.height, page.width, one.height], fill=CUT, width=max(1, int(0.2 * px)))
    return page
