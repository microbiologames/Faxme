"""La partie où une erreur laisse quelqu'un imprimer chez un enfant."""

from dataclasses import replace
from email.message import EmailMessage
from io import BytesIO

import pytest

from faxme import mailbox, simulate
from faxme.config import Config, MailConfig
from faxme.contacts import AddressBook, Contact
from faxme.mailbox import Rejected
from faxme.ticket import to_image

BASE = "raphael.faxme@gmail.com"


def make_config() -> Config:
    return replace(Config(), mail=replace(MailConfig(), address=BASE))


def make_book() -> AddressBook:
    return AddressBook([
        Contact("Mamie", "email", "mamie@example.com", 2),
        Contact("Papa", "email", "papa@example.com", 3),
        Contact("Léo", "box", "leo-boite.tailnet", wheel=1),
    ])


def make_message(
    sender="Mamie <mamie@example.com>",
    auth="dmarc=pass",
    subject="RAPH.FAXME",
    body="Coucou mon grand, gros bisous de Bretagne !",
    message_id="<abc@example.com>",
) -> EmailMessage:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = BASE
    if subject is not None:
        message["Subject"] = subject
    if message_id:
        message["Message-ID"] = message_id
    if auth:
        message["Authentication-Results"] = f"mx.google.com; {auth}"
    message.set_content(body)
    return message


def test_a_known_sender_with_dmarc_passes():
    accepted = mailbox.accept(make_message(), make_book(), make_config())
    assert accepted.contact.name == "Mamie"
    assert len(accepted.pages) == 1
    assert accepted.pages[0].shape[1] == 576


def test_dkim_and_spf_are_accepted_when_there_is_no_dmarc():
    accepted = mailbox.accept(
        make_message(auth="dkim=pass; spf=pass"), make_book(), make_config()
    )
    assert accepted.contact.name == "Mamie"


@pytest.mark.parametrize(
    "message, expected",
    [
        (make_message(sender="pub@spam.example"), "hors carnet"),
        (make_message(auth="dkim=fail; spf=softfail"), "authentification"),
        (make_message(auth=None), "Authentication-Results"),
        (make_message(auth="spf=pass"), "authentification"),  # SPF seul ne suffit pas
        (make_message(body="\n\n"), "ni image"),
        (make_message(message_id=None), "Message-ID"),
    ],
)
def test_everything_else_is_refused(message, expected):
    with pytest.raises(Rejected, match=expected):
        mailbox.accept(message, make_book(), make_config())


def test_a_box_contact_cannot_write_by_email():
    """Le carnet distingue les boîtes des adultes : une boîte n'écrit pas par e-mail."""
    message = make_message(sender="leo-boite.tailnet")
    with pytest.raises(Rejected, match="hors carnet"):
        mailbox.accept(message, make_book(), make_config())


def test_only_the_first_authentication_header_is_trusted():
    """Les en-têtes du bas ont été écrits en amont : un attaquant peut en poser."""
    message = make_message(auth="dmarc=fail")
    message["Authentication-Results"] = "attaquant.example; dmarc=pass"
    with pytest.raises(Rejected, match="authentification"):
        mailbox.accept(message, make_book(), make_config())


def test_an_attached_photo_is_printed_instead_of_the_body():
    config = make_config()
    photo = simulate.fake_photo(config)
    buffer = BytesIO()
    photo.save(buffer, format="PNG")

    message = make_message(body="Regarde ce que j'ai écrit")
    message.add_attachment(
        buffer.getvalue(), maintype="image", subtype="png", filename="lettre.png"
    )
    accepted = mailbox.accept(message, make_book(), config)
    assert len(accepted.pages) == 1
    # Une photo prise à main levée : le cadrage calibré de la boîte ne s'applique pas.
    assert accepted.pages[0].mean() > 0.005


def test_attachments_are_capped():
    config = replace(make_config(), mail=replace(make_config().mail, max_pages=2))
    photo = simulate.fake_photo(config)
    buffer = BytesIO()
    photo.save(buffer, format="PNG")
    message = make_message()
    for index in range(4):
        message.add_attachment(
            buffer.getvalue(), maintype="image", subtype="png",
            filename=f"page{index}.png",
        )
    assert len(mailbox.accept(message, make_book(), config).pages) == 2


@pytest.mark.parametrize(
    "subject",
    [
        "RAPH.FAXME",
        "raph faxme",
        "Re: RAPH.FAXME — une lettre de Raphaël",
        "TR : Raph-Faxme (photo du chat)",
        "RAPH.FAXME coucou mon grand",
        "  raph.faxme  ",
    ],
)
def test_the_subject_rule_survives_real_mail_clients(subject):
    """« Re: », « TR: », minuscules, ponctuation, texte en plus : tout doit passer."""
    assert mailbox.accept(make_message(subject=subject), make_book(), make_config())


@pytest.mark.parametrize("subject", ["coucou", "", None, "raphfax", "Réponse"])
def test_a_subject_without_the_keyword_is_not_printed(subject):
    with pytest.raises(mailbox.MissingKeyword):
        mailbox.accept(make_message(subject=subject), make_book(), make_config())


def test_a_forgotten_keyword_is_distinguished_from_an_intrusion():
    """Un oubli mérite une explication, une intrusion n'en mérite aucune."""
    forgotten = make_message(subject="coucou")
    with pytest.raises(mailbox.MissingKeyword):
        mailbox.accept(forgotten, make_book(), make_config())
    intruder = make_message(sender="pub@spam.example", subject="RAPH.FAXME")
    with pytest.raises(Rejected) as caught:
        mailbox.accept(intruder, make_book(), make_config())
    assert not isinstance(caught.value, mailbox.MissingKeyword)


def test_the_keyword_can_be_switched_off():
    config = make_config()
    config = replace(config, mail=replace(config.mail, subject_keyword=""))
    assert mailbox.accept(make_message(subject="coucou"), make_book(), config)


@pytest.mark.parametrize(
    "header, value",
    [("Auto-Submitted", "auto-replied"), ("Precedence", "bulk"),
     ("List-Id", "<liste.example.com>")],
)
def test_automated_mail_is_never_answered(header, value):
    message = make_message(subject="coucou")
    message[header] = value
    assert mailbox.looks_automated(message)


def test_authentication_can_be_switched_off_only_explicitly():
    config = make_config()
    config = replace(config, mail=replace(config.mail, require_authentication=False))
    assert mailbox.accept(make_message(auth=None), make_book(), config)


def test_outgoing_mail_carries_the_letter_and_asks_for_a_reply():
    import numpy as np

    ink = np.zeros((200, 576), dtype=bool)
    ink[10:14, :] = True
    contact = make_book().by_name("Mamie")
    message = mailbox.build_outgoing(ink, contact, make_config(), "Raphaël")
    assert message["To"] == "mamie@example.com"
    assert "Raphaël" in message["Subject"]
    # Le mot-clé est dans l'objet : la réponse de Mamie, en « Re: … », passera
    # la règle sans qu'elle ait à y penser.
    assert mailbox.subject_matches(message, make_config().mail.subject_keyword)
    attachments = [p for p in message.walk() if p.get_filename()]
    assert [p.get_content_type() for p in attachments] == ["image/png"]
    assert "Réponds à ce message" in message.get_body(preferencelist=("plain",)).get_content()
