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
   oblige à traverser la ville tuera le projet en trois semaines (§11).

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
- **Les fiches réglées sont pré-imprimées** avec un interligne large (~8 mm) — il
  existe aussi un papier blanc pour les dessins (§4.6). La fiche
  enseigne le format : écrire gros n'est pas une consigne à répéter, c'est une
  contrainte du papier. Toute cette réglure est imprimée **en orange clair à rouge
  saturé**, et le pipeline ne lit que le canal rouge de la photo : les lignes y
  apparaissent blanches et **ne partent donc jamais sur le ticket**, alors que le
  feutre noir ou bleu reste parfaitement noir. L'enfant est guidé, le destinataire ne
  reçoit que l'écriture. Contrepartie à assumer et à graver dans le marbre : **le
  feutre ne doit jamais être rouge ni orange**, il disparaîtrait exactement de la
  même façon.
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
  → rotation + recadrage fixe (calibré une fois à l'installation)
  → canal rouge  ← fait disparaître la réglure orange de la fiche
  → réduction à 2× la largeur du ticket (1152 px)
  → normalisation d'éclairage (division par un flou gaussien large)
  → binarisation adaptative de Sauvola — PAS de tramage Floyd-Steinberg
  → effacement d'une bande de 3 mm sur le pourtour  ← la découpe du papier
  → estimation puis correction de l'inclinaison (±4°), puis rebinarisation
  → rognage en hauteur sur l'écriture (l'échelle en largeur ne bouge pas)
  → réduction à 576 points, seuil bas pour ne pas perdre les traits fins
  → épaississement du trait, seulement s'il fait moins de 3 points
  → en-tête « DE NINO » + date, dessiné dans le même raster
  → raster ESC/POS (GS v 0)
```

Quatre points appris en écrivant ce code, et qui ne se devinaient pas :

- **Le bord du papier est le piège principal.** Sans l'effacement du pourtour, la
  découpe de la fiche devient le plus gros trait de l'image : elle capture le cadrage
  *et* fait échouer le redressement, dont le critère est alors dominé par cette barre
  noire. Trois millimètres suffisent, à condition de calibrer le recadrage **à
  l'intérieur** du papier et non sur son bord.
- **Rogner en largeur est une fausse bonne idée.** Recadrer sur l'écriture fait bien
  sortir des lettres plus grosses, mais l'échelle change alors d'une lettre à l'autre :
  trois mots deviennent une affiche. On rogne donc en hauteur seulement — le ticket ne
  fait que la longueur de ce qui a été écrit, et une minuscule fait toujours la même
  taille.
- **On n'épaissit le trait que s'il est trop fin.** Dilater systématiquement bouche les
  boucles des *a*, des *e* et des *o* dès qu'on écrit au feutre large. La dilatation
  est donc conditionnée à une mesure de l'épaisseur réelle.
- **Deux fois la résolution finale suffit.** Mesuré : passer de 3× à 2× divise le temps
  de traitement par trois sans changer l'épaisseur de trait, la longueur du ticket ni
  l'angle trouvé, y compris avec un trait fin.

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

### 4.6 Les dessins, et le deuxième papier

Un enfant de 7 ans écrit peu et dessine beaucoup. Un dessin n'est pas une lettre avec
des images : c'est un autre problème de rendu.

- **Une lettre** n'a que du noir et du blanc. Une binarisation franche est le bon
  traitement, et le tramage y ferait de la bouillie.
- **Un dessin colorié** a des aplats. Une binarisation franche les réduit à des taches
  noires ou les efface ; c'est là, et seulement là, que le tramage est le bon outil.

D'où **deux papiers et deux traitements** — mais aucun bouton pour choisir, parce qu'il
n'y a ni écran ni bouton libre pour ça. Tout se décide à la lecture de l'image :

| Papier | Reconnu à | Lecture | Rendu |
|---|---|---|---|
| Fiche réglée | sa bande orange en haut | canal rouge : la réglure disparaît | trait franc |
| Feuille blanche | l'absence de bande | luminance : toutes les couleurs comptent | tramage si aplats, trait sinon |

La bascule vers le tramage se fait en mesurant la surface de gris moyen : de l'écriture
au feutre n'en a presque pas, un ciel colorié en est presque entièrement fait.

Deux détails qui font la différence à l'impression :

- **Le noir franc reste noir.** On ne trame que les demi-teintes ; en dessous d'un
  certain gris, on imprime plein. Sans cette règle, le tramage réduit aussi les
  contours du dessin à un semis de points et la maison perd ses murs.
- **On éclaircit avant de tramer.** Une thermique surcharge : un aplat tramé à 50 %
  ressort presque noir. Un gamma de 0,72 remet les gris à leur place.

Et le grain assumé : un dessin d'enfant passé à la caméra puis à la thermique n'est pas
une reproduction fidèle, c'est une gravure. C'est très bien ainsi — c'est même une
partie du charme de l'objet, au même titre que le bruit d'un vieux fax.

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

## 7. Les adultes sans boîte : la passerelle e-mail

Une boîte ne sert à rien tant qu'il n'y en a pas deux — sauf si l'autre bout peut être
un adulte avec un téléphone. C'est ce que change cette passerelle, et elle change plus
que le confort : **elle rend une seule boîte utile**, donc elle permet de commencer
sans attendre l'accord d'une autre famille, et de découvrir si le rituel prend avant
d'installer du matériel chez quelqu'un.

Deux cas d'usage réels : le parent en déplacement long, et les grands-parents chez qui
on ne veut pas gérer une installation.

### 7.1 Il n'y a pas d'application à écrire

**L'application, c'est l'appareil photo et la messagerie du téléphone.** Rien à
installer, rien à maintenir, rien à publier sur un magasin, et surtout : ça marche pour
des grands-parents qui n'installeront jamais rien.

Mieux : on demande à l'adulte d'utiliser le **mode « numériser un document »** déjà
présent dans son téléphone (Notes ou Fichiers sur iPhone, Google Drive sur Android).
Il redresse la perspective tout seul. C'est la seule partie difficile du traitement
d'une photo prise à main levée, et elle est déjà écrite, gratuitement, par Apple et
Google. On ne la réécrira pas.

Une application maison pourrait venir plus tard pour le confort. Elle n'apporterait
aucune fonction nouvelle.

### 7.2 La passerelle tourne sur la boîte, pas sur un serveur

Le Pi relève une boîte aux lettres en IMAP toutes les minutes et envoie en SMTP. Pas
de serveur, pas d'hébergement, pas d'abonnement — la même logique que le choix de
Tailscale (§4.3). La boîte est allumée en permanence de toute façon (§10).

### 7.3 C'est la première ouverture du système : elle doit rester une meurtrière

Jusqu'ici, rien de l'extérieur ne pouvait atteindre l'enfant. Une adresse e-mail casse
cette propriété si on n'y prend pas garde. Quatre règles, toutes obligatoires :

1. **Liste blanche stricte**, configurée par les parents. Un expéditeur inconnu n'est
   pas imprimé, pas signalé, pas mis en attente : il est jeté. Au besoin réexpédié à
   l'adresse des parents, jamais au papier.
2. **Une adresse par adulte**, sous forme de sous-adresse : `raphael+mamie7fk3@…`.
   L'alias joue le rôle de secret partagé ; le connaître fait partie de
   l'authentification.
3. **Vérifier l'authentification du message.** Le champ `From:` d'un e-mail se falsifie
   en trois secondes. On lit l'en-tête `Authentication-Results` ajouté par le
   fournisseur et on n'accepte que si SPF et DKIM passent. Sans cette vérification,
   n'importe qui peut faire imprimer ce qu'il veut chez un enfant de 7 ans en écrivant
   « de la part de Mamie ».
4. **Le nom imprimé vient de la liste blanche, jamais du message.** Le ticket dit
   « DE MAMIE » parce que c'est ce que les parents ont écrit dans la configuration en
   face de cette adresse — pas parce que l'expéditeur s'est nommé ainsi.

### 7.4 Ce qu'un e-mail peut contenir

| Contenu | Traitement |
|---|---|
| Photo jointe (JPEG, PNG, HEIC) | même pipeline que la caméra, en luminance et en mode automatique |
| PDF joint | première page seulement — c'est ce que produisent les scanners de téléphone |
| Texte du corps | rendu dans une police manuscrite, pour que ça reste une lettre et pas un ticket de caisse |
| Objet, signature, citations | ignorés |

Limites à fixer dès le départ : trois pages par message au maximum, pièces jointes
au-delà d'une taille raisonnable refusées, tout le reste ignoré. Une boîte qui imprime
tout ce qu'on lui envoie est une imprimante à spam.

### 7.5 Dans l'autre sens

Une position de la roue peut être un adulte plutôt qu'une boîte. La lettre part alors
en e-mail, l'image en pièce jointe et affichée dans le corps du message, avec une
phrase qui entretient la boucle : *« Réponds à ce message, même juste avec un dessin,
Raphaël l'imprimera. »*

**Le voyant « IL A LU TA LETTRE » ne peut pas dire la vérité pour un e-mail.** Aucun
accusé de lecture fiable n'existe. Deux options, aucune parfaite : l'allumer à
l'acceptation du message par le serveur — ce qui veut dire « partie », pas « lue » —
ou attendre une réponse, au risque qu'il reste éteint des jours. Je prendrais la
première, en le sachant : à 7 ans, un voyant qui ne se rallume jamais est pire qu'un
voyant un peu optimiste.

### 7.6 Ce que ça coûte à la rétention zéro, et il faut le savoir

C'est le vrai prix de cette passerelle, et il ne se contourne pas.

Côté boîte, on peut tenir la règle : le message est **supprimé du serveur IMAP après
impression** (corbeille vidée comprise), et les envois ne sont pas enregistrés dans les
« messages envoyés ». Côté adulte, non : sa copie reste dans sa boîte aux lettres pour
toujours, et le message a transité par son fournisseur.

Autrement dit : **le chemin boîte-à-boîte reste privé et sans trace, le chemin e-mail
ne l'est pas.** C'est acceptable pour écrire à sa grand-mère, ça ne l'est pas comme
transport par défaut.

### 7.7 Pourquoi ne pas tout faire en e-mail

La tentation est réelle : un seul mécanisme, aucune infrastructure, une mise en file
d'attente naturelle quand l'autre bout est éteint, et l'ajout d'un correspondant se
réduit à une ligne de configuration. On pourrait supprimer Tailscale.

On ne le fait pas pour une raison : la correspondance de deux enfants de 7 ans serait
alors stockée indéfiniment chez un fournisseur de messagerie. C'est très exactement ce
que l'archivage local — refusé au §8.3 pour bien moins que ça — aurait fait. On perdrait
aussi le seul accusé de réception honnête du système, celui qui se déclenche à
l'impression réelle.

Donc **deux transports, un seul modèle de message.** Une lettre est un PNG et quelques
métadonnées, quel que soit le tuyau. Le code ne diffère qu'au dernier moment.

### 7.8 Ce qu'il faut choisir

- **Un fournisseur avec IMAP et sous-adressage.** Fastmail le fait nativement ;
  Gmail aussi, au prix d'un mot de passe d'application ou d'OAuth.
- **Une adresse dédiée par boîte**, qui ne sert qu'à ça et qui n'est jamais publiée
  ailleurs que dans la liste blanche.

## 8. Garde-fous

### 8.1 Quota
Cinq envois par jour, remis à zéro à 4 h, affichés en permanence par la jauge à cinq
points (§4.4). Dépassement = le bouton ENVOYER répond par une note descendante, la
jauge est déjà à zéro depuis le dernier envoi : aucune surprise, aucune lettre perdue.

La **réception et l'impression ne sont jamais bloquées par le quota** — sinon on punit
un enfant pour ce que l'autre a fait.

La pile de fiches A6 est un second quota, physique, plus pédagogique que le premier.

### 8.2 Mode nuit
Plage configurable (défaut 20 h – 7 h) : bouton d'envoi inerte avec un retour sonore
« non », cloche coupée, impression différée. Les lettres arrivées la nuit sortent au
premier appui après 7 h.

### 8.3 Côté parents
Une page web accessible **uniquement depuis le LAN et depuis le tailnet** : réseau
Wi-Fi, appairage, quota, horaires, calibration de la caméra, test d'impression,
journal technique. **Pas de galerie, pas d'images, pas d'archive** — la page ne sait
littéralement pas afficher une lettre. La surveillance parentale, c'est lire les
tickets sur la table.

## 9. Nomenclature et budget (par boîte, indicatif)

| Poste | Choix | € |
|---|---|---|
| Calculateur | Raspberry Pi 4 1 Go (déjà là) ou 2 Go, **sans ventilateur** | 0–60 |
| Refroidissement | Dissipateur passif ou boîtier alu radiateur | 8 |
| Caméra | Camera Module 3 (autofocus) + nappe | 35 |
| Imprimante | Thermique 80 mm ESC/POS USB, **avec capteur de papier** | 55–90 |
| Boutons | 2 arcade 30 mm à LED (ENVOYER / IMPRIMER) | 10 |
| Sélecteur | Commutateur rotatif 5 positions + bouton flèche | 5 |
| Voyants | 8 LED (courrier, lu, 5 crédits, papier) + rouge alerte | 6 |
| Son | Solénoïde + cloche, ampli, potentiomètre de volume | 15–25 |
| Éclairage | Bandeau LED blanc + diffuseur | 8 |
| Alimentation | **PSU dédiée pour l'imprimante** + PSU Pi officielle 3 A | 20 |
| Boîtier | Bois/contreplaqué, découpe simple | 15–30 |
| Divers | Papier sans phénol, feutres, fiches, porte-photos, câbles | 25 |
| | **Total** | **~230–320 € / boîte** |

**Le piège classique, à traiter dès le jour 1 :** une imprimante thermique tire des
pointes de plusieurs ampères pendant l'impression. Alimentée depuis le Pi ou depuis la
même petite alimentation, elle le fait redémarrer au milieu d'une lettre — panne
intermittente très pénible à diagnostiquer. **Alimentation séparée pour l'imprimante,
masses reliées, dès le premier montage sur table.**

## 10. Rester allumé : consommation, veille et fiabilité

**Choix : la boîte reste allumée en permanence. Pas de veille, pas de Wake-on-LAN.**

### 10.1 Sur un Raspberry Pi, la veille n'existe pas

Un Pi n'a pas d'état de sommeil au sens d'un portable : pas de suspend-to-RAM, pas de
S3. Il n'y a que deux états, allumé et éteint. **Le repos, c'est le ralenti** — et le
ralenti d'un Pi 4 sans écran est déjà très bas. « Mettre en veille » signifierait donc
couper l'alimentation et prévoir un circuit externe pour la rétablir, ce qui est un
autre projet.

### 10.2 Ce que ça coûte vraiment

| Poste | Puissance au repos | Sur un an |
|---|---|---|
| Pi 4 sans écran, Wi-Fi actif | ~3 W | 26 kWh |
| Imprimante thermique en veille | ~1 W | 9 kWh |
| Pertes des alimentations | ~1 W | 9 kWh |
| **Une boîte** | **~5 W** | **~44 kWh ≈ 9 €/an** |
| **Les deux boîtes** | ~10 W | **~18 €/an** |

À ~0,20 €/kWh. Un Pi Zero 2 W à la place du Pi 4 ferait économiser environ 2 W, soit
**~3,5 € par boîte et par an**. Un module RTC capable de couper puis rétablir
l'alimentation coûte 30 à 60 € pièce : il ne serait jamais amorti. Toute
l'optimisation en jeu vaut moins qu'un rouleau de papier par mois.

On peut gratter quelques dixièmes de watt en désactivant HDMI, Bluetooth et la LED
d'activité dans `config.txt`. C'est gratuit, donc autant le faire, mais ça ne change
pas la décision.

### 10.3 Pourquoi le Wake-on-LAN ne s'applique pas

Deux raisons, chacune suffisante :

1. **Le paquet magique ne traverse pas Internet.** Le WoL est une trame de diffusion de
   niveau 2 : elle ne circule que sur le réseau local. Pour réveiller la boîte du
   copain depuis chez toi, il faudrait un appareil **déjà allumé chez lui** pour
   relayer le réveil — c'est-à-dire exactement la chose qu'on cherchait à éviter.
2. **Le Raspberry Pi ne le supporte pas.** La carte réseau du Pi 4 n'implémente pas le
   WoL et n'est pas alimentée à l'arrêt ; en Wi-Fi, le WoWLAN n'est pas exploitable sur
   les puces des Pi. À vérifier en une commande sur ta carte : `ethtool eth0 | grep
   Wake` — il répondra `Supports Wake-on: d`, c'est-à-dire rien.

### 10.4 La vraie raison de ne pas dormir : la cloche

Même si le réveil marchait, il ne faudrait pas s'en servir. **Une boîte endormie ne
peut pas sonner.** Le courrier arriverait en silence et ne serait découvert que par
hasard, ou au prochain passage de l'enfant devant la boîte — c'est-à-dire que le cœur
du produit disparaîtrait pour économiser 3,50 € par an. Le délai de démarrage de 30 à
60 s que tu as mesuré n'est même pas le problème : le problème est qu'il n'y a personne
pour décider de démarrer.

C'est donc une question de produit, pas de watts. La boîte est un objet de la maison,
comme une lampe de couloir : elle est là, elle est prête, elle ne demande rien.

### 10.5 Quelle machine, puisque les Zero 2 W sont introuvables

**Le Pi 4 1 Go que tu as déjà est le bon choix, et sans ventilateur.**

- **1 Go suffit largement.** Le pipeline traite une image de 12 Mpx en niveaux de gris,
  soit ~12 Mo de tableau, quelques copies intermédiaires, sur un système sans interface
  graphique. On est très loin de la limite.
- **Aucun problème thermique**, à condition de respecter deux choses : un **dissipateur
  passif** (un boîtier alu qui fait radiateur est encore mieux) et **quelques fentes
  d'aération** dans le coffret bois. Le travail réel est une bouffée de 2 à 5 secondes
  de calcul toutes les quelques heures ; le reste du temps la carte est au ralenti,
  autour de 50 °C, très loin des 80 °C où elle commence à se brider. Ce qui tue un Pi
  sans ventilateur, c'est une charge continue dans une boîte hermétique — on n'a ni
  l'une ni l'autre.
- **Prends la même carte pour la deuxième boîte.** Deux Pi 4 identiques, c'est une
  seule image système, un seul jeu de scripts, un seul comportement à déboguer, et une
  carte SD interchangeable en cas de panne chez le copain. **L'homogénéité vaut
  beaucoup plus que l'optimisation** sur un parc de deux appareils.
- Note de dépendance : la Camera Module 3 et `picamera2` enferment le projet dans
  l'écosystème Raspberry Pi. C'est acceptable et assumé ; le jour où ce serait un
  problème, le repli est une webcam USB, au prix de l'autofocus.

### 10.6 Le vrai risque d'un objet allumé en permanence : la carte SD

Ce n'est pas la consommation, c'est la corruption. Un Pi débranché brutalement — et il
le sera, par une rallonge tirée, un ménage, un orage — finit par abîmer sa carte SD.
Sur la boîte du copain, ça veut dire un déplacement.

Trois mesures, dans l'ordre du rapport bénéfice/effort :

1. **Racine en lecture seule** (overlay `overlayfs`, activable par `raspi-config`), plus
   une petite partition inscriptible pour SQLite et les lettres en transit. Le système
   devient à peu près indestructible : un débranchement ne peut plus corrompre que la
   partition de données, qui est minuscule.
2. **SQLite en mode WAL avec `synchronous=FULL`** pour l'état des messages. Une lettre
   ne doit jamais changer d'état à moitié.
3. **Pas de swap**, journalisation en RAM (`log2ram` ou `Storage=volatile`). Moins
   d'écritures, plus de durée de vie.

### 10.7 Optionnel : couper l'imprimante entre deux impressions

Un MOSFET ou un petit relais piloté par le GPIO peut couper l'alimentation de
l'imprimante au repos et la rétablir avant impression — elle démarre instantanément.
Gain : ~1 W et un peu de chaleur en moins. Coût : une énumération USB à gérer à chaque
réveil, donc un mode de panne de plus.

À décider **après mesure**, en phase 0, avec un wattmètre sur la prise. Optimiser à
l'aveugle une consommation qu'on n'a pas mesurée est le meilleur moyen d'ajouter une
panne pour économiser un euro.

## 11. La boîte chez le copain : la vraie difficulté

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

## 12. Feuille de route

Chaque phase est utilisable et testable en vrai. On ne passe à la suivante qu'une fois
la précédente stable pendant quelques jours.

**La passerelle e-mail (§7) est passée devant la deuxième boîte**, et c'est un
changement d'ordre important : elle rend **une seule boîte utile toute seule**. On peut
donc mettre l'objet en service à la maison sans rien demander à personne, découvrir si
le rituel prend, et n'installer du matériel chez le copain qu'une fois qu'on sait que
ça vaut le coup. Elle exerce au passage tout le modèle de message — file d'attente,
bouton d'impression, mode nuit, quota — sans qu'il y ait deux appareils à déboguer en
même temps.

- **Phase 0 — La boucle locale.** ✅ *Logiciel écrit* (`src/faxme`, mode d'emploi dans
  `docs/PHASE0.md`) : pipeline trait et dessin, fiches réglées et papier blanc, aperçu
  à taille réelle, pilote ESC/POS, boucle bouton du Pi. Aucun réseau. Ce qui reste est
  la validation avec du vrai papier : un wattmètre sur la prise pour trancher §10.7, et
  un relevé de température après une heure boîtier fermé.
- **Phase 1 — La passerelle e-mail** *(une boîte devient utile)*. Relève IMAP, liste
  blanche et vérification SPF/DKIM, impression des photos et du texte, envoi SMTP vers
  les adultes, suppression après impression. Utilisable dès le premier week-end : papa
  en déplacement écrit, la boîte sonne à la maison.
- **Phase 2 — Deux boîtes sur le même réseau.** Envoi/réception HTTP en LAN, file
  persistante, idempotence, purge après impression. On les met dans deux pièces de la
  maison : c'est déjà un jouet formidable, et le meilleur banc de test.
- **Phase 3 — Deux maisons.** Tailscale, réessais, accusé de réception à l'impression,
  repli Wi-Fi en point d'accès.
- **Phase 4 — Les garde-fous et le tableau de bord.** Les 8 voyants, la roue, les 4
  sons, quotas et jauge de crédits, mode nuit, page de configuration parents, journal
  technique.
- **Phase 5 — L'objet.** Boîtier, fiches et feutre, démarrage automatique, watchdog,
  résistance au débranchement sauvage, mise à jour à distance.

## 13. Modes de panne à traiter explicitement

| Panne | Réponse attendue |
|---|---|
| Boîte d'en face éteinte | La lettre attend dans l'outbox et part au réveil. « Il a lu ta lettre » reste éteint, aucune alerte. |
| Réseau coupé | APPELLE UN ADULTE + détail sur la page web. Envois mis en file, tout repart seul. |
| Wi-Fi du copain changé | Point d'accès `faxme-setup` après 3 min (§11). |
| Plus de papier | Voyant PLUS DE PAPIER. La lettre **reste non imprimée** dans l'inbox. |
| Capture ratée (fiche de travers, doigt devant) | Appui long sur le bouton d'envoi = annuler la dernière lettre tant qu'elle n'est pas livrée. |
| Ticket sorti puis déchiré/perdu | Appui long sur le bouton d'impression = réimprimer la dernière (24 h). |
| Coupure de courant en pleine impression | La lettre reste marquée non imprimée : elle ressortira. Mieux vaut imprimer deux fois que perdre. |
| Roue sur une position vide | Note « non » à l'appui sur ENVOYER. Ce n'est pas une panne. |
| Fente vide ou fiche blanche | Détecté à la capture : note « non », ni envoi ni crédit consommé. |
| Débranchement sauvage | Racine en lecture seule : rien à réparer au rallumage (§10.6). |
| E-mail d'un expéditeur inconnu | Jeté, jamais imprimé. Réexpédié aux parents si configuré. |
| E-mail dont SPF ou DKIM échoue | Jeté, même si l'adresse est dans la liste blanche. |
| Le Pi ne redémarre pas | Watchdog matériel + `Restart=always`. Un objet du quotidien ne se répare pas au clavier. |
