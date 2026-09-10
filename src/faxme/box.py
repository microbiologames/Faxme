"""Le service de la boîte, phase 1 : e-mail + deux boutons.

Ce qui tourne en permanence sur le Pi. Deux fils d'exécution seulement :

- une **relève** de la boîte aux lettres toutes les minutes ;
- une **boucle de boutons**, qui ne fait qu'appeler les opérations de
  ``service.py``.

Le tableau de bord complet (huit voyants, roue, quatre sons) est la phase 4 :
ici on se contente de deux voyants facultatifs, parce qu'un objet muet est
invivable même pendant les essais.
"""

from __future__ import annotations

import threading
import time
from datetime import datetime

from . import pipeline, service, ticket
from .capture import PiCameraSource
from .config import Config
from .contacts import AddressBook, Contact
from .imaging import EmptyCard
from .mailbox import Gateway
from .store import Store


class Lamp:
    """Un voyant, ou rien du tout si aucune broche n'est câblée."""

    def __init__(self, pin: int | None):
        self._led = None
        if pin:
            from gpiozero import LED

            self._led = LED(pin)

    def set(self, on: bool) -> None:
        if self._led is not None:
            self._led.on() if on else self._led.off()


def poll_forever(
    store: Store, config: Config, gateway: Gateway, mail_lamp: Lamp, stop: threading.Event
) -> None:
    """Relève le courrier en boucle. Une panne de réseau ne doit rien figer."""
    while not stop.is_set():
        try:
            report = service.collect(store, config, gateway)
            if report.accepted:
                print(f"[courrier] {report}")
        except Exception as error:  # noqa: BLE001 - le réseau tombe, la boîte reste vivante
            print(f"[courrier] relève impossible : {error}")
        mail_lamp.set(bool(store.pending()))
        stop.wait(config.mail.poll_seconds)


def run(  # pragma: no cover - dépend du matériel
    config: Config,
    *,
    data_dir: str,
    device: str,
    password: str,
    send_pin: int,
    print_pin: int,
    mail_pin: int | None = None,
    error_pin: int | None = None,
    default_contact: str | None = None,
) -> int:
    from gpiozero import Button

    book = AddressBook(config.contacts)
    contact = _default_contact(book, default_contact)
    store = Store(data_dir, config)
    gateway = Gateway(config, password)
    mail_lamp, error_lamp = Lamp(mail_pin), Lamp(error_pin)

    camera = PiCameraSource(config)
    send_button = Button(send_pin, bounce_time=0.05)
    print_button = Button(print_pin, bounce_time=0.05)

    stop = threading.Event()
    poller = threading.Thread(
        target=poll_forever, args=(store, config, gateway, mail_lamp, stop), daemon=True
    )
    poller.start()

    print(f"prêt — envoi vers {contact.name}, impression du courrier reçu.")
    try:
        while True:
            if send_button.is_pressed:
                _handle_send(store, config, gateway, camera, contact, error_lamp)
                send_button.wait_for_release()
            elif print_button.is_pressed:
                _handle_print(store, config, device, mail_lamp, error_lamp)
                print_button.wait_for_release()
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\narrêt.")
        return 0
    finally:
        stop.set()
        camera.close()
        store.close()


def _default_contact(book: AddressBook, name: str | None) -> Contact:
    if name:
        contact = book.by_name(name)
        if contact is None:
            raise SystemExit(f"contact inconnu : {name}")
        return contact
    candidates = [c for c in book if c.kind == "email"]
    if len(candidates) != 1:
        raise SystemExit(
            "préciser le destinataire : le carnet en compte "
            f"{len(candidates)} (la roue arrive en phase 4)"
        )
    return candidates[0]


def _handle_send(store, config, gateway, camera, contact, error_lamp) -> None:  # pragma: no cover
    error_lamp.set(False)
    try:
        result = pipeline.process(camera.grab(), config)
    except EmptyCard as error:
        print(f"[envoi] refusé : {error}")
        return
    raster = ticket.render(result.ink, config, when=datetime.now())
    try:
        service.send_letter(store, config, gateway, contact, raster)
    except (service.QuotaExhausted, service.Sleeping) as raison:
        print(f"[envoi] {raison}")
        return
    except Exception as error:  # noqa: BLE001
        print(f"[envoi] échec : {error}")
        error_lamp.set(True)
        return
    print(f"[envoi] lettre partie à {contact.name} — "
          f"{store.credits_left()} restante(s) aujourd'hui")


def _handle_print(store, config, device, mail_lamp, error_lamp) -> None:  # pragma: no cover
    error_lamp.set(False)
    try:
        message = service.print_next(store, config, device)
    except service.Sleeping as raison:
        print(f"[impression] {raison}")
        return
    except Exception as error:  # noqa: BLE001
        print(f"[impression] échec : {error}")
        error_lamp.set(True)
        return
    if message is None:
        print("[impression] aucune lettre en attente")
    else:
        print(f"[impression] lettre de {message.contact}")
    mail_lamp.set(bool(store.pending()))
