"""Ce qui relie la passerelle, le magasin et le papier.

Trois opérations, et les garde-fous qui vont avec : relever le courrier,
imprimer la lettre suivante, envoyer une lettre à un adulte.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from email.message import EmailMessage

import numpy as np

from . import escpos, mailbox, ticket
from .config import Config
from .contacts import AddressBook, Contact
from .mailbox import Gateway, MissingKeyword, Rejected
from .store import Message, Store


class QuotaExhausted(Exception):
    """Plus de crédit aujourd'hui. Refus doux, jamais une lettre perdue."""


class Sleeping(Exception):
    """Mode nuit : la lettre attend le matin, elle n'est pas perdue."""


@dataclass
class CollectReport:
    accepted: list[str] = field(default_factory=list)
    rejected: list[str] = field(default_factory=list)
    duplicates: int = 0
    hinted: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        hints = f", {len(self.hinted)} rappel(s) de la règle" if self.hinted else ""
        return (
            f"{len(self.accepted)} lettre(s) reçue(s), "
            f"{len(self.rejected)} refusée(s), {self.duplicates} déjà connue(s)"
            f"{hints}"
        )


def collect(store: Store, config: Config, gateway: Gateway) -> CollectReport:
    """Relève la boîte aux lettres et met le courrier en attente d'impression.

    Le message est supprimé du serveur **uniquement** si son sort est réglé :
    enregistré, refusé, ou déjà connu. En cas d'erreur inattendue on le laisse
    en place, quitte à le retraiter : perdre une lettre est pire que la voir
    deux fois, et l'idempotence par Message-ID couvre la seconde.
    """
    book = AddressBook(config.contacts)
    report = CollectReport()
    to_delete: list[bytes] = []

    for number, message in gateway.fetch():
        try:
            accepted = mailbox.accept(message, book, config)
        except MissingKeyword as reason:
            # Un adulte du carnet a simplement oublié l'objet : on le lui dit,
            # au lieu de le laisser croire que sa lettre est arrivée.
            report.rejected.append(str(reason))
            if _hint(message, store, config, gateway):
                report.hinted.append(mailbox.sender_address(message))
            to_delete.append(number)
            continue
        except Rejected as reason:
            report.rejected.append(str(reason))
            _forward_unknown(message, config, gateway)
            to_delete.append(number)
            continue

        stored = store.add(
            direction="in",
            contact=accepted.contact.name,
            source="email",
            pages=accepted.pages,
            external_id=accepted.external_id,
        )
        if stored is None:
            report.duplicates += 1
        else:
            report.accepted.append(accepted.contact.name)
        to_delete.append(number)

    gateway.delete(to_delete)
    return report


def _hint(message: EmailMessage, store: Store, config: Config, gateway: Gateway) -> bool:
    """Explique la règle à un expéditeur du carnet. Renvoie True si c'est parti."""
    if not config.mail.reply_hint or mailbox.looks_automated(message):
        return False
    address = mailbox.sender_address(message)
    if not address or not store.should_hint(address):
        return False
    try:
        gateway.send(mailbox.build_hint(address, config, config.ticket.sender))
    except Exception:  # noqa: BLE001 - un rappel raté ne doit rien bloquer
        return False
    return True


def _forward_unknown(message: EmailMessage, config: Config, gateway: Gateway) -> None:
    """Réexpédie aux parents ce qui a été refusé, s'ils l'ont demandé."""
    destination = config.mail.forward_unknown_to
    if not destination:
        return
    forward = EmailMessage()
    forward["From"] = config.mail.address
    forward["To"] = destination
    forward["Subject"] = "Faxme : message refusé"
    forward.set_content(
        "Un message a été refusé et n'a pas été imprimé.\n"
        f"Expéditeur annoncé : {message.get('From', '(inconnu)')}\n"
        f"Objet : {message.get('Subject', '(sans objet)')}\n"
    )
    forward.add_attachment(
        message.as_bytes(), maintype="message", subtype="rfc822", filename="message.eml"
    )
    try:
        gateway.send(forward)
    except Exception:  # noqa: BLE001 - une réexpédition ratée ne doit rien bloquer
        pass


def print_next(
    store: Store, config: Config, device: str, *, now: datetime | None = None
) -> Message | None:
    """Imprime la plus ancienne lettre en attente. Renvoie None s'il n'y a rien."""
    now = now or datetime.now()
    if store.is_night(now):
        raise Sleeping("mode nuit : la lettre sortira demain matin")
    message = store.next_to_print()
    if message is None:
        return None

    for number in range(1, message.pages + 1):
        raster = ticket.render(
            message.page(number),
            config,
            sender=message.contact,
            when=message.created_at,
        )
        escpos.send(raster, device, config.ticket.feed_lines)
    store.settle(message.id, "printed", now)
    store.purge(now)
    return message


def send_letter(
    store: Store,
    config: Config,
    gateway: Gateway,
    contact: Contact,
    ink: np.ndarray,
    *,
    child_name: str | None = None,
    now: datetime | None = None,
) -> Message:
    """Envoie une lettre à un adulte. Consomme un crédit du quota du jour."""
    now = now or datetime.now()
    if store.is_night(now):
        raise Sleeping("mode nuit : la boîte n'envoie pas la nuit")
    if store.credits_left(now) <= 0:
        raise QuotaExhausted(
            f"plus de lettre disponible aujourd'hui ({config.quota.daily_letters} par jour)"
        )
    if contact.kind != "email":
        raise ValueError(f"{contact.name} n'est pas un contact e-mail")

    message = store.add(
        direction="out", contact=contact.name, source="email", pages=[ink],
        created_at=now,
    )
    try:
        gateway.send(
            mailbox.build_outgoing(
                ink, contact, config, child_name or config.ticket.sender
            )
        )
    except Exception:
        store.settle(message.id, "failed", now)
        raise
    # Pas d'accusé de lecture en e-mail : « partie » est tout ce qu'on sait
    # honnêtement dire (CONCEPT.md §7.5).
    store.settle(message.id, "sent", now)
    store.purge(now)
    return message
