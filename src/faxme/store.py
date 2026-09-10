"""L'état de la boîte : les lettres en transit, les quotas, la purge.

Trois choses seulement, mais ce sont celles qui doivent survivre à un
débranchement sauvage (CONCEPT.md §10.6) :

- une lettre reçue et pas encore imprimée **ne doit jamais disparaître** ;
- une lettre imprimée **doit disparaître**, c'est la rétention zéro (§6.2) ;
- une lettre ne doit jamais être imprimée deux fois par un simple redémarrage.

D'où SQLite en WAL avec ``synchronous=FULL`` pour l'état, et les images à
côté sur le disque. Le fichier est la donnée, la base est la vérité.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from PIL import Image

from .config import Config

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id          TEXT PRIMARY KEY,
    direction   TEXT NOT NULL,          -- 'in' (à imprimer) | 'out' (à envoyer)
    contact     TEXT NOT NULL,          -- le nom du carnet, jamais celui du message
    source      TEXT NOT NULL,          -- 'email' | 'box' | 'camera'
    created_at  TEXT NOT NULL,
    state       TEXT NOT NULL,          -- pending | printed | sent | failed
    settled_at  TEXT,
    pages       INTEGER NOT NULL DEFAULT 1,
    external_id TEXT                    -- identifiant côté source, pour l'idempotence
);
CREATE INDEX IF NOT EXISTS messages_state ON messages(state, direction);
CREATE UNIQUE INDEX IF NOT EXISTS messages_external
    ON messages(source, external_id) WHERE external_id IS NOT NULL;
"""


@dataclass(frozen=True)
class Message:
    id: str
    direction: str
    contact: str
    source: str
    created_at: datetime
    state: str
    pages: int
    directory: Path

    def page(self, number: int = 1) -> np.ndarray:
        """Charge une page comme masque booléen (True = encre)."""
        image = Image.open(self.directory / f"page-{number}.png").convert("L")
        return np.asarray(image) < 128


class Store:
    def __init__(self, root: str | Path, config: Config):
        self.root = Path(root)
        self.config = config
        self.messages_dir = self.root / "messages"
        self.messages_dir.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.root / "state.db", isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        # Une lettre ne doit jamais changer d'état à moitié.
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    # --- écriture ------------------------------------------------------------

    def add(
        self,
        *,
        direction: str,
        contact: str,
        source: str,
        pages: list[np.ndarray],
        external_id: str | None = None,
        created_at: datetime | None = None,
    ) -> Message | None:
        """Enregistre une lettre. Renvoie None si elle est déjà connue.

        L'idempotence par ``external_id`` est ce qui garantit qu'un e-mail
        relevé deux fois — parce que la suppression a échoué, parce que le Pi
        a redémarré au mauvais moment — n'est pas imprimé deux fois.
        """
        if not pages:
            raise ValueError("une lettre sans page")
        if external_id and self._known(source, external_id):
            return None

        message_id = str(uuid.uuid4())
        created_at = created_at or datetime.now()
        directory = self.messages_dir / message_id
        directory.mkdir(parents=True)
        for number, page in enumerate(pages, start=1):
            Image.fromarray(np.where(page, 0, 255).astype(np.uint8)).convert("1").save(
                directory / f"page-{number}.png"
            )
        (directory / "meta.json").write_text(
            json.dumps(
                {
                    "id": message_id,
                    "direction": direction,
                    "contact": contact,
                    "source": source,
                    "created_at": created_at.isoformat(timespec="seconds"),
                    "pages": len(pages),
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        try:
            self.db.execute(
                "INSERT INTO messages (id, direction, contact, source, created_at,"
                " state, pages, external_id) VALUES (?,?,?,?,?,?,?,?)",
                (
                    message_id,
                    direction,
                    contact,
                    source,
                    created_at.isoformat(timespec="seconds"),
                    "pending",
                    len(pages),
                    external_id,
                ),
            )
        except sqlite3.IntegrityError:
            # Course entre deux relèves : l'autre a gagné, on efface la copie.
            shutil.rmtree(directory, ignore_errors=True)
            return None
        return self._read(message_id)

    def settle(self, message_id: str, state: str, when: datetime | None = None) -> None:
        """Marque une lettre imprimée, envoyée ou en échec."""
        if state not in ("printed", "sent", "failed"):
            raise ValueError(f"état inattendu : {state!r}")
        self.db.execute(
            "UPDATE messages SET state = ?, settled_at = ? WHERE id = ?",
            (state, (when or datetime.now()).isoformat(timespec="seconds"), message_id),
        )

    # --- lecture -------------------------------------------------------------

    def pending(self, direction: str = "in") -> list[Message]:
        rows = self.db.execute(
            "SELECT * FROM messages WHERE state = 'pending' AND direction = ?"
            " ORDER BY created_at",
            (direction,),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    def next_to_print(self) -> Message | None:
        """La plus ancienne lettre reçue non imprimée. Le courrier se relève dans l'ordre."""
        waiting = self.pending("in")
        return waiting[0] if waiting else None

    def last_printed(self) -> Message | None:
        """Pour la réimpression après un ticket déchiré (CONCEPT.md §6.2)."""
        row = self.db.execute(
            "SELECT * FROM messages WHERE state = 'printed' AND direction = 'in'"
            " ORDER BY settled_at DESC LIMIT 1"
        ).fetchone()
        return self._from_row(row) if row and self._directory(row["id"]).exists() else None

    # --- quota et mode nuit --------------------------------------------------

    def quota_day(self, now: datetime) -> str:
        """Le jour de quota : il commence à l'heure de remise à zéro, pas à minuit."""
        return (now - timedelta(hours=self.config.quota.reset_hour)).date().isoformat()

    def sent_today(self, now: datetime | None = None) -> int:
        now = now or datetime.now()
        start = datetime.fromisoformat(self.quota_day(now)) + timedelta(
            hours=self.config.quota.reset_hour
        )
        row = self.db.execute(
            "SELECT COUNT(*) AS n FROM messages WHERE direction = 'out'"
            " AND created_at >= ?",
            (start.isoformat(timespec="seconds"),),
        ).fetchone()
        return int(row["n"])

    def credits_left(self, now: datetime | None = None) -> int:
        return max(0, self.config.quota.daily_letters - self.sent_today(now))

    def is_night(self, now: datetime | None = None) -> bool:
        now = now or datetime.now()
        start = self.config.quota.night_start_hour
        end = self.config.quota.night_end_hour
        if start == end:
            return False
        if start < end:
            return start <= now.hour < end
        return now.hour >= start or now.hour < end

    # --- purge ---------------------------------------------------------------

    def purge(self, now: datetime | None = None, keep_last_hours: int = 24) -> int:
        """Efface les images des lettres réglées. Rien ne se garde (§6.2).

        Seule exception : la dernière lettre imprimée reste disponible
        ``keep_last_hours`` heures, pour la réimprimer si le ticket s'est
        déchiré. La ligne de base, elle, demeure : c'est ce qui empêche une
        relève ultérieure de réimprimer une lettre déjà sortie.
        """
        now = now or datetime.now()
        spared = self.last_printed()
        spared_id = spared.id if spared else None
        removed = 0
        rows = self.db.execute(
            "SELECT id, state, settled_at FROM messages WHERE state != 'pending'"
        ).fetchall()
        for row in rows:
            directory = self._directory(row["id"])
            if not directory.exists():
                continue
            if row["id"] == spared_id and row["settled_at"]:
                age = now - datetime.fromisoformat(row["settled_at"])
                if age < timedelta(hours=keep_last_hours):
                    continue
            shutil.rmtree(directory, ignore_errors=True)
            removed += 1
        return removed

    # --- interne -------------------------------------------------------------

    def _directory(self, message_id: str) -> Path:
        return self.messages_dir / message_id

    def _known(self, source: str, external_id: str) -> bool:
        row = self.db.execute(
            "SELECT 1 FROM messages WHERE source = ? AND external_id = ?",
            (source, external_id),
        ).fetchone()
        return row is not None

    def _read(self, message_id: str) -> Message:
        row = self.db.execute(
            "SELECT * FROM messages WHERE id = ?", (message_id,)
        ).fetchone()
        return self._from_row(row)

    def _from_row(self, row: sqlite3.Row) -> Message:
        return Message(
            id=row["id"],
            direction=row["direction"],
            contact=row["contact"],
            source=row["source"],
            created_at=datetime.fromisoformat(row["created_at"]),
            state=row["state"],
            pages=row["pages"],
            directory=self._directory(row["id"]),
        )
