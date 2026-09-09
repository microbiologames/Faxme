# Faxme — courrier papier entre enfants, sans écran

## 0. Le cadre du prototype (décidé)

- **Deux boîtes** : à la maison, et chez le meilleur copain, dont les parents sont partants.
  Le matériel prévoit **5 destinataires** dès le départ, pour n'avoir à rien rouvrir ensuite.
- **Un enfant de 7 ans** de chaque côté. Un seul destinataire par boîte.
- **Aucune conservation des lettres.** Ni album, ni archive parentale. Les images sont
  détruites une fois imprimées ; ce qui reste, ce sont les tickets papier. La
  surveillance parentale se fait sur le papier, comme pour n'importe quel courrier.

Ces trois choix ferment beaucoup de portes, et c'est tant mieux : ils rendent le
prototype plus simple, pas moins.

## 1. L'idée en une phrase

Deux boîtes posées dans deux maisons. Un enfant glisse une lettre écrite à la main,
appuie sur un bouton, la lettre est numérisée et part. Chez l'autre enfant une lumière
s'allume : il appuie, la lettre sort imprimée. Rien d'autre n'est possible.

## 2. Principes de conception (non négociables)

Ces principes tranchent la plupart des décisions techniques qui suivent. Quand un
arbitrage est douteux, c'est eux qui décident.

1. **Aucun écran, jamais.** Ni pour l'enfant, ni comme solution de repli en cas d'erreur.
2. **Un seul usage.** L'objet ne sait faire qu'une chose. Pas de mode caché, pas de
   navigateur, pas de son autre que ceux du courrier.
3. **Le papier est le média.** Ce qui entre est du papier, ce qui sort est du papier.
   Le numérique n'est qu'un tuyau entre les deux, invisible — et il ne garde rien.
4. **Les destinataires sont un carnet fermé**, configuré par les parents. Aucune
   découverte, aucun ajout depuis l'appareil, aucune façon d'atteindre quelqu'un d'autre.
5. **Défaillance silencieuse interdite.** Sans écran, l'objet doit toujours dire son
   état par la lumière et le son. Une lettre perdue sans que personne ne le sache est
   le pire échec possible.
6. **L'attente fait partie du plaisir.** On ne cherche pas l'instantané. Le rituel
   (écrire, glisser, attendre, aller relever le courrier) est la valeur du produit.
7. **Un objet posé chez quelqu'un d'autre doit se dépanner sans nous.** Tout ce qui
   oblige à traverser la ville tuera le projet en trois semaines (§9).

## 3. Le parcours de l'enfant

**Envoyer**
1. Il écrit ou dessine sur une fiche A6 pré-imprimée, avec le feutre de la boîte (§4.1).
2. Il glisse la fiche dans la fente, contre les butées (position garantie, pas
   d'alignement à réussir).
3. Il tourne la **roue** sur la photo du copain à qui il écrit.
4. Il appuie sur **ENVOYER**. La boîte fait un bruit de traitement pendant le scan,
   puis un son de départ quand la lettre est partie. Le voyant « il a lu ta lettre »
   s'éteint : elle est en chemin.
5. Plus tard, ce voyant se rallume avec un petit ding : le copain l'a imprimée.

**Recevoir**
1. La cloche sonne.
2. Le voyant **TU AS DU COURRIER** reste allumé tant qu'il reste des lettres non
   imprimées.
3. L'enfant appuie sur **IMPRIMER** : une lettre sort. S'il en reste, le voyant reste
   allumé. Il rappuie.

Deux boutons, une roue, et un tableau de voyants qui se lisent sans rien décoder (§4.4).

## 4. Les décisions structurantes

### 4.1 Format papier, écriture et impression

**Choix : impression thermique 80 mm, fiches A6 pré-imprimées, feutre fourni.**

L'imprimante thermique est la seule technologie qui tienne les principes : pas de
consommable liquide, pas de séchage, pas de pilote, démarrage instantané, rouleau à
2 € qui dure des mois. En contrepartie elle impose une largeur.

| Papier thermique | Largeur imprimable | Points (203 dpi) | Réduction depuis A5 | Réduction depuis A6 |
|---|---|---|---|---|
| 58 mm | ~48 mm | 384 | ×0,32 | ×0,46 |
| **80 mm** | **~72 mm** | **576** | ×0,49 | **×0,69** |

**Le calcul refait pour 7 ans.** En CE1 on écrit en Seyès 2,5–3 mm : hauteur des
minuscules ~3 mm, ~9 mm avec les hampes. Réduites de A6 vers 72 mm (×0,69), les
minuscules font **~2 mm** sur le ticket. C'est petit mais franchement lisible — le
corps de texte d'un journal fait 1,4 à 1,7 mm. Ce n'est donc **pas la taille qui pose
problème, c'est l'épaisseur du trait** : un stylo bille fin (0,3 mm) tombe à 0,2 mm,
soit 2 points d'imprimante, avec des ruptures de trait après binarisation.

D'où trois décisions liées, qui sont du design produit autant que de la technique :

- **On fournit le feutre.** Un feutre noir pointe moyenne (~0,7–1 mm), jamais de
  crayon à papier (gris, il scanne mal et disparaît à la binarisation), jamais de
  stylo bille clair. Le « feutre officiel du fax » attaché à la boîte par une
  ficelle : c'est un objet désirable pour un enfant *et* la garantie du contraste.
- **Les fiches sont pré-imprimées** avec un interligne large (~8 mm) et une zone de
  dessin. La fiche enseigne le format : écrire gros n'est pas une consigne à répéter,
  c'est une contrainte du papier.
- **Le pipeline épaissit le trait** d'un point après binarisation (dilatation
  morphologique 1 px). Gratuit, et ça sauve les traits fins.

Reste à **valider en phase 0 avec l'écriture réelle** de ton fils. Si c'est trop
serré, le repli est la fiche A7 (74 × 105 mm), imprimée quasiment à l'échelle 1:1.

Deux points pratiques :
- **Papier thermique sans phénol** (ni BPA ni BPS). Les enfants vont manipuler ces
  tickets tous les jours, les plier, les garder sous l'oreiller.
- **Le thermique s'efface** en quelques mois à quelques années (chaleur, lumière,
  frottement). Sans archive, c'est assumé : une lettre est une chose qui passe. Si un
  ticket doit vraiment survivre, une photo prise par un parent avec son téléphone
  fait le travail, hors du système.

### 4.2 Capture : caméra fixe, pas de scanner

**Choix : caméra fixe sur potence, avec butées papier et éclairage LED intégré.**

| | Scanner USB à plat | Caméra fixe |
|---|---|---|
| Qualité | Excellente, éclairage maîtrisé | Bonne si l'éclairage est intégré |
| Vitesse | 10–25 s | < 1 s |
| Pièces mobiles | Oui (panne n° 1 à terme) | Aucune |
| Encombrement | Impose un objet plat et large | Boîtier compact vertical |
| Logiciel | `scanimage`, trivial | picamera2 + traitement d'image |
| Coût | 30–60 € d'occasion | ~35 € (Camera Module 3) |

Le scanner gagne sur le logiciel, la caméra gagne sur tout le reste — et surtout sur
l'ergonomie : glisser une fiche et appuyer, c'est instantané. On paie ça par un
pipeline image à écrire, mais c'est du travail fait une fois.

**L'astuce qui simplifie tout : la géométrie est fixe.** Butées mécaniques + caméra
vissée = la fiche est toujours au même endroit dans l'image. On supprime la détection
de contour, la correction de perspective adaptative, le recadrage automatique. Un
recadrage constant calibré une fois suffit. C'est 80 % de la vision par ordinateur en
moins, et c'est ce qui rend le projet faisable en quelques week-ends.

Prendre la **Camera Module 3 (autofocus)** plutôt qu'une caméra à focale fixe : elle
évite tout le réglage mécanique fin de la distance de mise au point.

**Pipeline image** (une fiche → un raster prêt à imprimer) :

```
capture RAW
  → recadrage fixe (calibré à l'installation)
  → niveaux de gris
  → normalisation d'éclairage (division par un flou gaussien large)
  → binarisation adaptative (Sauvola) — PAS de tramage Floyd-Steinberg
  → dilatation 1 px (épaissit le trait de feutre)
  → redressement fin (±3°) + recadrage sur la boîte d'encre
  → redimensionnement à 576 px de large
  → raster ESC/POS
```

Le point contre-intuitif : **surtout pas de tramage.** Le tramage est fait pour les
photos ; sur du trait de feutre il produit une bouillie grise, consomme de l'énergie
thermique et ralentit l'impression. On veut du noir et blanc franc.

### 4.3 Transport : Tailscale, pas de serveur

| Option | Infra à maintenir | Hors-ligne | Ajout d'un 3ᵉ appareil | Dépendance |
|---|---|---|---|---|
| Serveur relais (VPS) | Oui, un VPS + un service | Géré par le serveur | Trivial | Toi, à vie |
| **Tailscale + HTTP direct** | **Aucune** | File d'attente côté émetteur | Facile | Tailscale |
| MQTT | Un broker | Bonne (QoS 1) | Facile | Broker |
| E-mail / IMAP | Aucune | Excellente | Facile | Fournisseur mail |

**Choix : Tailscale + un petit endpoint HTTP sur chaque appareil.** Zéro
infrastructure, zéro coût récurrent, chiffré de bout en bout, traverse les box sans
ouvrir de port — et, argument décisif ici, **c'est aussi ton canal d'administration
sur la boîte installée chez le copain**, sans rien demander à ses parents et sans
toucher à leur réseau.

La disponibilité se règle côté émetteur : la lettre part dans une **file locale
persistante** et est réessayée jusqu'à acquittement. Si la boîte d'en face est
éteinte, la lettre attend sur disque et part quand elle se rallume.

### 4.4 Le tableau de bord : un voyant par idée, gravé en clair

**Choix : un voyant dédié par information, avec son symbole et son texte gravés à
côté. Aucune signification portée par une couleur ou un rythme de clignotement.**

C'est le bon principe et il mérite d'être énoncé comme tel : **l'information est
portée par l'endroit où la lumière s'allume, pas par sa couleur ni son rythme.** Un
code temporel (« rouge deux fois vite = plus de papier ») demande de se souvenir d'une
table ; un voyant à côté du mot *PAPIER* ne demande rien. Ça coûte quelques LED et
quelques broches — c'est-à-dire rien — et ça supprime la seule vraie difficulté
d'ergonomie du projet. La couleur ne sert plus qu'à hiérarchiser (tout en blanc chaud,
sauf l'alerte en rouge), donc elle peut être ignorée sans rien perdre : bon pour un
enfant de 7 ans comme pour un daltonien.

Corollaire : **on grave le texte, pas seulement le pictogramme.** À 7 ans on lit. Un
mot est moins ambigu qu'un dessin.

#### Le panneau

```
   ┌──────────────────────────────────────────────────────┐
   │                                                      │
   │   ● TU AS DU COURRIER          ○○○○○ TES LETTRES     │
   │                                       DU JOUR        │
   │   ● PLUS DE PAPIER                                   │
   │                                                      │
   │   ● APPELLE UN ADULTE   (rouge)                      │
   │                                                      │
   │   ┌────────────────┐                                 │
   │   │   ( roue )     │   ● IL A LU TA LETTRE           │
   │   │  Léo  ·  ·  ·  │                                 │
   │   └────────────────┘                                 │
   │                                                      │
   │      [ ENVOYER ]              [ IMPRIMER ]           │
   └──────────────────────────────────────────────────────┘
```

**La disposition fait partie du message.** Le voyant « il a lu ta lettre » est collé à
la roue, parce que c'est le seul qui dépend du destinataire sélectionné ; les autres
sont groupés à part, parce qu'ils parlent de la boîte. Un enfant ne lira jamais cette
règle, mais il l'apprendra en deux jours parce que la lumière est au bon endroit.

| Voyant | Allumé veut dire | Portée |
|---|---|---|
| **TU AS DU COURRIER** | il reste au moins une lettre non imprimée | toute la boîte |
| **IL A LU TA LETTRE** | le copain choisi sur la roue n'a plus aucune de tes lettres en attente | destinataire sélectionné |
| **TES LETTRES DU JOUR** | 5 points : ce qu'il te reste à envoyer aujourd'hui | toute la boîte |
| **PLUS DE PAPIER** | le rouleau est vide ou presque | toute la boîte |
| **APPELLE UN ADULTE** | tout le reste (réseau, panne) — le détail est sur la page web | toute la boîte |

#### Trois ajustements par rapport à ta liste

1. **Le crédit devient une jauge, pas une alarme.** Plutôt qu'un voyant « plus de
   courrier disponible » qui ne s'allume qu'au moment du refus, cinq petits points qui
   s'éteignent un par un. L'enfant voit son budget fondre, il apprend à le gérer, et
   surtout il n'est jamais surpris — le refus sec au 6ᵉ envoi, sans prévenir, est la
   frustration la plus facile à éviter du projet. Ça coûte quatre LED.
2. **« Plus de papier » sort de « appelle un adulte ».** Ce sera 80 % des incidents,
   c'est réparable en cinq secondes, et ça ne mérite pas de sortir un téléphone —
   surtout chez le copain. Condition : choisir une imprimante qui **remonte l'état du
   papier** en ESC/POS (`DLE EOT`, presque toutes les vraies 80 mm le font, beaucoup de
   modules bas de gamme non). À mettre dans les critères d'achat.
3. **« Il a lu ta lettre » est un état, pas un événement.** Ta formulation « la boîte
   de réception du destinataire est clear ou pas » est meilleure que « le dernier
   courrier a été lu » : elle ne demande pas de se souvenir de quel message on parle,
   elle marche si on envoie trois lettres d'affilée, et elle se recalcule toute seule
   après un redémarrage. Donc : **éteint = au moins une de mes lettres attend chez lui ;
   allumé = il a tout imprimé.** Au repos (rien envoyé depuis des jours) il est allumé,
   ce qui est vrai et rassurant. Ça demande une petite extension du protocole (§6.1).

#### Les sons

| Son | Quand | Caractère |
|---|---|---|
| Traitement | pendant le scan et l'envoi | tic-tic mécanique discret, façon vieux fax |
| Départ | la lettre est acceptée par la boîte d'en face | souffle court |
| Lecture | le copain vient d'imprimer ta lettre | ding léger, en même temps que le voyant |
| **Arrivée** | une lettre arrive | **cloche franche, audible d'une autre pièce** |

J'en propose quatre là où tu en demandais trois : je sépare *départ* et *lecture*,
parce que ce sont deux moments distincts et que la lecture est la récompense
émotionnelle de tout le système. Elle a besoin d'un son, pas seulement d'une lumière
qu'on ne regarde pas au bon moment.

Une règle et un détail matériel :
- **La cloche d'arrivée doit être incomparable au reste.** Les trois autres sons sont
  des confirmations discrètes, à portée de main. Une vraie cloche frappée par un
  solénoïde 5 V (~3 €) fait de l'arrivée du courrier un événement dans la maison ; un
  buzzer fait de la boîte un appareil électroménager.
- **Un bouton de volume physique** (potentiomètre) sur le côté. Chez le copain, ses
  parents doivent pouvoir baisser la cloche un soir sans te téléphoner. C'est le genre
  de détail qui décide si l'objet reste branché.

En mode nuit, tous les sons sont coupés et les voyants passent en très faible
intensité — une boîte qui éclaire une chambre à 22 h finit dans un placard.

### 4.5 La roue de sélection : oui, et c'est plus simple qu'un bouton

**Choix : un commutateur rotatif 5 positions, une position = un porte-photo.**

C'est faisable, c'est peu cher, et c'est le composant le plus adapté du projet.

| | Encodeur rotatif (sans fin) | **Commutateur rotatif 5 positions** |
|---|---|---|
| Position | relative : le logiciel doit se souvenir | **absolue : le bouton pointe, c'est tout** |
| Après un redémarrage | position perdue, il faut la réafficher | inchangée, physiquement vraie |
| Retour visuel | il faut une LED par position | le repère gravé suffit |
| Câblage | 2 broches | 5 broches (le Pi en a de reste) |
| Prix | ~2 € | ~3–5 € |

L'encodeur sans fin est le piège classique : sans écran, un sélecteur dont la position
n'est pas lisible sur l'objet lui-même est ingérable. Le commutateur rotatif est
**absolu** — la flèche du bouton pointe sur la photo de Léo, donc le destinataire est
Léo, y compris après une coupure de courant, y compris pour un adulte qui n'a jamais
vu la boîte. Zéro état logiciel, zéro ambiguïté.

Câblage : commun au 3,3 V, une broche GPIO par position avec résistance de tirage. Le
logiciel lit la position à chaque appui sur ENVOYER — c'est tout.

**Chaque position est une fente porte-photo**, pas une gravure : on y glisse une petite
photo du copain (ou son portrait dessiné par ton fils). Les quatre positions libres
restent visiblement libres, et c'est une promesse formidable pour un enfant de 7 ans :
*il y a de la place pour quatre autres copains*. Le jour où une boîte s'ajoute, on
glisse une photo, on ajoute une clé dans la configuration, et c'est fini — pas de
boîtier à rouvrir.

Règle sur une position vide : ENVOYER répond par la note « non », rien d'autre. Ce
n'est pas une panne, donc le voyant rouge ne s'allume pas.

Détail à ne pas oublier côté logiciel : le destinataire est figé **au moment de l'appui**
sur ENVOYER. Tourner la roue pendant qu'une lettre part ne change rien à sa destination,
et met simplement à jour le voyant « il a lu ta lettre » pour le nouveau copain choisi.

## 5. Architecture logicielle

```
┌─────────────────── Boîte A (Raspberry Pi) ───────────────────┐
│                                                              │
│  roue + 2 boutons ──► ui (gpiozero) ──┬──► 8 voyants         │
│                                       └──► cloche + sons     │
│                                  │                           │
│  caméra ──────► capture ──► pipeline image ──► outbox/       │
│                                                  │           │
│                                            sender (retry)    │
│                                                  │           │
│  ┌───────────────────────────────────────────────┼────────┐  │
│  │  état : SQLite (messages, quotas, pending/pair)│        │  │
│  └───────────────────────────────────────────────┼────────┘  │
│                                                  ▼           │
│  imprimante ◄── printer (ESC/POS) ◄── inbox/ ◄── receiver    │
│       │            │                              (HTTP)     │
│       │            └──► purge (§6.2)                         │
│       └──► état papier (DLE EOT) ──► voyant PLUS DE PAPIER   │
│                                                              │
│  config web (LAN + tailnet, parents) ────────────────────────┤
└──────────────────────────────────┬───────────────────────────┘
                                   │ Tailscale (chiffré)
                                   ▼
                          ┌──── Boîte B ────┐
```

**Pile** : Raspberry Pi OS Lite, Python 3, `picamera2`, `numpy`/`opencv`,
`python-escpos`, `gpiozero`, `FastAPI`, SQLite, services `systemd` avec
`Restart=always` et watchdog matériel.

Deux processus : `faxme-ui` (boutons, LED, son, caméra, impression) et `faxme-net`
(endpoint HTTP + file d'envoi), qui communiquent par SQLite et les répertoires.
Le réseau peut planter sans figer les boutons, et inversement.

## 6. Protocole, données et rétention

### 6.1 Un message
```
messages/<uuid>/
  meta.json     {"id","from","to","created_at","checksum"}
  page-1.png    1 bit, 576 px de large  (~20–40 Ko)
  state         queued | sent | delivered | printed | failed
```

Trois verbes réseau :
```
POST /v1/letter    multipart (meta.json + page-1.png)
                   en-têtes X-Faxme-Device + X-Faxme-Signature (HMAC clé partagée)
                   → 202 {"id": ..., "status": "queued"}
POST /v1/receipt   ← le destinataire signale l'IMPRESSION
                   → allume « IL A LU TA LETTRE », joue le ding
POST /v1/pending   ← le destinataire pousse son compteur à chaque changement
                   {"from": "<moi>", "pending": 2}
GET  /v1/pending   → filet de sécurité : l'émetteur interroge toutes les 5 min,
                     au cas où une notification se serait perdue
```

C'est `pending` qui fait vivre le voyant « il a lu ta lettre » : la boîte du copain est
la seule à savoir combien de mes lettres attendent encore chez elle, et elle le dit à
chaque arrivée et à chaque impression. Le sondage périodique évite le pire cas — un
voyant éteint pour toujours à cause d'un paquet perdu.

Trois propriétés à ne pas négocier :
- **Idempotence par UUID** : un réessai ne doit jamais imprimer deux fois la même lettre.
- **Authentification par clé d'appareil** même à l'intérieur du tailnet : personne ne
  doit pouvoir faire cracher du papier chez un enfant en tapant une URL.
- **Acquittement à l'impression, pas à la réception.** « Livré » veut dire « sorti sur
  papier ». C'est ce qui rend le retour émotionnellement juste.

### 6.2 Rétention : rien ne se garde

La place disque n'a jamais été le sujet (5 lettres/jour pendant 2 ans ≈ 100 Mo). Le
sujet est qu'on ne veut pas d'un dossier d'images de la correspondance de deux enfants
qui traîne sur deux Raspberry Pi. Donc :

| Où | Ce qu'on garde | Jusqu'à quand |
|---|---|---|
| Émetteur | l'image envoyée | jusqu'à l'accusé d'impression, puis **effacée** |
| Destinataire | l'image reçue | jusqu'à l'impression réussie, puis **effacée** |
| Destinataire | la **dernière** lettre imprimée | 24 h max, uniquement pour la réimpression |
| Les deux | journal technique | horodatage, id, taille, statut — **jamais d'image** |
| Les deux | jamais | rien d'autre |

La seule vraie conséquence de la rétention zéro : **on ne peut pas réimprimer une
lettre qu'on a effacée.** C'est pour ça qu'on ne supprime qu'après une impression
*réussie* (rouleau vide ou coupure de courant en plein ticket = la lettre reste dans
l'inbox et ressortira), et qu'on garde la dernière 24 h derrière un appui long, pour le
cas « le ticket est sorti mais il s'est déchiré / le chien l'a mangé ». Deux
suppressions de plus que nécessaire valent mieux qu'une lettre perdue, l'inverse
n'est pas vrai.

Purge au démarrage aussi : un redémarrage ne doit pas ressusciter d'anciens fichiers.

## 7. Garde-fous

### 7.1 Quota
Cinq envois par jour, remis à zéro à 4 h, affichés en permanence par la jauge à cinq
points (§4.4). Dépassement = le bouton ENVOYER répond par une note descendante, la
jauge est déjà à zéro depuis le dernier envoi : aucune surprise, aucune lettre perdue.

La **réception et l'impression ne sont jamais bloquées par le quota** — sinon on punit
un enfant pour ce que l'autre a fait.

La pile de fiches A6 est un second quota, physique, plus pédagogique que le premier.

### 7.2 Mode nuit
Plage configurable (défaut 20 h – 7 h) : bouton d'envoi inerte avec un retour sonore
« non », cloche coupée, impression différée. Les lettres arrivées la nuit sortent au
premier appui après 7 h.

### 7.3 Côté parents
Une page web accessible **uniquement depuis le LAN et depuis le tailnet** : réseau
Wi-Fi, appairage, quota, horaires, calibration de la caméra, test d'impression,
journal technique. **Pas de galerie, pas d'images, pas d'archive** — la page ne sait
littéralement pas afficher une lettre. La surveillance parentale, c'est lire les
tickets sur la table.

## 8. Nomenclature et budget (par boîte, indicatif)

| Poste | Choix | € |
|---|---|---|
| Calculateur | Raspberry Pi 4 (2 Go) ou Zero 2 W | 40–60 |
| Caméra | Camera Module 3 (autofocus) + nappe | 35 |
| Imprimante | Thermique 80 mm ESC/POS USB, **avec capteur de papier** | 55–90 |
| Boutons | 2 arcade 30 mm à LED (ENVOYER / IMPRIMER) | 10 |
| Sélecteur | Commutateur rotatif 5 positions + bouton flèche | 5 |
| Voyants | 8 LED (courrier, lu, 5 crédits, papier) + rouge alerte | 6 |
| Son | Solénoïde + cloche, ampli, potentiomètre de volume | 15–25 |
| Éclairage | Bandeau LED blanc + diffuseur | 8 |
| Alimentation | **PSU dédiée pour l'imprimante** + PSU Pi | 20 |
| Boîtier | Bois/contreplaqué, découpe simple | 15–30 |
| Divers | Papier sans phénol, feutres, fiches, porte-photos, câbles | 25 |
| | **Total** | **~230–320 € / boîte** |

**Le piège classique, à traiter dès le jour 1 :** une imprimante thermique tire des
pointes de plusieurs ampères pendant l'impression. Alimentée depuis le Pi ou depuis la
même petite alimentation, elle le fait redémarrer au milieu d'une lettre — panne
intermittente très pénible à diagnostiquer. **Alimentation séparée pour l'imprimante,
masses reliées, dès le premier montage sur table.**

## 9. La boîte chez le copain : la vraie difficulté

Ce n'est pas un détail d'installation, c'est la contrainte qui décide si le projet
survit à l'hiver. Une boîte chez quelqu'un d'autre, c'est : leur Wi-Fi, leur prise,
leur patience, et zéro accès physique pour toi.

**Ce qu'il faut prévoir, par ordre d'importance :**

1. **Le repli Wi-Fi.** Si le Pi ne rejoint aucun réseau connu en 3 minutes, il ouvre
   son propre point d'accès `faxme-setup` avec une page unique où un parent saisit le
   nouveau mot de passe depuis son téléphone. C'est un écran, mais pour l'adulte, une
   fois. Sans ça, un simple changement de box t'oblige à traverser la ville — et à la
   deuxième fois, le projet meurt.
2. **Deux réseaux enregistrés** dès l'installation : leur Wi-Fi *et* le partage de
   connexion de ton téléphone. Tu peux dépanner en te garant devant chez eux.
3. **Le rouleau se change sans outil**, capot à clapet, en cinq secondes. Laisse cinq
   rouleaux d'avance dans la boîte le jour de l'installation.
4. **Rien à faire au quotidien.** Pas de bouton à tenir appuyé, pas de redémarrage
   rituel. Ça se branche et ça vit. Watchdog matériel + `Restart=always`.
5. **Le risque non technique** : l'asymétrie. Si le copain répond peu, ton fils reçoit
   une boîte muette. Aucune solution logicielle à ça — juste à savoir avant de se
   lancer, et à en parler avec leurs parents comme d'un engagement partagé.

Option à garder en tête si leur réseau devient un problème récurrent : une clé 4G avec
une SIM IoT (~3–5 €/mois) rend la boîte totalement indépendante de leur box. Trop tôt
pour le prototype, mais c'est la sortie de secours.

## 10. Feuille de route

Chaque phase est utilisable et testable en vrai. On ne passe à la suivante qu'une fois
la précédente stable pendant quelques jours.

- **Phase 0 — La boucle locale** (1 week-end). Un seul Pi, caméra + imprimante, un
  bouton : on scanne, on imprime sur sa propre imprimante. Aucun réseau. But : valider
  le pipeline image, le format de fiche et le feutre **en faisant écrire ton fils pour
  de vrai**. C'est la phase qui décide de tout le reste — si le ticket n'est pas beau
  et lisible, rien d'autre ne compte, et ça se voit ici.
- **Phase 1 — Deux boîtes sur le même réseau** (1 week-end). Envoi/réception HTTP en
  LAN, file persistante, idempotence, purge après impression. On les met dans deux
  pièces de la maison : c'est déjà un jouet formidable, et le meilleur banc de test.
- **Phase 2 — Deux maisons** (1 week-end). Tailscale, réessais, LEDs et cloche,
  accusé de réception à l'impression, repli Wi-Fi en point d'accès.
- **Phase 3 — Les garde-fous et le tableau de bord** (1 week-end). Les 8 voyants, la
  roue, les 4 sons, quotas et jauge de crédits, mode nuit, page de configuration
  parents, journal technique.
- **Phase 4 — L'objet** (le plus long). Boîtier, fiches et feutre, démarrage
  automatique, watchdog, résistance au débranchement sauvage, mise à jour à distance.

## 11. Modes de panne à traiter explicitement

| Panne | Réponse attendue |
|---|---|
| Boîte d'en face éteinte | La lettre attend dans l'outbox et part au réveil. « Il a lu ta lettre » reste éteint, aucune alerte. |
| Réseau coupé | APPELLE UN ADULTE + détail sur la page web. Envois mis en file, tout repart seul. |
| Wi-Fi du copain changé | Point d'accès `faxme-setup` après 3 min (§9). |
| Plus de papier | Voyant PLUS DE PAPIER. La lettre **reste non imprimée** dans l'inbox. |
| Capture ratée (fiche de travers, doigt devant) | Appui long sur le bouton d'envoi = annuler la dernière lettre tant qu'elle n'est pas livrée. |
| Ticket sorti puis déchiré/perdu | Appui long sur le bouton d'impression = réimprimer la dernière (24 h). |
| Coupure de courant en pleine impression | La lettre reste marquée non imprimée : elle ressortira. Mieux vaut imprimer deux fois que perdre. |
| Roue sur une position vide | Note « non » à l'appui sur ENVOYER. Ce n'est pas une panne. |
| Fente vide ou fiche blanche | Détecté à la capture : note « non », ni envoi ni crédit consommé. |
| Le Pi ne redémarre pas | Watchdog matériel + `Restart=always`. Un objet du quotidien ne se répare pas au clavier. |
