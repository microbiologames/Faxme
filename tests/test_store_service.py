"""Le magasin et les trois opérations qui l'utilisent."""

from dataclasses import replace
from datetime import datetime, timedelta

import numpy as np
import pytest

from faxme import service
from faxme.config import Config, MailConfig, QuotaConfig
from faxme.contacts import Contact
from faxme.service import QuotaExhausted, Sleeping
from faxme.store import Store
from tests.test_mailbox import make_book, make_config, make_message


class FakeGateway:
    """IMAP et SMTP en mémoire : toute la logique se teste hors ligne."""

    def __init__(self, messages=()):
        self.inbox = [(str(i).encode(), m) for i, m in enumerate(messages)]
        self.deleted: list[bytes] = []
        self.sent: list = []
        self.fail_send = False

    def fetch(self):
        return list(self.inbox)

    def delete(self, numbers):
        self.deleted.extend(numbers)

    def send(self, message):
        if self.fail_send:
            raise OSError("serveur injoignable")
        self.sent.append(message)


def a_page(rows: int = 200) -> np.ndarray:
    page = np.zeros((rows, 576), dtype=bool)
    page[10:14, 20:500] = True
    return page


def make_store(tmp_path, config=None) -> Store:
    return Store(tmp_path / "var", config or make_config())


# --- relève ------------------------------------------------------------------


def test_collect_stores_accepted_mail_and_clears_the_server(tmp_path):
    config = replace(make_config(), contacts=tuple(make_book()))
    store = make_store(tmp_path, config)
    gateway = FakeGateway([make_message(), make_message(sender="pub@spam.example")])

    report = service.collect(store, config, gateway)

    assert len(report.accepted) == 1 and len(report.rejected) == 1
    assert len(store.pending()) == 1
    assert store.pending()[0].contact == "Mamie"
    # Les deux sont retirés du serveur : le refusé aussi, sinon il revient sans fin.
    assert len(gateway.deleted) == 2


def test_the_same_mail_collected_twice_is_printed_once(tmp_path):
    config = replace(make_config(), contacts=tuple(make_book()))
    store = make_store(tmp_path, config)
    service.collect(store, config, FakeGateway([make_message()]))
    report = service.collect(store, config, FakeGateway([make_message()]))
    assert report.duplicates == 1
    assert len(store.pending()) == 1


def test_a_refused_mail_is_forwarded_to_the_parents(tmp_path):
    config = make_config()
    config = replace(
        config,
        contacts=tuple(make_book()),
        mail=replace(config.mail, forward_unknown_to="parents@example.com"),
    )
    store = make_store(tmp_path, config)
    gateway = FakeGateway([make_message(sender="pub@spam.example")])
    service.collect(store, config, gateway)
    assert len(store.pending()) == 0
    assert gateway.sent and gateway.sent[0]["To"] == "parents@example.com"


# --- impression --------------------------------------------------------------


def test_printing_settles_the_letter_and_purges_nothing_pending(tmp_path):
    config = make_config()
    store = make_store(tmp_path, config)
    store.add(direction="in", contact="Mamie", source="email", pages=[a_page()])
    store.add(direction="in", contact="Papa", source="email", pages=[a_page()])
    device = tmp_path / "imprimante.bin"

    printed = service.print_next(store, config, device, now=datetime(2026, 9, 10, 15))

    assert printed.contact == "Mamie"  # la plus ancienne d'abord
    assert device.read_bytes().startswith(b"\x1b@")
    assert len(store.pending()) == 1  # celle de Papa attend toujours
    assert store.pending()[0].directory.exists()


def test_nothing_prints_at_night(tmp_path):
    config = make_config()
    store = make_store(tmp_path, config)
    store.add(direction="in", contact="Mamie", source="email", pages=[a_page()])
    with pytest.raises(Sleeping):
        service.print_next(store, config, tmp_path / "p.bin", now=datetime(2026, 9, 10, 22))
    assert len(store.pending()) == 1  # rien n'est perdu


def test_printing_an_empty_box_is_not_an_error(tmp_path):
    config = make_config()
    store = make_store(tmp_path, config)
    assert service.print_next(store, config, tmp_path / "p.bin",
                              now=datetime(2026, 9, 10, 15)) is None


# --- envoi -------------------------------------------------------------------


def test_sending_consumes_a_credit_and_leaves_no_trace(tmp_path):
    config = replace(make_config(), contacts=tuple(make_book()))
    store = make_store(tmp_path, config)
    gateway = FakeGateway()
    contact = make_book().by_name("Mamie")
    now = datetime(2026, 9, 10, 15)

    before = store.credits_left(now)
    message = service.send_letter(store, config, gateway, contact, a_page(), now=now)

    assert len(gateway.sent) == 1
    assert store.credits_left(now) == before - 1
    # Rétention zéro : l'image n'existe plus une fois partie.
    assert not message.directory.exists()


def test_the_quota_refuses_the_sixth_letter(tmp_path):
    config = replace(make_config(), contacts=tuple(make_book()),
                     quota=replace(QuotaConfig(), daily_letters=2))
    store = make_store(tmp_path, config)
    gateway = FakeGateway()
    contact = make_book().by_name("Mamie")
    now = datetime(2026, 9, 10, 15)

    for _ in range(2):
        service.send_letter(store, config, gateway, contact, a_page(), now=now)
    with pytest.raises(QuotaExhausted):
        service.send_letter(store, config, gateway, contact, a_page(), now=now)
    assert len(gateway.sent) == 2


def test_the_quota_resets_after_the_reset_hour(tmp_path):
    config = replace(make_config(), contacts=tuple(make_book()),
                     quota=replace(QuotaConfig(), daily_letters=1))
    store = make_store(tmp_path, config)
    gateway = FakeGateway()
    contact = make_book().by_name("Mamie")

    service.send_letter(store, config, gateway, contact, a_page(),
                        now=datetime(2026, 9, 10, 19))
    # 2 h du matin, c'est encore la même journée de quota (remise à zéro à 4 h).
    assert store.credits_left(datetime(2026, 9, 11, 2)) == 0
    assert store.credits_left(datetime(2026, 9, 11, 9)) == 1


def test_a_failed_send_does_not_lose_the_letter_silently(tmp_path):
    config = replace(make_config(), contacts=tuple(make_book()))
    store = make_store(tmp_path, config)
    gateway = FakeGateway()
    gateway.fail_send = True
    with pytest.raises(OSError):
        service.send_letter(store, config, gateway, make_book().by_name("Mamie"),
                            a_page(), now=datetime(2026, 9, 10, 15))
    row = store.db.execute("SELECT state FROM messages").fetchone()
    assert row["state"] == "failed"


# --- purge -------------------------------------------------------------------


def test_the_last_printed_letter_survives_a_day_then_disappears(tmp_path):
    config = make_config()
    store = make_store(tmp_path, config)
    message = store.add(direction="in", contact="Mamie", source="email", pages=[a_page()])
    printed_at = datetime(2026, 9, 10, 15)
    store.settle(message.id, "printed", printed_at)

    store.purge(printed_at + timedelta(hours=2))
    assert message.directory.exists()  # réimprimable après un ticket déchiré

    store.purge(printed_at + timedelta(hours=25))
    assert not message.directory.exists()
    # La ligne demeure : c'est elle qui empêche une réimpression accidentelle.
    assert store.db.execute("SELECT COUNT(*) c FROM messages").fetchone()["c"] == 1


def test_a_restart_never_reprints_a_printed_letter(tmp_path):
    config = make_config()
    store = make_store(tmp_path, config)
    message = store.add(direction="in", contact="Mamie", source="email", pages=[a_page()])
    store.settle(message.id, "printed")
    store.close()

    again = Store(tmp_path / "var", config)
    assert again.next_to_print() is None
