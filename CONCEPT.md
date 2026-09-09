# Faxme — courrier papier entre enfants, sans écran

## 0. Le cadre du prototype (décidé)

- **Deux boîtes** : à la maison, et chez le meilleur copain, dont les parents sont partants.
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
3. Il appuie sur le gros bouton d'envoi. Le bouton clignote pendant l'envoi.
4. Le bouton fait deux pulsations gaies quand la lettre a été **imprimée** chez le
   copain. C'est l'accusé de réception, et c'est la moitié du plaisir.

**Recevoir**
1. Une cloche sonne (une vraie, frappée par un solénoïde) ou un carillon doux.
2. Le voyant « courrier » reste allumé tant qu'il reste des lettres non imprimées.
3. L'enfant appuie sur le bouton « imprimer » : une lettre sort. S'il en reste, le
   voyant reste allumé. Il rappuie.

Deux boutons, puisqu'il n'y a qu'un destinataire : **envoyer** et **imprimer**.

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

### 4.4 Le langage lumière/son, version 7 ans

Un enfant de 7 ans ne décode pas une table de clignotements. L'interface se lit donc
à **deux niveaux** : trois états pour l'enfant, le détail pour l'adulte.

**Ce que l'enfant doit apprendre (et rien d'autre) :**

| | Signification |
|---|---|
| 🟢 Vert | Tout va bien, tu peux écrire |
| ⚪ Blanc allumé + cloche | Tu as du courrier, appuie pour l'imprimer |
| 🔴 Rouge | La boîte a un souci : va chercher un adulte |

**Le détail, pour l'adulte, imprimé sur un carton collé sous la boîte :**

| État | Lumière | Son |
|---|---|---|
| Prêt | Vert fixe, faible | — |
| Envoi en cours | Vert clignotant | clic doux |
| Lettre imprimée chez le copain | Deux pulsations vertes | ding léger |
| Lettre partie mais pas encore imprimée (> 6 h) | Vert, pulsation lente | — |
| Courrier en attente d'impression | Blanc fixe | cloche à l'arrivée |
| Quota épuisé | Orange, 3 clignotements à l'appui | note descendante |
| Mode nuit | Respiration bleue très faible | aucun |
| Pas de réseau | Rouge, clignotement lent | — |
| Plus de papier / erreur imprimante | Rouge, double clignotement rapide | — |
| Panne logicielle | Rouge fixe | — |

Trois remarques :
- Utiliser des **boutons d'arcade 30 mm à LED intégrée** : robustes, satisfaisants à
  appuyer, et la LED est déjà dedans (un composant au lieu de deux).
- Le **son de réception compte plus que la lumière** : une lampe dans une pièce vide
  n'informe personne. Une vraie cloche frappée par un petit solénoïde 5 V (~3 €) est
  ce qui transformera l'objet en événement dans la maison. Alternative charmante : le
  **drapeau de boîte aux lettres américaine** relevé par un micro-servo, visible de
  loin et immédiatement compris.
- L'état « partie mais pas encore lue » compte à 7 ans : sans lui, une lettre chez un
  copain absent trois jours ressemble à une lettre perdue.

## 5. Architecture logicielle

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
│                    │                              (HTTP)    │
│                    └──► purge (§6.2)                         │
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

Un seul verbe réseau :
```
POST /v1/letter    multipart (meta.json + page-1.png)
                   en-têtes X-Faxme-Device + X-Faxme-Signature (HMAC clé partagée)
                   → 202 {"id": ..., "status": "queued"}
POST /v1/receipt   ← le destinataire signale l'IMPRESSION
                   → l'émetteur fait ses deux pulsations vertes
```

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
Compteur quotidien par appareil (défaut : **5 envois/jour**), remis à zéro à 4 h.
Dépassement = refus doux (orange + note descendante), jamais une lettre perdue.
La **réception et l'impression ne sont jamais bloquées par le quota** — sinon on
punit un enfant pour ce que l'autre a fait.

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
| Imprimante | Thermique 80 mm ESC/POS USB | 55–90 |
| Boutons | 2 arcade 30 mm à LED | 10 |
| Son | Solénoïde + petite cloche, ou buzzer | 5–15 |
| Éclairage | Bandeau LED blanc + diffuseur | 8 |
| Alimentation | **PSU dédiée pour l'imprimante** + PSU Pi | 20 |
| Boîtier | Bois/contreplaqué, découpe simple | 15–30 |
| Divers | Papier sans phénol, feutres, fiches, câbles | 20 |
| | **Total** | **~210–290 € / boîte** |

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
- **Phase 3 — Les garde-fous** (1 week-end). Quotas, mode nuit, page de configuration
  parents, journal technique.
- **Phase 4 — L'objet** (le plus long). Boîtier, fiches et feutre, démarrage
  automatique, watchdog, résistance au débranchement sauvage, mise à jour à distance.

## 11. Modes de panne à traiter explicitement

| Panne | Réponse attendue |
|---|---|
| Boîte d'en face éteinte | La lettre attend dans l'outbox et part au réveil. Pulsation lente après 6 h, jamais de rouge. |
| Réseau coupé | Rouge lent, envois mis en file, tout repart seul. |
| Wi-Fi du copain changé | Point d'accès `faxme-setup` après 3 min (§9). |
| Plus de papier | Rouge double clignotement. La lettre **reste non imprimée** dans l'inbox. |
| Capture ratée (fiche de travers, doigt devant) | Appui long sur le bouton d'envoi = annuler la dernière lettre tant qu'elle n'est pas livrée. |
| Ticket sorti puis déchiré/perdu | Appui long sur le bouton d'impression = réimprimer la dernière (24 h). |
| Coupure de courant en pleine impression | La lettre reste marquée non imprimée : elle ressortira. Mieux vaut imprimer deux fois que perdre. |
| Le Pi ne redémarre pas | Watchdog matériel + `Restart=always`. Un objet du quotidien ne se répare pas au clavier. |
