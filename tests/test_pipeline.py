"""Tests de bout en bout, sur des photos fabriquées par le simulateur."""

import numpy as np
import pytest
from dataclasses import replace

from faxme import pipeline, simulate, ticket
from faxme.config import Config
from faxme.imaging import EmptyCard


def make_config(**pipeline_overrides) -> Config:
    config = Config()
    config = replace(config, capture=replace(config.capture, crop=simulate.crop_for(config)))
    if pipeline_overrides:
        config = replace(config, pipeline=replace(config.pipeline, **pipeline_overrides))
    return config


def test_a_letter_becomes_a_printable_ticket():
    config = make_config()
    result = pipeline.process(simulate.fake_photo(config), config)

    assert result.ink.shape[1] == config.printer.dots_per_line
    assert result.ink.dtype == bool
    # Redressement retrouvé à un demi-degré près.
    assert result.stats["angle_deg"] == pytest.approx(-1.8, abs=0.5)
    # Le ticket ne fait que la longueur de ce qui a été écrit.
    assert 25 < result.stats["length_mm"] < 60
    # Épaisseur de trait dans la plage imprimable.
    assert 2 <= result.stats["stroke_dots"] <= 6


def test_preprinted_guides_never_reach_the_ticket():
    """La réglure orange doit être invisible : une fiche vierge est vide."""
    config = make_config()
    blank = simulate.fake_photo(config, text=[])
    with pytest.raises(EmptyCard):
        pipeline.process(blank, config)


@pytest.mark.parametrize("sigma", [3.0, 10.0])
def test_a_blank_card_never_turns_into_snow(sigma):
    """Le bruit du capteur ne doit jamais passer pour de l'encre."""
    config = make_config()
    blank = np.asarray(simulate.fake_photo(config, text=[]), dtype=np.float32)
    noisy = np.random.default_rng(1).normal(0, sigma, blank.shape) + blank
    from PIL import Image

    with pytest.raises(EmptyCard):
        pipeline.process(
            Image.fromarray(np.clip(noisy, 0, 255).astype("uint8")), config
        )


def test_luma_channel_would_have_kept_the_guides():
    """Le contre-exemple : sans l'astuce du canal rouge, la réglure passe."""
    config = make_config()
    config = replace(config, capture=replace(config.capture, gray_channel="luma"))
    blank = simulate.fake_photo(config, text=[])
    result = pipeline.process(blank, config)
    assert result.stats["ink_ratio"] > 0.01  # les lignes sont bien là


def test_trim_keeps_the_scale_constant_between_letters():
    """Deux lettres de longueurs différentes doivent sortir à la même taille."""
    config = make_config()
    short = pipeline.process(simulate.fake_photo(config, text=["Coucou"]), config)
    long = pipeline.process(
        simulate.fake_photo(config, text=["Coucou", "ça va ?", "moi oui", "et toi ?"]),
        config,
    )
    assert short.stats["stroke_dots"] == pytest.approx(long.stats["stroke_dots"], abs=1)
    assert long.stats["length_mm"] > short.stats["length_mm"] * 1.5


def test_ink_fit_magnifies_a_short_letter():
    """Le mode 'ink' grossit, au prix d'une échelle qui varie : documenté, pas subi."""
    trimmed = make_config(fit="trim")
    zoomed = make_config(fit="ink")
    text = ["Coucou"]
    a = pipeline.process(simulate.fake_photo(trimmed, text=text), trimmed)
    b = pipeline.process(simulate.fake_photo(zoomed, text=text), zoomed)
    assert b.stats["stroke_dots"] > a.stats["stroke_dots"]


def test_tiny_handwriting_is_thickened_enough_to_print():
    """Un enfant qui écrit très petit produit un trait trop fin : on l'épaissit."""
    config = make_config()
    tiny = pipeline.process(
        simulate.fake_photo(config, x_height_mm=1.5, pen_mm=0.2), config
    )
    assert tiny.stats["stroke_dots"] >= config.pipeline.min_stroke_dots


def test_a_thick_felt_tip_is_left_alone():
    config = make_config()
    thick = pipeline.process(simulate.fake_photo(config, pen_mm=1.0), config)
    normal = pipeline.process(simulate.fake_photo(config, pen_mm=0.7), config)
    assert thick.stats["stroke_dots"] > normal.stats["stroke_dots"]


def test_stages_are_captured_only_on_demand():
    config = make_config()
    photo = simulate.fake_photo(config)
    assert pipeline.process(photo, config).stages == []
    stages = pipeline.process(photo, config, keep_stages=True).stages
    assert [stage.name for stage in stages][:3] == ["photo", "cadree", "gris"]
    pipeline.contact_sheet(stages)  # ne doit pas lever


def test_unknown_fit_is_refused():
    config = make_config(fit="plein")
    with pytest.raises(ValueError, match="fit"):
        pipeline.process(simulate.fake_photo(config), config)
