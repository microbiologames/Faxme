"""La passerelle e-mail (CONCEPT.md §7).

Le fichier est écrit en deux moitiés séparées à dessein :

- **la décision** — qui a le droit d'écrire, le message est-il authentique, que
  contient-il — qui est du code pur, testable hors ligne sur des messages
  fabriqués, et qui est la partie où une erreur a des conséquences ;
- **le transport** — IMAP et SMTP — qui n'est qu'une trentaine de lignes de
  bibliothèque standard.

C'est la première ouverture du système vers l'extérieur : tout ce qui suit
part du principe qu'un message est hostile jusqu'à preuve du contraire.
"""

from __future__ import annotations

import email
import imaplib
import re
import smtplib
import subprocess
import tempfile
from dataclasses import dataclass, replace
from email import policy as email_policy
from email.message import EmailMessage
from email.utils import parseaddr
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

from . import pipeline, textletter, ticket
from .config import Config
from .contacts import AddressBook, Contact

IMAGE_TYPES = {"image/jpeg", "image/png", "image/heic", "image/heif", "image/webp"}


class Rejected(Exception):
    """Le message n'ira pas au papier. La raison sert au journal, pas au ticket."""


@dataclass
class Accepted:
    contact: Contact
    pages: list[np.ndarray]
    external_id: str


# --- la décision -------------------------------------------------------------


def sender_address(message: EmailMessage) -> str:
    return parseaddr(message.get("From", ""))[1].strip().lower()


def delivered_alias(message: EmailMessage, base_address: str) -> str:
    """Extrait le ``+suffixe`` de l'adresse à laquelle le message a été livré.

    L'alias sert à **identifier** le correspondant, pas à l'authentifier : sur
    Gmail, n'importe qui connaissant l'adresse de base peut y ajouter le
    suffixe de son choix. L'authentification, c'est la liste blanche plus
    SPF/DKIM.
    """
    local = base_address.split("@")[0].lower()
    for header in ("Delivered-To", "X-Original-To", "To", "Cc"):
        for value in message.get_all(header, []):
            for candidate in re.findall(r"[\w.+-]+@[\w.-]+", value):
                name = candidate.split("@")[0].lower()
                if name.startswith(local + "+"):
                    return name[len(local) + 1 :]
    return ""


def authentication_ok(message: EmailMessage) -> tuple[bool, str]:
    """Lit l'en-tête ``Authentication-Results`` posé par notre fournisseur.

    On ne regarde que le **premier**, celui qu'ajoute le serveur qui nous
    livre : les suivants ont été écrits par des machines en amont, dont un
    attaquant fait partie. Sans cette vérification, le champ ``From`` se
    falsifie en trois secondes et n'importe qui peut faire imprimer ce qu'il
    veut chez un enfant.
    """
    headers = message.get_all("Authentication-Results", [])
    if not headers:
        return False, "aucun en-tête Authentication-Results"
    results = headers[0].lower()

    def verdict(method: str) -> str | None:
        found = re.search(rf"\b{method}=(\w+)", results)
        return found.group(1) if found else None

    if verdict("dmarc") == "pass":
        return True, "dmarc=pass"
    if verdict("dkim") == "pass" and verdict("spf") == "pass":
        return True, "dkim=pass spf=pass"
    return False, f"authentification refusée ({results.strip()[:120]})"


def _email_pipeline_config(config: Config) -> Config:
    """La configuration du pipeline pour une photo reçue par e-mail.

    Rien à voir avec une fiche posée contre des butées : le cadrage calibré de
    la boîte n'a aucun sens ici, la photo est prise à main levée et cadrée au
    jugé. On prend donc l'image entière, en luminance — il n'y a pas de
    réglure orange à faire disparaître — et on recadre sur le contenu, sans
    quoi on imprimerait surtout de la table.
    """
    return replace(
        config,
        capture=replace(config.capture, crop=(0.0, 0.0, 1.0, 1.0), gray_channel="luma"),
        pipeline=replace(config.pipeline, fit="ink", border_mm=0.0),
    )


def _open_image(payload: bytes) -> Image.Image:
    try:
        return Image.open(BytesIO(payload)).convert("RGB")
    except Exception:
        try:  # les photos d'iPhone arrivent parfois en HEIC
            import pillow_heif

            pillow_heif.register_heif_opener()
        except ImportError as error:
            raise Rejected(
                "image illisible (HEIC ? installer 'faxme[heic]')"
            ) from error
        return Image.open(BytesIO(payload)).convert("RGB")


def _pdf_first_page(payload: bytes) -> Image.Image:
    """Rend la première page d'un PDF avec pdftoppm, si poppler est installé.

    Les scanners de téléphone produisent des PDF : les ignorer reviendrait à
    refuser le format le plus probable. On s'appuie sur ``poppler-utils``
    (paquet apt) plutôt que sur une bibliothèque Python, qui serait lourde.
    """
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "in.pdf"
        source.write_bytes(payload)
        try:
            subprocess.run(
                ["pdftoppm", "-png", "-r", "200", "-f", "1", "-l", "1",
                 str(source), str(Path(directory) / "page")],
                check=True, capture_output=True, timeout=60,
            )
        except FileNotFoundError as error:
            raise Rejected("PDF reçu mais pdftoppm absent (apt install poppler-utils)") from error
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            raise Rejected("PDF illisible") from error
        rendered = sorted(Path(directory).glob("page*.png"))
        if not rendered:
            raise Rejected("PDF sans page")
        return Image.open(rendered[0]).convert("RGB")


def pages_from(message: EmailMessage, config: Config) -> list[np.ndarray]:
    """Les pages à imprimer : les pièces jointes, sinon le texte du message."""
    mail = config.mail
    limit = mail.max_attachment_mb * 1024 * 1024
    photo_config = _email_pipeline_config(config)
    pages: list[np.ndarray] = []

    for part in message.walk():
        if len(pages) >= mail.max_pages:
            break
        content_type = (part.get_content_type() or "").lower()
        if content_type not in IMAGE_TYPES and content_type != "application/pdf":
            continue
        payload = part.get_payload(decode=True) or b""
        if not payload or len(payload) > limit:
            continue
        image = _pdf_first_page(payload) if content_type == "application/pdf" else _open_image(payload)
        try:
            pages.append(pipeline.process(image, photo_config).ink)
        except pipeline.EmptyCard:
            continue  # une pièce jointe blanche n'est pas une lettre

    if pages:
        return pages

    body = message.get_body(preferencelist=("plain",))
    if body is not None:
        text = body.get_content()
        try:
            return [textletter.render(text, config)]
        except ValueError:
            pass
    raise Rejected("ni image exploitable ni texte")


def accept(message: EmailMessage, book: AddressBook, config: Config) -> Accepted:
    """Décide si un message a le droit d'atteindre le papier. Lève ``Rejected`` sinon."""
    sender = sender_address(message)
    contact = book.by_address(sender)
    if contact is None or contact.kind != "email":
        raise Rejected(f"expéditeur hors carnet : {sender or '(vide)'}")

    if config.mail.require_authentication:
        ok, reason = authentication_ok(message)
        if not ok:
            raise Rejected(f"{sender} : {reason}")

    alias = delivered_alias(message, config.mail.address)
    if alias and contact.alias and alias.lower() != contact.alias.lower():
        raise Rejected(f"{sender} : alias {alias!r} ne correspond pas au carnet")

    external_id = (message.get("Message-ID") or "").strip()
    if not external_id:
        raise Rejected(f"{sender} : message sans Message-ID")

    return Accepted(contact=contact, pages=pages_from(message, config), external_id=external_id)


# --- le transport ------------------------------------------------------------


def build_outgoing(
    ink: np.ndarray, contact: Contact, config: Config, child_name: str
) -> EmailMessage:
    """Le message envoyé à un adulte : l'image, et une invitation à répondre."""
    message = EmailMessage()
    message["From"] = config.mail.address
    message["To"] = contact.address
    message["Subject"] = f"Une lettre de {child_name}"
    message.set_content(
        f"{child_name} t'a écrit. Sa lettre est en pièce jointe.\n\n"
        "Réponds à ce message, même juste avec une photo d'un mot ou d'un "
        f"dessin : {child_name} pourra l'imprimer et le lire tout seul.\n"
    )
    buffer = BytesIO()
    ticket.to_image(ink).save(buffer, format="PNG")
    message.add_attachment(
        buffer.getvalue(), maintype="image", subtype="png", filename="lettre.png"
    )
    return message


class Gateway:
    """IMAP et SMTP, en bibliothèque standard. Volontairement mince."""

    def __init__(self, config: Config, password: str):
        self.config = config
        self._password = password

    def fetch(self) -> list[tuple[bytes, EmailMessage]]:
        """Relève les messages non lus. Renvoie (identifiant serveur, message)."""
        mail = self.config.mail
        with imaplib.IMAP4_SSL(mail.imap_host, mail.imap_port) as client:
            client.login(mail.address, self._password)
            client.select("INBOX")
            _, data = client.search(None, "UNSEEN")
            messages = []
            for number in data[0].split():
                _, payload = client.fetch(number, "(RFC822)")
                if payload and payload[0]:
                    messages.append(
                        (number, email.message_from_bytes(payload[0][1], policy=email_policy.default))
                    )
            return messages

    def delete(self, numbers: list[bytes]) -> None:
        """Supprime définitivement, corbeille comprise : rien ne se garde (§7.6)."""
        if not numbers:
            return
        mail = self.config.mail
        with imaplib.IMAP4_SSL(mail.imap_host, mail.imap_port) as client:
            client.login(mail.address, self._password)
            client.select("INBOX")
            for number in numbers:
                client.store(number, "+FLAGS", "\\Deleted")
            client.expunge()

    def send(self, message: EmailMessage) -> None:
        mail = self.config.mail
        with smtplib.SMTP_SSL(mail.smtp_host, mail.smtp_port) as server:
            server.login(mail.address, self._password)
            server.send_message(message)
