"""Ligne de commande de la phase 0.

Tout ce qui suit se lance depuis un PC, sans aucun matériel, sauf ``imprimer``
et ``boucle`` qui demandent l'imprimante et le Pi.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from PIL import Image

import os

from . import cards, escpos, pipeline, service, simulate, ticket
from .capture import open_source
from .config import Config
from .contacts import AddressBook
from .imaging import EmptyCard
from .mailbox import Gateway
from .store import Store


def _load_config(args) -> Config:
    config = Config.load(args.config)
    if getattr(args, "expediteur", None):
        config = replace(config, ticket=replace(config.ticket, sender=args.expediteur))
    if getattr(args, "cadrage", None):
        config = replace(config, pipeline=replace(config.pipeline, fit=args.cadrage))
    return config


def _report(stats: dict, config: Config) -> None:
    dots = stats["stroke_dots"]
    lecture = "canal rouge (fiche réglée)" if stats["channel"] == "red" else "luminance (feuille blanche)"
    rendu = "tramage (dessin colorié)" if stats["mode"] == "dessin" else "trait franc"
    print(f"  lecture         : {lecture}")
    print(f"  rendu           : {rendu}")
    print(f"  redressement    : {stats['angle_deg']:+.1f}°")
    print(f"  taille ticket   : {stats['width_mm']} × {stats['length_mm']} mm")
    print(f"  couverture      : {stats['ink_ratio'] * 100:.1f} % du ticket")
    print(f"  épaisseur trait : {dots:.0f} points ({stats['stroke_mm']} mm)")
    if stats["mode"] == "dessin":
        print("  (l'épaisseur de trait ne veut pas dire grand-chose sur un dessin tramé.)")
    elif dots < 2:
        print("  ⚠  moins de 2 points : le trait va se casser à l'impression.")
        print("     Écrire plus gros, ou prendre un feutre à pointe plus large.")
    elif dots > 6:
        print("  ⚠  trait très épais : les lettres risquent de se boucher.")
    else:
        print("  ✓ épaisseur de trait dans la bonne plage (2 à 6 points).")


def cmd_rendre(args) -> int:
    config = _load_config(args)
    out = Path(args.sortie)
    out.mkdir(parents=True, exist_ok=True)

    photo = open_source(args.photo, config).grab()
    try:
        result = pipeline.process(photo, config, keep_stages=args.etapes)
    except EmptyCard as error:
        print(f"fiche refusée : {error}", file=sys.stderr)
        return 2

    full = ticket.render(result.ink, config, when=datetime.now())

    ticket.to_image(full).save(out / "ticket.png")
    ticket.paper_preview(full, config).save(out / "apercu-rouleau.png")
    ticket.true_size_page(full, config).save(out / "ticket-taille-reelle.pdf",
                                             resolution=300.0)
    if args.etapes:
        pipeline.contact_sheet(result.stages).save(out / "etapes.png")
    (out / "mesures.json").write_text(
        json.dumps(result.stats, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"ticket écrit dans {out}/")
    _report(result.stats, config)
    print(f"\n  → imprime {out}/ticket-taille-reelle.pdf à 100 % pour juger en vrai.")
    return 0


def cmd_simuler(args) -> int:
    config = Config.load(args.config)
    if args.dessin:
        photo = simulate.fake_drawing(config, seed=args.graine, angle_deg=args.angle)
    else:
        photo = simulate.fake_photo(
            config,
            x_height_mm=args.hauteur,
            pen_mm=args.feutre,
            angle_deg=args.angle,
            seed=args.graine,
            text=args.texte.split("|") if args.texte else None,
        )
    Path(args.sortie).parent.mkdir(parents=True, exist_ok=True)
    photo.save(args.sortie)
    crop = simulate.crop_for(config, args.angle)
    print(f"photo simulée : {args.sortie}  ({photo.width}×{photo.height})")
    print("recadrage correspondant, à mettre dans le TOML :")
    print(f"  [capture]\n  crop = [{', '.join(f'{v:.4f}' for v in crop)}]")
    return 0


def cmd_fiches(args) -> int:
    config = Config.load(args.config)
    page = cards.sheet(config, dpi=args.dpi, blank=args.vierges)
    out = Path(args.sortie)
    out.parent.mkdir(parents=True, exist_ok=True)
    page.save(out, resolution=float(args.dpi))
    print(f"planche de 4 fiches A6 : {out}")
    if args.vierges:
        print("imprimer à 100 %, puis couper en quatre.")
    else:
        print("imprimer à 100 %, EN COULEUR, puis couper en quatre.")
    return 0


def cmd_imprimer(args) -> int:
    config = _load_config(args)
    photo = open_source(args.photo, config).grab()
    try:
        result = pipeline.process(photo, config)
    except EmptyCard as error:
        print(f"fiche refusée : {error}", file=sys.stderr)
        return 2
    full = ticket.render(result.ink, config, when=datetime.now())
    if args.vers_fichier:
        Path(args.vers_fichier).write_bytes(
            escpos.ticket_bytes(full, config.ticket.feed_lines)
        )
        print(f"flux ESC/POS écrit dans {args.vers_fichier}")
        return 0
    written = escpos.send(full, args.peripherique, config.ticket.feed_lines)
    print(f"{written} octets envoyés à {args.peripherique}")
    _report(result.stats, config)
    return 0


def cmd_calibrer(args) -> int:
    """Superpose une grille sur une photo pour lire les valeurs de recadrage."""
    from PIL import ImageDraw

    config = Config.load(args.config)
    photo = open_source(args.photo, config).grab()
    draw = ImageDraw.Draw(photo)
    w, h = photo.size
    for fraction in range(1, 20):
        x, y = w * fraction / 20, h * fraction / 20
        colour = (255, 0, 0) if fraction % 5 == 0 else (255, 160, 160)
        draw.line([x, 0, x, h], fill=colour)
        draw.line([0, y, w, y], fill=colour)
        if fraction % 5 == 0:
            draw.text((x + 4, 4), f"{fraction / 20:.2f}", fill=(255, 0, 0))
            draw.text((4, y + 4), f"{fraction / 20:.2f}", fill=(255, 0, 0))
    photo.save(args.sortie)
    print(f"grille écrite dans {args.sortie}")
    print("relève les bords de la fiche et reporte-les dans le TOML :")
    print("  [capture]\n  crop = [gauche, haut, droite, bas]")
    return 0


def cmd_boite(args) -> int:
    """Phase 1 sur le Pi : relève e-mail en tâche de fond + deux boutons."""
    from .box import run

    config = _load_config(args)
    gateway_password = os.environ.get(config.mail.password_env, "")
    if not gateway_password:
        raise SystemExit(f"exporte {config.mail.password_env} avant de démarrer")
    return run(
        config,
        data_dir=args.donnees,
        device=args.peripherique,
        password=gateway_password,
        send_pin=args.bouton_envoi,
        print_pin=args.bouton_impression,
        mail_pin=args.voyant_courrier,
        error_pin=args.voyant_erreur,
        default_contact=args.a,
    )


def cmd_boucle(args) -> int:
    """Phase 0 sur le Pi : bouton → caméra → pipeline → imprimante."""
    from .loopback import run

    return run(_load_config(args), device=args.peripherique, button_pin=args.bouton)


# --- passerelle e-mail -------------------------------------------------------


def _open_gateway(config: Config) -> Gateway:
    """Le mot de passe vient de l'environnement, jamais du fichier de config."""
    password = os.environ.get(config.mail.password_env, "")
    if not config.mail.address:
        raise SystemExit("aucune adresse configurée : renseigne [mail] address dans le TOML")
    if not password:
        raise SystemExit(
            f"mot de passe absent : exporte {config.mail.password_env} "
            "(mot de passe d'application Gmail, pas le mot de passe du compte)"
        )
    return Gateway(config, password)


def _open_store(args, config: Config) -> Store:
    return Store(args.donnees, config)


def cmd_relever(args) -> int:
    config = _load_config(args)
    store = _open_store(args, config)
    report = service.collect(store, config, _open_gateway(config))
    print(report)
    for reason in report.rejected:
        print(f"  refusé : {reason}")
    for name in report.accepted:
        print(f"  reçu de {name}")
    print(f"  en attente d'impression : {len(store.pending())}")
    return 0


def cmd_etat(args) -> int:
    config = _load_config(args)
    store = _open_store(args, config)
    waiting = store.pending()
    print(f"  courrier en attente : {len(waiting)}")
    for message in waiting:
        quand = message.created_at.strftime("%d/%m %Hh%M")
        print(f"    - de {message.contact}, {quand}, {message.pages} page(s)")
    print(f"  lettres restantes aujourd'hui : {store.credits_left()}"
          f" / {config.quota.daily_letters}")
    print(f"  mode nuit : {'oui' if store.is_night() else 'non'}")
    book = AddressBook(config.contacts)
    print(f"  carnet : {len(book)} contact(s)")
    for contact in book:
        roue = f", roue {contact.wheel}" if contact.wheel else ""
        print(f"    - {contact.name} ({contact.kind}) {contact.address}{roue}")
    return 0


def cmd_imprimer_attente(args) -> int:
    config = _load_config(args)
    store = _open_store(args, config)
    try:
        message = service.print_next(store, config, args.peripherique)
    except service.Sleeping as raison:
        print(raison)
        return 0
    if message is None:
        print("aucune lettre en attente")
        return 0
    print(f"imprimée : lettre de {message.contact}")
    print(f"  reste en attente : {len(store.pending())}")
    return 0


def cmd_envoyer(args) -> int:
    config = _load_config(args)
    store = _open_store(args, config)
    book = AddressBook(config.contacts)
    contact = book.by_name(args.a) or book.by_address(args.a)
    if contact is None:
        raise SystemExit(f"contact inconnu dans le carnet : {args.a}")

    photo = open_source(args.photo, config).grab()
    try:
        result = pipeline.process(photo, config)
    except EmptyCard as error:
        print(f"fiche refusée : {error}", file=sys.stderr)
        return 2
    full = ticket.render(result.ink, config, when=datetime.now())
    try:
        service.send_letter(store, config, _open_gateway(config), contact, full)
    except (service.QuotaExhausted, service.Sleeping) as raison:
        print(raison, file=sys.stderr)
        return 3
    print(f"lettre envoyée à {contact.name} ({contact.address})")
    print(f"  lettres restantes aujourd'hui : {store.credits_left()}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="faxme", description="Faxme — phase 0 : de la fiche au ticket."
    )
    parser.add_argument("-c", "--config", help="fichier TOML de la boîte")
    sub = parser.add_subparsers(dest="commande", required=True)

    p = sub.add_parser("rendre", help="photo de fiche → ticket + aperçus")
    p.add_argument("photo")
    p.add_argument("-o", "--sortie", default="sortie")
    p.add_argument("--etapes", action="store_true", help="planche de contrôle du pipeline")
    p.add_argument("--expediteur")
    p.add_argument("--cadrage", choices=("trim", "card", "ink"))
    p.set_defaults(func=cmd_rendre)

    p = sub.add_parser("simuler", help="fabrique une fausse photo de fiche")
    p.add_argument("-o", "--sortie", default="sortie/photo-simulee.png")
    p.add_argument("--hauteur", type=float, default=3.0, help="hauteur des minuscules en mm")
    p.add_argument("--feutre", type=float, default=0.7, help="largeur du trait en mm")
    p.add_argument("--angle", type=float, default=1.8)
    p.add_argument("--graine", type=int, default=7)
    p.add_argument("--texte", help="lignes séparées par des barres verticales")
    p.add_argument("--dessin", action="store_true",
                   help="un dessin d'enfant sur feuille blanche au lieu d'une lettre")
    p.set_defaults(func=cmd_simuler)

    p = sub.add_parser("fiches", help="planche de fiches A6 à imprimer")
    p.add_argument("-o", "--sortie", default="sortie/fiches-a6.pdf")
    p.add_argument("--dpi", type=int, default=300)
    p.add_argument("--vierges", action="store_true",
                   help="fiches blanches pour les dessins, sans rien d'imprimé")
    p.set_defaults(func=cmd_fiches)

    p = sub.add_parser("imprimer", help="photo de fiche → imprimante thermique")
    p.add_argument("photo")
    p.add_argument("-p", "--peripherique", default="/dev/usb/lp0")
    p.add_argument("--vers-fichier", help="écrit le flux ESC/POS au lieu d'imprimer")
    p.add_argument("--expediteur")
    p.add_argument("--cadrage", choices=("trim", "card", "ink"))
    p.set_defaults(func=cmd_imprimer)

    p = sub.add_parser("calibrer", help="grille de calibration du recadrage")
    p.add_argument("photo")
    p.add_argument("-o", "--sortie", default="sortie/calibration.png")
    p.set_defaults(func=cmd_calibrer)

    p = sub.add_parser("relever", help="relève la boîte e-mail et met en attente")
    p.add_argument("-d", "--donnees", default="var", help="répertoire d'état")
    p.set_defaults(func=cmd_relever)

    p = sub.add_parser("etat", help="courrier en attente, crédits, carnet")
    p.add_argument("-d", "--donnees", default="var")
    p.set_defaults(func=cmd_etat)

    p = sub.add_parser("imprimer-attente", help="imprime la lettre reçue la plus ancienne")
    p.add_argument("-d", "--donnees", default="var")
    p.add_argument("-p", "--peripherique", default="/dev/usb/lp0")
    p.set_defaults(func=cmd_imprimer_attente)

    p = sub.add_parser("envoyer", help="scanne une fiche et l'envoie à un contact")
    p.add_argument("photo")
    p.add_argument("--a", required=True, help="nom ou adresse du destinataire")
    p.add_argument("-d", "--donnees", default="var")
    p.add_argument("--expediteur")
    p.add_argument("--cadrage", choices=("trim", "card", "ink"))
    p.set_defaults(func=cmd_envoyer)

    p = sub.add_parser("boite", help="sur le Pi : service complet (e-mail + boutons)")
    p.add_argument("-d", "--donnees", default="var")
    p.add_argument("-p", "--peripherique", default="/dev/usb/lp0")
    p.add_argument("--bouton-envoi", type=int, default=17)
    p.add_argument("--bouton-impression", type=int, default=27)
    p.add_argument("--voyant-courrier", type=int, default=0)
    p.add_argument("--voyant-erreur", type=int, default=0)
    p.add_argument("--a", help="destinataire par défaut (la roue arrive en phase 4)")
    p.add_argument("--expediteur")
    p.add_argument("--cadrage", choices=("trim", "card", "ink"))
    p.set_defaults(func=cmd_boite)

    p = sub.add_parser("boucle", help="sur le Pi : bouton → scan → impression, sans réseau")
    p.add_argument("-p", "--peripherique", default="/dev/usb/lp0")
    p.add_argument("--bouton", type=int, default=17, help="broche GPIO du bouton")
    p.add_argument("--expediteur")
    p.add_argument("--cadrage", choices=("trim", "card", "ink"))
    p.set_defaults(func=cmd_boucle)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
