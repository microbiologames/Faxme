"""Le strict minimum d'ESC/POS pour envoyer une image à une thermique 80 mm.

Une trentaine de lignes suffisent, donc pas de dépendance : une brique de
moins à installer sur le Pi et à voir casser dans deux ans.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

INIT = b"\x1b@"


def feed(lines: int) -> bytes:
    return b"\x1bd" + bytes([max(0, min(255, lines))])


def partial_cut() -> bytes:
    return b"\x1dV\x42\x00"


def raster(ink: np.ndarray, band_height: int = 128) -> bytes:
    """Encode le masque d'encre en commandes GS v 0.

    Découpé en bandes : beaucoup d'imprimantes bon marché avalent mal une
    image de plusieurs milliers de lignes en une seule commande.
    """
    if ink.ndim != 2:
        raise ValueError("le raster attend un masque 2D")
    height, width = ink.shape
    if width % 8:
        ink = np.pad(ink, ((0, 0), (0, 8 - width % 8)))
        width = ink.shape[1]
    width_bytes = width // 8

    out = bytearray()
    for top in range(0, height, band_height):
        band = ink[top : top + band_height]
        rows = band.shape[0]
        packed = np.packbits(band.astype(np.uint8), axis=1)  # 1 = point noir
        out += b"\x1dv0\x00"
        out += bytes([width_bytes & 0xFF, width_bytes >> 8, rows & 0xFF, rows >> 8])
        out += packed.tobytes()
    return bytes(out)


def ticket_bytes(ink: np.ndarray, feed_lines: int = 3, cut: bool = True) -> bytes:
    payload = INIT + raster(ink) + feed(feed_lines)
    return payload + partial_cut() if cut else payload


def send(ink: np.ndarray, device: str | Path, feed_lines: int = 3, cut: bool = True) -> int:
    """Écrit le ticket sur le périphérique (typiquement /dev/usb/lp0)."""
    payload = ticket_bytes(ink, feed_lines, cut)
    with open(device, "wb") as handle:
        handle.write(payload)
    return len(payload)
