import pytest

from faxme.config import Config


def test_defaults_are_coherent():
    config = Config()
    assert config.printer.dots_per_line == 576
    assert 71.5 < config.printer.width_mm < 72.5  # 72 mm imprimables
    # La résolution de travail doit rester au-dessus de celle du ticket.
    assert config.working_width == 1152
    assert config.working_px_per_mm > 10


def test_load_toml(tmp_path):
    path = tmp_path / "boite.toml"
    path.write_text(
        "[capture]\ncrop = [0.1, 0.2, 0.9, 0.8]\n\n[ticket]\nsender = 'Nino'\n",
        encoding="utf-8",
    )
    config = Config.load(path)
    assert config.capture.crop == (0.1, 0.2, 0.9, 0.8)
    assert config.ticket.sender == "Nino"
    assert config.printer.dots_per_line == 576  # le reste garde ses valeurs


def test_unknown_key_is_refused(tmp_path):
    path = tmp_path / "boite.toml"
    path.write_text("[ticket]\nexpediteur = 'Nino'\n", encoding="utf-8")
    with pytest.raises(ValueError, match="réglage inconnu"):
        Config.load(path)
