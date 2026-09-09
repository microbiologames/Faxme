import numpy as np
import pytest

from faxme import escpos, ticket
from faxme.config import Config


def a_letter(rows: int = 400) -> np.ndarray:
    ink = np.zeros((rows, 576), dtype=bool)
    ink[100:104, 50:500] = True
    return ink


def test_header_is_added_above_the_letter():
    config = Config()
    body = a_letter()
    full = ticket.render(body, config, sender="Nino")
    assert full.shape[1] == 576
    assert full.shape[0] > body.shape[0]
    # L'en-tête est de l'encre, en haut.
    assert full[: full.shape[0] - body.shape[0]].any()


def test_header_can_be_switched_off():
    from dataclasses import replace

    config = Config()
    config = replace(config, ticket=replace(config.ticket, header=False))
    body = a_letter()
    assert ticket.render(body, config).shape == body.shape


def test_narrow_letter_is_centred():
    narrow = np.zeros((50, 200), dtype=bool)
    narrow[:, :] = True
    padded = ticket._pad_to_width(narrow, 576)
    assert padded.shape[1] == 576
    assert not padded[0, 0] and padded[0, 288]


def test_french_date():
    from datetime import datetime

    assert ticket.french_date(datetime(2026, 9, 9, 20, 5)) == "mercredi 9 septembre · 20h05"


def test_raster_header_describes_the_image():
    ink = np.zeros((3, 16), dtype=bool)
    ink[0, 0] = True
    payload = escpos.raster(ink)
    assert payload[:4] == b"\x1dv0\x00"
    width_bytes = payload[4] | (payload[5] << 8)
    height = payload[6] | (payload[7] << 8)
    assert (width_bytes, height) == (2, 3)
    # Bit de poids fort du premier octet = premier point, noir.
    assert payload[8] == 0b10000000


def test_raster_pads_widths_that_are_not_multiples_of_eight():
    payload = escpos.raster(np.ones((2, 13), dtype=bool))
    assert (payload[4] | (payload[5] << 8)) == 2  # 13 bits arrondis à 16


def test_raster_is_split_into_bands():
    payload = escpos.raster(np.zeros((300, 8), dtype=bool), band_height=128)
    assert payload.count(b"\x1dv0\x00") == 3


def test_ticket_bytes_initialise_and_cut():
    payload = escpos.ticket_bytes(a_letter(20), feed_lines=4)
    assert payload.startswith(escpos.INIT)
    assert payload.endswith(escpos.partial_cut())
    assert escpos.feed(4) in payload
