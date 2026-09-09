"""D'où vient la photo : un fichier sur un PC, la caméra sur le Pi."""

from __future__ import annotations

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


def open_source(spec: str, config: Config) -> Source:
    """``camera`` pour la caméra du Pi, n'importe quel chemin pour un fichier."""
    if spec == "camera":
        return PiCameraSource(config)
    return FileSource(spec)
