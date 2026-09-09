"""La boucle locale de la phase 0, sur le Pi.

Un bouton, la caméra, l'imprimante, rien d'autre : pas de réseau, pas de
destinataire. Le but est de valider le rendu du ticket avec l'écriture réelle
d'un enfant avant de construire quoi que ce soit d'autre.
"""

from __future__ import annotations

import time
from datetime import datetime

from . import escpos, pipeline, ticket
from .capture import PiCameraSource
from .config import Config
from .imaging import EmptyCard


def run(config: Config, *, device: str, button_pin: int) -> int:  # pragma: no cover
    try:
        from gpiozero import Button
    except ImportError as error:
        raise RuntimeError(
            "gpiozero est introuvable : la boucle ne tourne que sur le Pi "
            "(pip install 'faxme[pi]')."
        ) from error

    camera = PiCameraSource(config)
    button = Button(button_pin, bounce_time=0.05)
    print(f"prêt — appuie sur le bouton (GPIO {button_pin}). Ctrl-C pour arrêter.")
    try:
        while True:
            button.wait_for_press()
            started = time.monotonic()
            try:
                result = pipeline.process(camera.grab(), config)
            except EmptyCard as error:
                print(f"refusé : {error}")
                continue
            full = ticket.render(result.ink, config, when=datetime.now())
            escpos.send(full, device, config.ticket.feed_lines)
            print(
                f"imprimé en {time.monotonic() - started:.1f}s — "
                f"{result.stats['length_mm']} mm, "
                f"trait {result.stats['stroke_dots']:.0f} points"
            )
            button.wait_for_release()
    except KeyboardInterrupt:
        print("\narrêt.")
        return 0
    finally:
        camera.close()
