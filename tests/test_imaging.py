import numpy as np
import pytest
from PIL import Image

from faxme import imaging
from faxme.config import Config


def test_sauvola_survives_an_illumination_gradient():
    """Un seuil global échouerait ici : c'est tout l'intérêt de l'adaptatif."""
    gray = np.linspace(0.35, 1.0, 200, dtype=np.float32)[None, :].repeat(200, axis=0)
    gray[90:96, 20:180] *= 0.45  # un trait, partout moins clair que son fond
    ink = imaging.sauvola(gray, 21, 0.2)
    assert ink[92, 30] and ink[92, 170]  # détecté du côté sombre comme du clair
    assert not ink[10, 10] and not ink[10, 190]


def test_illumination_normalisation_flattens_a_gradient():
    gradient = np.linspace(0.3, 1.0, 300, dtype=np.float32)[None, :].repeat(300, axis=0)
    flat = imaging.normalize_illumination(gradient, radius_px=40)
    # Au centre, le dégradé disparaît complètement.
    assert flat[:, 60:-60].std() < 0.005
    # Sur les bords il en reste : le flou n'a rien à sa gauche pour estimer le
    # fond. C'est une des raisons d'être de pipeline.border_mm.
    assert flat.std() < gradient.std() / 5


@pytest.mark.parametrize("angle", [-2.5, -1.0, 1.5, 3.0])
def test_estimate_skew_finds_the_angle(angle):
    lines = np.zeros((400, 400), dtype=bool)
    for y in range(60, 340, 30):
        lines[y : y + 4, 60:340] = True
    tilted = np.asarray(
        Image.fromarray((lines * 255).astype(np.uint8)).rotate(
            -angle, resample=Image.Resampling.BILINEAR, fillcolor=0
        )
    ) > 127
    assert imaging.estimate_skew(tilted, max_deg=4.0) == pytest.approx(angle, abs=0.4)


def test_stroke_thickness_ignores_orientation():
    horizontal = np.zeros((60, 60), dtype=bool)
    horizontal[20:24, 10:50] = True
    vertical = np.zeros((60, 60), dtype=bool)
    vertical[10:50, 20:23] = True
    assert imaging.stroke_thickness(horizontal) == 4
    assert imaging.stroke_thickness(vertical) == 3


def test_clear_border_removes_the_paper_edge():
    ink = np.zeros((100, 100), dtype=bool)
    ink[:, 0:2] = True  # la découpe du papier
    ink[40:44, 30:70] = True  # de l'écriture
    cleaned = imaging.clear_border(ink, 5)
    assert not cleaned[:, 0:2].any()
    assert cleaned[40:44, 30:70].all()


def test_downsample_keeps_thin_strokes():
    """Un trait d'un pixel sur trois doit survivre à la réduction, pas disparaître."""
    ink = np.zeros((300, 1728), dtype=bool)
    for x in range(100, 1600, 60):
        ink[50:250, x : x + 3] = True
    reduced = imaging.downsample_ink(ink, 576)
    assert reduced.shape[1] == 576
    assert reduced.any(axis=0).sum() >= 20  # les traits sont toujours là


def test_thicken_only_when_needed():
    thin = np.zeros((80, 80), dtype=bool)
    thin[10:70, 40:41] = True
    thick = np.zeros((80, 80), dtype=bool)
    thick[10:70, 36:41] = True
    assert imaging.stroke_thickness(imaging.thicken_thin_strokes(thin, 3)) >= 3
    assert imaging.stroke_thickness(imaging.thicken_thin_strokes(thick, 3)) == 5


def test_gray_channel_is_validated():
    config = Config()
    object.__setattr__(config.capture, "gray_channel", "vert")
    with pytest.raises(ValueError, match="gray_channel"):
        imaging.to_working_gray(Image.new("RGB", (100, 140), "white"), config)
