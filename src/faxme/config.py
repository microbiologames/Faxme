"""Configuration d'une boîte.

Deux principes :

- **Les réglages sont en millimètres, pas en pixels.** Le pipeline convertit
  vers les pixels à partir de la géométrie connue de la fiche. On peut donc
  changer de caméra, de résolution ou de format de fiche sans retoucher un
  seul paramètre de traitement.
- **Le recadrage est fixe.** La caméra est vissée et la fiche vient contre des
  butées : sa position dans l'image ne change jamais. C'est ce qui permet de
  se passer de toute détection de contour (cf. CONCEPT.md §4.2).
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass(frozen=True)
class PrinterConfig:
    """Imprimante thermique 80 mm par défaut."""

    dots_per_line: int = 576  # 72 mm imprimables
    dpi: int = 203

    @property
    def dots_per_mm(self) -> float:
        return self.dpi / 25.4

    @property
    def width_mm(self) -> float:
        return self.dots_per_line / self.dots_per_mm


@dataclass(frozen=True)
class CardConfig:
    """La fiche que l'enfant remplit. A6 par défaut (cf. CONCEPT.md §4.1)."""

    width_mm: float = 105.0
    height_mm: float = 148.0
    ruling_mm: float = 8.0  # interligne des fiches pré-imprimées


@dataclass(frozen=True)
class CaptureConfig:
    """Géométrie fixe de la prise de vue.

    ``crop`` est le rectangle de la fiche dans l'image, en fractions de
    l'image (gauche, haut, droite, bas). Il se calibre une fois à
    l'installation avec ``faxme calibrer``.
    """

    crop: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0)
    rotate_quarters: int = 0  # rotations de 90° appliquées avant le recadrage
    resolution: tuple[int, int] = (2304, 1296)

    # "red"  : on ne garde que le canal rouge de la photo. Tout ce qui est
    #          imprimé sur la fiche en orange clair (réglure, cadre, mentions)
    #          y apparaît blanc et disparaît donc du ticket, alors que le
    #          feutre noir ou bleu reste parfaitement noir. C'est ce qui permet
    #          d'avoir des fiches guidées sans que les lignes soient envoyées.
    #          Contrepartie : ne jamais écrire au feutre rouge ou orange.
    # "luma" : conversion classique, à utiliser avec des fiches vierges.
    gray_channel: str = "red"


@dataclass(frozen=True)
class PipelineConfig:
    """Réglages du traitement, tous exprimés en mm sur la fiche."""

    # Largeur de travail, en multiple de la largeur finale du ticket.
    # Mesuré : passer de 3 à 2 divise le temps de traitement par trois sans
    # changer ni l'épaisseur de trait, ni la longueur du ticket, ni l'angle
    # trouvé — y compris avec un trait fin. On reste néanmoins à deux fois la
    # résolution finale pour que la binarisation voie plus finement que le
    # point d'imprimante.
    working_factor: float = 2.0

    illumination_mm: float = 10.0  # rayon du flou qui modélise l'éclairage
    sauvola_window_mm: float = 3.0  # ~ la hauteur d'une minuscule
    sauvola_k: float = 0.20
    deskew_max_deg: float = 4.0
    margin_mm: float = 2.0  # marge blanche laissée autour de l'écriture

    # Bande ignorée sur le pourtour de la fiche. Le bord du papier, son ombre
    # portée et un recadrage un peu large produisent une ligne noire franche
    # qui, sans cela, deviendrait le plus gros « trait » de la lettre : elle
    # fausserait le cadrage comme le redressement.
    border_mm: float = 3.0
    # Épaisseur minimale visée pour le trait, en points d'imprimante. On
    # n'épaissit **que si c'est nécessaire** : dilater un trait déjà large
    # bouche les boucles des a, des e et des o.
    min_stroke_dots: int = 3

    # "trim" : largeur de la fiche entière, hauteur rognée sur l'écriture.
    #          L'échelle horizontale est donc la même pour toutes les lettres
    #          (une minuscule fait toujours la même taille sur le ticket) et
    #          le ticket n'est jamais plus long que ce qui a été écrit.
    # "card" : la fiche entière, y compris le bas resté blanc.
    # "ink"  : on recadre aussi en largeur. L'écriture remplit le ticket, donc
    #          elle sort plus grosse — mais l'échelle change d'une lettre à
    #          l'autre, et trois mots deviennent une affiche.
    fit: str = "trim"

    # En dessous, on considère que la fiche est vide et on refuse l'envoi.
    min_ink_ratio: float = 0.0005


@dataclass(frozen=True)
class TicketConfig:
    """L'en-tête imprimé en haut du ticket."""

    header: bool = True
    sender: str = "Léo"
    header_height_mm: float = 5.0
    feed_lines: int = 3  # avance papier avant la coupe


@dataclass(frozen=True)
class Config:
    printer: PrinterConfig = field(default_factory=PrinterConfig)
    card: CardConfig = field(default_factory=CardConfig)
    capture: CaptureConfig = field(default_factory=CaptureConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    ticket: TicketConfig = field(default_factory=TicketConfig)

    @classmethod
    def load(cls, path: str | Path | None) -> "Config":
        """Charge un fichier TOML. Sans chemin, renvoie les valeurs par défaut."""
        if path is None:
            return cls()
        raw = tomllib.loads(Path(path).read_text(encoding="utf-8"))
        sections = {
            "printer": PrinterConfig,
            "card": CardConfig,
            "capture": CaptureConfig,
            "pipeline": PipelineConfig,
            "ticket": TicketConfig,
        }
        kwargs = {}
        for name, klass in sections.items():
            values = raw.get(name, {})
            unknown = set(values) - {f for f in klass.__dataclass_fields__}
            if unknown:
                raise ValueError(
                    f"[{name}] : réglage inconnu {sorted(unknown)} dans {path}"
                )
            if "crop" in values:
                values["crop"] = tuple(values["crop"])
            if "resolution" in values:
                values["resolution"] = tuple(values["resolution"])
            kwargs[name] = klass(**values)
        return cls(**kwargs)

    def as_dict(self) -> dict:
        return asdict(self)

    # --- conversions mm <-> pixels ------------------------------------------

    @property
    def working_width(self) -> int:
        """Largeur en pixels de l'image de travail."""
        return int(round(self.printer.dots_per_line * self.pipeline.working_factor))

    @property
    def working_px_per_mm(self) -> float:
        """Échelle de l'image de travail, sachant qu'elle couvre toute la fiche."""
        return self.working_width / self.card.width_mm
