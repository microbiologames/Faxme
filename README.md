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

**Phases 0 et 1 écrites.** Le traitement d'image (écriture et dessins), les fiches,
le pilote d'imprimante thermique, et la **passerelle e-mail** qui permet aux adultes
sans boîte — grands-parents, parent en déplacement — d'écrire depuis leur téléphone et
de recevoir les lettres de l'enfant. Une seule boîte est donc déjà utile. Le lien
direct entre deux boîtes arrive en phase 2.

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
- **[docs/PHASE0.md](docs/PHASE0.md)** — de la fiche au ticket : les fiches à imprimer,
  le rendu, et le protocole d'essai avec du vrai papier.
- **[docs/PHASE1.md](docs/PHASE1.md)** — la passerelle e-mail : la boîte Gmail, le
  carnet fermé, ce qu'on dit aux grands-parents, le service du Pi.
