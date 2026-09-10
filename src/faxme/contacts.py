"""Le carnet d'adresses : un carnet fermé, écrit par les parents.

Il n'existe aucun moyen d'ajouter un correspondant depuis l'appareil. C'est
le principe n° 4 (CONCEPT.md §2) et c'est ce qui fait qu'une adresse e-mail
n'ouvre pas le système : tout ce qui n'est pas dans ce carnet est jeté.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Contact:
    name: str  # le nom imprimé sur le ticket. Jamais celui annoncé par le message.
    kind: str  # "email" ou "box"
    address: str = ""  # e-mail de l'adulte, ou nom Tailscale de la boîte
    alias: str = ""  # sous-adresse qui identifie ce contact à la réception
    wheel: int = 0  # position sur la roue, 0 = non attribué

    def __post_init__(self) -> None:
        if self.kind not in ("email", "box"):
            raise ValueError(f"contact {self.name!r} : kind doit valoir 'email' ou 'box'")
        if not self.address:
            raise ValueError(f"contact {self.name!r} : adresse manquante")

    @classmethod
    def from_dict(cls, entry: dict) -> "Contact":
        unknown = set(entry) - set(cls.__dataclass_fields__)
        if unknown:
            raise ValueError(f"contact : clés inconnues {sorted(unknown)}")
        return cls(**entry)


class AddressBook:
    """Recherche par adresse, par alias ou par position de roue."""

    def __init__(self, contacts: tuple[Contact, ...] | list[Contact]):
        self._contacts = tuple(contacts)
        seen_wheel = {}
        for contact in self._contacts:
            if contact.wheel:
                if contact.wheel in seen_wheel:
                    raise ValueError(
                        f"position de roue {contact.wheel} attribuée deux fois : "
                        f"{seen_wheel[contact.wheel]} et {contact.name}"
                    )
                seen_wheel[contact.wheel] = contact.name

    def __iter__(self):
        return iter(self._contacts)

    def __len__(self) -> int:
        return len(self._contacts)

    def by_address(self, address: str) -> Contact | None:
        """Un expéditeur autorisé, ou None. La comparaison ignore la casse."""
        wanted = (address or "").strip().lower()
        for contact in self._contacts:
            if contact.address.lower() == wanted:
                return contact
        return None

    def by_alias(self, alias: str) -> Contact | None:
        wanted = (alias or "").strip().lower()
        if not wanted:
            return None
        for contact in self._contacts:
            if contact.alias and contact.alias.lower() == wanted:
                return contact
        return None

    def by_wheel(self, position: int) -> Contact | None:
        for contact in self._contacts:
            if contact.wheel == position:
                return contact
        return None

    def by_name(self, name: str) -> Contact | None:
        wanted = (name or "").strip().lower()
        for contact in self._contacts:
            if contact.name.lower() == wanted:
                return contact
        return None
