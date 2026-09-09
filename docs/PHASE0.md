# Phase 0 — la boucle locale

> Une fiche entre, un ticket sort. Aucun réseau, aucun destinataire.

Le but de cette phase n'est pas de faire marcher un fax, c'est de **répondre à une
seule question** : est-ce que l'écriture d'un enfant de 7 ans, réduite à 72 mm de
large et imprimée en thermique, est belle et lisible ? Si la réponse est non, le
format change, et tout le reste attend. Si elle est oui, on peut acheter la deuxième
boîte l'esprit tranquille.

Tout ce qui suit tourne **sur un PC, sans matériel**, sauf les deux dernières
sections. Tu peux donc juger le rendu avant même d'avoir commandé l'imprimante.

## Installation

```bash
pip install -e .          # numpy + pillow, c'est tout
pip install -e '.[dev]'   # + pytest
```

Sur le Raspberry Pi seulement, pour la caméra et le bouton :

```bash
pip install -e '.[pi]'    # picamera2 + gpiozero
```

Volontairement **pas d'OpenCV** : numpy et Pillow font tout ce dont on a besoin, en
quelques secondes d'installation au lieu de quelques centaines de mégaoctets.

## 1. Imprimer les fiches

```bash
faxme fiches -o sortie/fiches-a6.pdf
```

Quatre fiches A6 sur une A4, à découper en quatre. **À imprimer en couleur, à 100 %.**

La réglure, le cadre et la mention « POUR » sont dans un orange dont la composante
rouge est saturée. Le pipeline ne lisant que le canal rouge, ces repères sont
strictement invisibles à la numérisation : l'enfant est guidé, le destinataire ne
reçoit que l'écriture.

> **Le feutre doit être noir ou bleu foncé.** Un feutre rouge ou orange disparaîtrait
> exactement comme la réglure. C'est aussi pour ça qu'on fournit le stylo.

## 2. Rendre un ticket

Sans matériel, à partir d'une simple photo de fiche prise au téléphone :

```bash
faxme -c exemple-boite.toml rendre photo.jpg -o sortie --etapes
```

Quatre fichiers dans `sortie/` :

| Fichier | À quoi ça sert |
|---|---|
| `ticket.png` | le raster exact envoyé à l'imprimante, 576 points de large |
| `apercu-rouleau.png` | le ticket posé sur son rouleau de 80 mm, à l'échelle |
| **`ticket-taille-reelle.pdf`** | **à imprimer sur une imprimante ordinaire pour juger en vrai** |
| `etapes.png` | les 8 étapes du traitement côte à côte, pour diagnostiquer |
| `mesures.json` | les mesures, en machine |

Le PDF est le plus important : imprimé **à 100 %, sans « ajuster à la page »**, il
place le ticket à sa taille physique exacte. La réglette de 50 mm imprimée à côté sert
à vérifier que le pilote d'impression ne t'a pas menti. Tu tiens alors dans la main ce
que la thermique produira, à la texture du papier près.

## 3. Lire les mesures

```
  redressement    : -2.0°
  taille ticket   : 72.1 × 35.2 mm
  couverture      : 6.4 % du ticket
  épaisseur trait : 4 points (0.5 mm)
  ✓ épaisseur de trait dans la bonne plage (2 à 6 points).
```

**L'épaisseur du trait est la mesure qui décide.** Ce qui casse à l'impression
thermique n'est pas la taille des lettres — 2 mm de hauteur restent lisibles, le corps
d'un journal fait 1,5 mm — mais la finesse du trait :

- **moins de 2 points** : le trait se casse, des morceaux de lettres manquent. Écrire
  plus gros, ou prendre un feutre à pointe plus large.
- **2 à 6 points** : la bonne plage.
- **plus de 6 points** : les boucles des *a*, des *e* et des *o* se bouchent. Feutre
  trop large pour la taille d'écriture.

Si le trait est trop fin, le pipeline l'épaissit tout seul jusqu'à 3 points — mais
c'est un rattrapage, pas une solution : mieux vaut changer de feutre.

## 4. Sans photo sous la main

Un simulateur fabrique une fausse fiche manuscrite, avec réglure orange, éclairage
inégal, fiche de travers et bruit de capteur :

```bash
faxme simuler -o sortie/photo.png --hauteur 3 --feutre 0.7 --angle 1.8
faxme -c exemple-boite.toml rendre sortie/photo.png -o sortie --etapes
```

`--hauteur` est la hauteur des minuscules en mm (3 mm ≈ Seyès de CE1), `--feutre` la
largeur du trait. C'est ce qui permet d'explorer les cas limites sans faire écrire
personne : essaie `--hauteur 1.5 --feutre 0.2` pour voir un enfant qui écrit trop petit.

## 5. Le protocole d'essai, avec du vrai papier

C'est la partie qui compte, et elle ne se simule pas.

1. Imprimer une planche de fiches, en couleur.
2. Faire écrire **une vraie lettre**, sans consigne particulière au début : on veut
   l'écriture spontanée, pas l'écriture appliquée du test.
3. Photographier la fiche bien à plat, sous une lumière quelconque.
4. `faxme rendre`, puis imprimer le PDF taille réelle.
5. **Le faire lire au destinataire prévu**, pas à un adulte. Un adulte compense sans
   s'en rendre compte.

Refaire avec trois ou quatre lettres différentes, dont une écrite vite et une écrite
petite. On décide sur cette base :

| Ce qu'on observe | Ce qu'on change |
|---|---|
| Lisible, trait entre 2 et 6 points | Rien. On passe à la phase 1. |
| Trait trop fin de façon répétée | Feutre à pointe plus large. |
| Lettres trop petites malgré la réglure | Fiche A7 (74 × 105 mm), imprimée quasi 1:1. |
| Boucles bouchées | Feutre plus fin, ou interligne plus large. |
| Lignes de la fiche visibles sur le ticket | L'imprimante couleur ne sature pas le rouge : refaire les fiches, ou passer en `gray_channel = "luma"` avec du papier vierge. |

## 6. Sur le Pi : calibrer puis boucler

**Calibration du recadrage**, une seule fois, caméra vissée et butées en place :

```bash
faxme calibrer photo-de-la-fiche.jpg -o sortie/calibration.png
```

Une grille graduée est superposée à la photo. On relève les bords de la fiche et on
les reporte dans le TOML. **Viser l'intérieur du papier, pas son bord** : quelques
millimètres de table dans le cadre deviendraient le plus gros trait de la lettre.

**La boucle** — bouton, caméra, imprimante, rien d'autre :

```bash
faxme -c boite.toml boucle --peripherique /dev/usb/lp0 --bouton 17
```

Un appui : la fiche est numérisée, traitée et imprimée sur place. Comptez de deux à
quatre secondes sur un Pi 4.

Pour tester l'imprimante sans la boucle :

```bash
faxme -c boite.toml imprimer photo.jpg -p /dev/usb/lp0
faxme -c boite.toml imprimer photo.jpg --vers-fichier sortie/flux.escpos  # sans imprimante
```

## Ce que la phase 0 ne fait pas

Pas de réseau, pas de destinataire, pas de quota, pas de voyants, pas de mode nuit,
pas de rétention. Tout ça arrive en phase 1 et suivantes (cf. `CONCEPT.md` §11). La
seule chose que la phase 0 doit prouver, c'est que le ticket est beau.

## Tests

```bash
python -m pytest -q
```

Les tests de bout en bout passent par le simulateur : ils vérifient notamment que la
réglure orange n'atteint jamais le ticket, qu'une fiche vierge est refusée au lieu de
sortir en tempête de points, et que deux lettres de longueurs différentes sortent à la
même échelle.
