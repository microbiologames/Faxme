"""D'où vient la photo : un fichier sur un PC, la caméra sur le Pi."""

from __future__ import annotations

import io
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageOps

from .config import Config


class Source:
    def grab(self) -> Image.Image:  # pragma: no cover - interface
        raise NotImplementedError

    def close(self) -> None:
        pass


class FileSource(Source):
    """Une image sur disque. C'est ce qui rend tout le pipeline testable sans matériel."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def grab(self) -> Image.Image:
        image = Image.open(self.path)
        # Respecte l'orientation EXIF des photos prises au téléphone.
        return ImageOps.exif_transpose(image).convert("RGB")


class PiCameraSource(Source):
    """La Camera Module 3 du Pi. Import protégé : picamera2 n'existe que là-bas."""

    def __init__(self, config: Config):
        try:
            from picamera2 import Picamera2
        except ImportError as error:  # pragma: no cover - dépend du matériel
            raise RuntimeError(
                "picamera2 est introuvable : cette source ne fonctionne que sur un "
                "Raspberry Pi (pip install 'faxme[pi]')."
            ) from error
        self._camera = Picamera2()
        self._camera.configure(
            self._camera.create_still_configuration(
                main={"size": tuple(config.capture.resolution)}
            )
        )
        self._camera.start()

    def grab(self) -> Image.Image:  # pragma: no cover - dépend du matériel
        return self._camera.capture_image("main").convert("RGB")

    def close(self) -> None:  # pragma: no cover - dépend du matériel
        self._camera.stop()


class ScannerSource(Source):
    """Un scanner à plat piloté par SANE (``scanimage``).

    Voie alternative à la caméra, mesurée comme ~5 fois moins coûteuse en
    calcul à qualité égale : l'éclairage est déjà plat et la géométrie exacte,
    donc l'image de travail peut être beaucoup plus petite. À réserver aux
    scanners **effectivement pilotables sous Linux** : un appareil qui se
    présente en clé USB, ou qui exige un logiciel Windows, ne peut pas être
    déclenché par un bouton d'enfant, quelle que soit sa résolution.

    Avec cette source, mettre dans le TOML :
    ``[capture] crop = [0, 0, 1, 1]`` et ``[pipeline] working_factor = 1.2``.
    """

    def __init__(self, config: Config, device: str = "", resolution: int = 200):
        if shutil.which("scanimage") is None:
            raise RuntimeError(
                "scanimage est introuvable (apt install sane-utils). "
                "Vérifier aussi que le scanner est reconnu : scanimage -L"
            )
        self.config = config
        self.device = device
        self.resolution = resolution

    def _command(self) -> list[str]:
        card = self.config.card
        command = ["scanimage", "--format=png", "--mode", "Color",
                   "--resolution", str(self.resolution)]
        if self.device:
            command += ["--device", self.device]
        # On ne numérise que la surface de la fiche : inutile de balayer une A4
        # entière pour une carte A6, c'est autant de secondes et de pixels.
        command += ["-x", str(card.width_mm), "-y", str(card.height_mm)]
        return command

    def grab(self) -> Image.Image:
        try:
            done = subprocess.run(self._command(), capture_output=True, timeout=120)
        except subprocess.TimeoutExpired as error:
            raise RuntimeError("le scanner n'a pas répondu en 2 minutes") from error
        if done.returncode != 0:
            raise RuntimeError(
                f"scanimage a échoué : {done.stderr.decode('utf-8', 'replace').strip()[:200]}"
            )
        return Image.open(io.BytesIO(done.stdout)).convert("RGB")


def open_source(spec: str, config: Config) -> Source:
    """``camera``, ``scanner`` (éventuellement ``scanner:<périphérique>``),
    ou n'importe quel chemin de fichier."""
    if spec == "camera":
        return PiCameraSource(config)
    if spec == "scanner" or spec.startswith("scanner:"):
        _, _, device = spec.partition(":")
        return ScannerSource(config, device=device)
    return FileSource(spec)
