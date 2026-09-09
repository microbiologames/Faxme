# Faxme

Du courrier papier entre enfants, sans écran.

Deux boîtes dans deux maisons. Un enfant glisse une lettre écrite à la main dans la
fente, tourne la roue sur la photo de son copain et appuie sur un bouton : la lettre
est numérisée et envoyée. Chez le copain, une cloche sonne et un voyant s'allume ; il
appuie, la lettre sort imprimée sur papier.

Pas d'écran, pas de compte, pas de clavier, pas d'autre usage possible. Les
destinataires sont un carnet fermé configuré par les parents. Rien n'est conservé :
une fois imprimée, la lettre n'existe plus que sur le ticket.

## État

**Phase 0 — la boucle locale.** Le traitement d'image, la génération des fiches,
l'aperçu à taille réelle, le pilote d'imprimante thermique et la boucle bouton du
Raspberry Pi sont écrits et testés. Rien n'est encore mis en réseau.

```bash
pip install -e .
faxme fiches -o sortie/fiches-a6.pdf        # les fiches A6 à imprimer
faxme simuler -o sortie/photo.png           # une fausse fiche, sans matériel
faxme -c exemple-boite.toml rendre sortie/photo.png -o sortie --etapes
```

Puis imprimer `sortie/ticket-taille-reelle.pdf` à 100 % : c'est le ticket à sa taille
physique réelle, à juger avant d'acheter quoi que ce soit.

## Documentation

- **[CONCEPT.md](CONCEPT.md)** — le projet : principes, arbitrages techniques et leurs
  raisons, protocole réseau, tableau de bord lumineux, matériel, budget, feuille de
  route, modes de panne.
- **[docs/PHASE0.md](docs/PHASE0.md)** — le mode d'emploi de ce qui est écrit, et le
  protocole d'essai avec du vrai papier.
