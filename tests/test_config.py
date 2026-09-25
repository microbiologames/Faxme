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


def test_open_source_picks_the_right_backend(tmp_path, monkeypatch):
    """Un chemin, la caméra, ou le scanner — décidés par la même chaîne."""
    import shutil

    from faxme.capture import FileSource, ScannerSource, open_source
    from faxme.config import Config

    photo = tmp_path / "photo.png"
    from PIL import Image

    Image.new("RGB", (10, 10), "white").save(photo)
    assert isinstance(open_source(str(photo), Config()), FileSource)

    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/scanimage")
    source = open_source("scanner:genesys:libusb:001:005", Config())
    assert isinstance(source, ScannerSource)
    assert source.device == "genesys:libusb:001:005"
    command = source._command()
    # On ne balaie que la fiche, pas une A4 entière.
    assert command[command.index("-x") + 1] == "105.0"
    assert command[command.index("-y") + 1] == "148.0"


def test_a_scanner_without_sane_fails_clearly(monkeypatch):
    import shutil

    import pytest

    from faxme.capture import open_source
    from faxme.config import Config

    monkeypatch.setattr(shutil, "which", lambda name: None)
    with pytest.raises(RuntimeError, match="scanimage"):
        open_source("scanner", Config())
