# Faxme — courrier papier entre enfants, sans écran

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
   Le numérique n'est qu'un tuyau entre les deux, invisible.
4. **Les destinataires sont un carnet fermé**, configuré par les parents. Aucune
   découverte, aucun ajout depuis l'appareil, aucune façon d'atteindre quelqu'un d'autre.
5. **Défaillance silencieuse interdite.** Sans écran, l'objet doit toujours dire son
   état par la lumière et le son. Un message perdu sans que personne ne le sache est
   le pire échec possible.
6. **L'attente fait partie du plaisir.** On ne cherche pas l'instantané. Le rituel
   (écrire, glisser, attendre, aller relever le courrier) est la valeur du produit.

## 3. Le parcours de l'enfant

**Envoyer**
1. Il écrit ou dessine sur une fiche pré-découpée, posée dans la boîte à côté.
2. Il glisse la fiche dans la fente, contre les butées (position garantie, pas
   d'alignement à réussir).
3. Il appuie sur le bouton du destinataire. Le bouton clignote pendant l'envoi.
4. Le bouton fait deux pulsations gaies quand la lettre a été **imprimée** chez l'autre.
   C'est l'accusé de réception, et c'est la moitié du plaisir.

**Recevoir**
1. Une cloche sonne (une vraie, frappée par un solénoïde) ou un carillon doux.
2. Le voyant « courrier » reste allumé tant qu'il reste des lettres non imprimées.
3. L'enfant appuie sur le gros bouton « imprimer » : une lettre sort. S'il en reste,
   le voyant reste allumé. Il rappuie.

Rien d'autre. Trois boutons au maximum sur le prototype : *envoyer à X*, *imprimer*,
et éventuellement un bouton *recommencer* si la capture est ratée.

## 4. Les décisions structurantes

### 4.1 Format papier et impression

**Choix : impression thermique 80 mm, format d'écriture A6 (105 × 148 mm).**

L'imprimante thermique est la seule technologie qui tienne les principes : pas de
consommable liquide, pas de séchage, pas de pilote, démarrage instantané, rouleau à
2 € qui dure des mois. En contrepartie elle impose une largeur.

Le calcul qui décide du format d'écriture :

| Papier thermique | Largeur imprimable | Points (203 dpi) | Réduction depuis A5 | Réduction depuis A6 |
|---|---|---|---|---|
| 58 mm | ~48 mm | 384 | ×0,32 | ×0,46 |
| **80 mm** | **~72 mm** | **576** | ×0,49 | **×0,69** |

Une lettre d'enfant de 6-8 ans fait environ 10 mm de haut. En A5 sur du 58 mm elle
tombe à 3 mm : illisible. En **A6 sur du 80 mm elle reste à ~7 mm** : parfaitement
lisible, et le ticket sort à ~10 cm de long, taille carte postale. C'est le bon point.

Conséquence produit : on fournit aux enfants des **fiches A6 pré-découpées**, ce qui
sert aussi de quota physique naturel et de guide d'écriture. Un message = une fiche.

Deux points pratiques à ne pas rater :
- **Papier thermique sans phénol** (ni BPA ni BPS). Les enfants vont manipuler ces
  tickets tous les jours, les plier, les garder sous l'oreiller. Ça coûte à peine plus cher.
- **Le thermique s'efface** (chaleur, lumière, frottement) en quelques mois à quelques
  années. Pour les lettres qu'on veut garder, la réponse est l'archive numérique côté
  parents (§7.3), pas le papier.

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
l'ergonomie enfant : glisser une fiche et appuyer, c'est instantané, il n'y a rien à
attendre ni à recommencer. On paie ça par un pipeline image à écrire, mais c'est du
travail fait une fois.

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
  → redressement fin (±3°) + recadrage sur la boîte d'encre
  → redimensionnement à 576 px de large
  → raster ESC/POS
```

Le point contre-intuitif : **surtout pas de tramage.** Le tramage est fait pour les
photos ; sur du trait de stylo il produit une bouillie grise, consomme de l'énergie
thermique et ralentit l'impression. On veut du noir et blanc franc, du trait net.

### 4.3 Transport : Tailscale, pas de serveur

Options envisagées :

| Option | Infra à maintenir | Hors-ligne | Ajout d'un 3ᵉ appareil | Dépendance |
|---|---|---|---|---|
| Serveur relais (VPS) | Oui, un VPS + un service | Géré par le serveur | Trivial | Toi, à vie |
| **Tailscale + HTTP direct** | **Aucune** | File d'attente côté émetteur | Facile | Tailscale |
| MQTT | Un broker | Bonne (QoS 1) | Facile | Broker |
| E-mail / IMAP | Aucune | Excellente | Facile | Fournisseur mail |

**Choix pour le prototype : Tailscale + un petit endpoint HTTP sur chaque appareil.**
Zéro infrastructure, zéro coût récurrent, chiffré de bout en bout, traverse les box
sans ouvrir de port, et — argument sous-estimé — **c'est aussi le canal d'administration** :
tu peux te connecter en SSH sur la boîte installée chez le copain sans rien demander à
ses parents.

La disponibilité se règle côté émetteur : la lettre part dans une **file locale
persistante** et est réessayée jusqu'à acquittement. Si la boîte d'en face est éteinte,
la lettre attend sur disque et part quand elle se rallume. Rien ne se perd.

Si un jour il y a 5 ou 10 boîtes dans le réseau de copains, on bascule vers un relais
central. Le protocole ci-dessous ne change pas.

### 4.4 Le langage lumière/son (le vrai défi)

Sans écran, l'interface **est** ce tableau. Il faut le figer tôt, l'imprimer sur un
petit carton collé sous la boîte, et ne plus en changer.

| État | Lumière | Son |
|---|---|---|
| Prêt | Bouton d'envoi vert fixe, faible | — |
| Envoi en cours | Bouton d'envoi vert clignotant | clic doux |
| Lettre imprimée chez l'autre | Deux pulsations vertes | ding léger |
| Courrier en attente | Bouton d'impression blanc fixe | cloche à l'arrivée |
| Quota épuisé | Bouton d'envoi orange, 3 clignotements au appui | note descendante |
| Mode nuit | Respiration bleue très faible | aucun |
| Pas de réseau | Rouge, clignotement lent | — |
| Plus de papier / erreur imprimante | Rouge, double clignotement rapide | — |
| Panne logicielle | Rouge fixe | — |

Deux remarques :
- Utiliser des **boutons d'arcade 30 mm à LED intégrée** : robustes, satisfaisants à
  appuyer pour un enfant, et la LED est déjà dedans (un composant au lieu de deux).
- Le **son de réception compte plus que la lumière** : une lampe dans une pièce vide
  n'informe personne. Une vraie cloche frappée par un petit solénoïde 5 V (~3 €) est
  ce qui transformera l'objet en événement dans la maison. Alternative charmante :
  le **drapeau de boîte aux lettres américaine** relevé par un micro-servo — visible
  depuis l'autre bout de la pièce, zéro électronique visible, immédiatement compris
  par un enfant.

## 5. Architecture logicielle

Un dépôt, un service par appareil, une configuration par appareil.

```
┌─────────────────── Boîte A (Raspberry Pi) ───────────────────┐
│                                                              │
│  boutons/LED ──► ui (gpiozero) ──┐                           │
│                                  ▼                           │
│  caméra ──────► capture ──► pipeline image ──► outbox/       │
│                                                  │           │
│                                            sender (retry)    │
│                                                  │           │
│  ┌───────────────────────────────────────────────┼────────┐  │
│  │  état : SQLite (messages, quotas, accusés)    │        │  │
│  └───────────────────────────────────────────────┼────────┘  │
│                                                  ▼           │
│  imprimante ◄── printer (ESC/POS) ◄── inbox/ ◄── receiver    │
│                                                   (HTTP)     │
│  config web (LAN seulement, parents) ────────────────────────┤
└──────────────────────────────────┬───────────────────────────┘
                                   │ Tailscale (chiffré)
                                   ▼
                          ┌──── Boîte B ────┐
```

**Pile** : Raspberry Pi OS Lite, Python 3, `picamera2`, `numpy`/`opencv`,
`python-escpos`, `gpiozero`, `FastAPI` (réception + page de config), SQLite,
services `systemd` avec `Restart=always` et watchdog.

Découpage en processus : un service `faxme-ui` (boutons, LED, son, caméra,
impression) et un service `faxme-net` (endpoint HTTP + file d'envoi). Ils communiquent
par la base SQLite et les répertoires `outbox/`/`inbox/`. Avantage : le réseau peut
planter sans figer les boutons, et inversement.

## 6. Protocole et modèle de données

Un message est un dossier :

```
messages/<uuid>/
  meta.json     {"id","from","to","created_at","pages":1,"checksum"}
  page-1.png    1 bit, 576 px de large
  state         queued | sent | delivered | printed | failed
```

Un seul verbe réseau :

```
POST https://<pair>.tailnet:8443/v1/letter
  en-tête : X-Faxme-Device, X-Faxme-Signature (HMAC clé partagée)
  corps   : multipart (meta.json + page-1.png)
  → 202 {"id": ..., "status": "queued"}

POST /v1/receipt   ← l'appareil destinataire signale l'impression
  → l'émetteur fait ses deux pulsations vertes
```

Trois propriétés à ne pas négocier :
- **Idempotence par UUID** : un réessai ne doit jamais imprimer deux fois la même lettre.
- **Authentification par clé d'appareil** (HMAC) même à l'intérieur du tailnet : personne
  ne doit pouvoir faire cracher du papier chez un enfant en tapant une URL.
- **Acquittement à l'impression, pas à la réception**. « Livré » veut dire « sorti sur
  papier ». C'est ce qui rend le retour d'accusé émotionnellement juste.

## 7. Garde-fous

### 7.1 Quota
Compteur quotidien par appareil (défaut : 5 envois/jour), remis à zéro à 4 h du matin.
Dépassement = refus doux (orange + note descendante), jamais un message perdu.
La **réception et l'impression ne sont jamais bloquées par le quota** — sinon on punit
l'enfant pour ce que l'autre a fait.

Le quota physique (une pile de fiches A6 pré-découpées) est un excellent second quota,
plus pédagogique que le premier.

### 7.2 Mode nuit
Plage configurable (défaut 20 h – 7 h) : bouton d'envoi inerte avec un retour sonore
« non », cloche coupée, impression différée au matin. Les lettres arrivées la nuit
sortent au premier appui après 7 h.

### 7.3 Côté parents
Une page web accessible **uniquement depuis le LAN** (et depuis le tailnet) : carnet
de contacts, quota, horaires, calibration de la caméra, test d'impression, et
l'**archive** de toutes les lettres envoyées et reçues, exportable en PDF mensuel.

Cette archive mérite une décision consciente : c'est à la fois un magnifique album
souvenir et une surveillance de la correspondance d'un enfant. Mon avis : à 6-8 ans
l'album l'emporte largement, mais autant le dire aux enfants dès le premier jour
(« les lettres sont gardées dans le livre de la maison ») plutôt que de le découvrir
plus tard. Vers 10-11 ans, il faudra sans doute pouvoir couper l'archive.

## 8. Nomenclature et budget (par boîte, indicatif)

| Poste | Choix | € |
|---|---|---|
| Calculateur | Raspberry Pi 4 (2 Go) ou Zero 2 W | 40–60 |
| Caméra | Camera Module 3 (autofocus) + nappe | 35 |
| Imprimante | Thermique 80 mm ESC/POS USB | 55–90 |
| Boutons | 2–3 arcade 30 mm à LED | 12 |
| Son | Solénoïde + petite cloche, ou buzzer | 5–15 |
| Éclairage | Bandeau LED blanc + diffuseur | 8 |
| Alimentation | **PSU dédiée pour l'imprimante** + PSU Pi | 20 |
| Boîtier | Bois/contreplaqué, découpe simple | 15–30 |
| Divers | Papier sans phénol, câbles, visserie | 15 |
| | **Total** | **~205–280 € / boîte** |

**Le piège classique, à traiter dès le jour 1 :** une imprimante thermique tire des
pointes de plusieurs ampères pendant l'impression. Alimentée depuis le Pi ou depuis la
même petite alimentation, elle le fait redémarrer au milieu d'une lettre — panne
intermittente très pénible à diagnostiquer. **Alimentation séparée pour l'imprimante,
masses reliées, dès le premier montage sur table.**

## 9. Feuille de route du prototype

Chaque phase est utilisable et testable en vrai. On ne passe à la suivante qu'une fois
la précédente stable pendant quelques jours.

- **Phase 0 — La boucle locale** (1 week-end). Un seul Pi, caméra + imprimante, un
  bouton : on scanne, on imprime sur sa propre imprimante. Aucun réseau. But : valider
  le pipeline image et le format papier en faisant écrire les enfants pour de vrai.
  C'est la phase qui décide de tout le reste — si la lettre imprimée n'est pas jolie,
  le projet ne vaut rien, et ça se voit ici.
- **Phase 1 — Deux boîtes sur le même réseau** (1 week-end). Envoi/réception HTTP en
  LAN, file d'attente persistante, idempotence. On les met dans deux pièces de la maison.
- **Phase 2 — Deux maisons** (1 week-end). Tailscale, réessais, LEDs et cloche,
  accusé de réception à l'impression.
- **Phase 3 — Les garde-fous** (1 week-end). Quotas, mode nuit, page de config parents,
  archive.
- **Phase 4 — L'objet** (le plus long). Boîtier, démarrage automatique, watchdog,
  résistance au débranchement sauvage, mise à jour à distance.

## 10. Modes de panne à traiter explicitement

| Panne | Réponse attendue |
|---|---|
| Boîte d'en face éteinte | La lettre attend dans l'outbox, part au réveil. Aucun signal d'erreur avant plusieurs heures. |
| Réseau coupé | Rouge lent, envois mis en file, tout repart seul. |
| Plus de papier | Détecté avant impression si l'imprimante le remonte, sinon après échec. La lettre **reste non imprimée** dans l'inbox. |
| Capture ratée (fiche de travers, doigt devant) | Bouton « recommencer » qui annule le dernier envoi tant qu'il n'est pas livré. |
| Coupure de courant en pleine impression | La lettre reste marquée non imprimée : elle ressortira. Mieux vaut imprimer deux fois que perdre. |
| Le Pi ne redémarre pas | Watchdog matériel + services `Restart=always`. Un objet du quotidien ne se répare pas au clavier. |

## 11. Questions ouvertes

1. **Où est la deuxième boîte ?** Chez un copain ? Chez les grands-parents ? Chez
   l'autre parent ? Ça change beaucoup de choses : installer un objet connecté chez
   quelqu'un d'autre demande l'adhésion de ses parents, un coin de table, une prise, et
   quelqu'un qui changera le rouleau de papier. Le prototype le plus facile à réussir
   est **grands-parents ↔ enfant** : bénéficiaire enthousiaste, et l'asymétrie
   d'écriture (un adulte qui répond toujours) garantit que la boucle tourne.
2. **Quel âge ?** Ça décide de la taille d'écriture, donc du format papier, donc de la
   largeur d'impression.
3. **Une ou deux fiches par lettre ?** Je commencerais à une seule, quitte à ce que
   l'enfant envoie deux lettres.
4. **La cloche ou le drapeau ?** Les deux marchent ; le drapeau est plus doux pour la
   maison, la cloche plus excitante pour l'enfant.
5. **Archive visible des parents : oui, non, ou jusqu'à quel âge ?**
