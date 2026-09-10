# Phase 1 — la passerelle e-mail

> Une seule boîte devient utile : les adultes écrivent depuis leur téléphone.

C'est ce qui permet de mettre l'objet en service à la maison sans attendre l'accord
d'une autre famille — et de découvrir si le rituel prend avant d'installer du matériel
chez quelqu'un.

**Il n'y a pas d'application à installer.** L'application, c'est l'appareil photo et la
messagerie du téléphone. On demande simplement aux adultes d'utiliser le mode
« numériser un document » déjà présent dans leur téléphone : il redresse la perspective
tout seul.

## 1. Créer la boîte aux lettres

Un compte **Gmail dédié**, gratuit, qui ne servira qu'à ça et ne sera jamais publié.

1. Créer le compte, par exemple `raphael.faxme@gmail.com`.
2. Activer la **validation en deux étapes** (obligatoire pour l'étape suivante).
3. Créer un **mot de passe d'application** (16 caractères) dans les paramètres de
   sécurité du compte Google.
4. Vérifier qu'IMAP est actif : *Paramètres → Transfert et POP/IMAP*.

Le mot de passe ne va **jamais** dans le fichier de configuration, qui finit dans un
dépôt git :

```bash
export FAXME_MAIL_PASSWORD='xxxx xxxx xxxx xxxx'
```

## 2. Écrire le carnet

C'est le cœur du modèle de sécurité : **rien de ce qui n'est pas dans ce fichier ne
peut atteindre le papier.** Il n'existe aucun moyen d'ajouter un correspondant depuis
l'appareil.

```toml
[mail]
address = "raphael.faxme@gmail.com"
forward_unknown_to = "papa@example.com"   # facultatif : ce qui est refusé t'est renvoyé

[[contacts]]
name = "Mamie"            # le nom imprimé sur le ticket, jamais celui annoncé par le message
kind = "email"
address = "mamie@example.com"
alias = "mamie7fk3"
```

Un message est imprimé **si et seulement si** les quatre conditions sont réunies :

1. l'expéditeur est dans le carnet ;
2. le message passe **DMARC**, ou à défaut **DKIM et SPF** — sans quoi n'importe qui
   ferait imprimer ce qu'il veut chez un enfant en écrivant « de la part de Mamie » ;
3. la sous-adresse utilisée, s'il y en a une, correspond à celle du contact ;
4. il contient une image exploitable ou du texte.

Tout le reste est jeté, jamais mis en attente.

> **L'alias `+mamie7fk3` identifie, il n'authentifie pas.** Sur Gmail, quiconque connaît
> l'adresse de base peut y accoler le suffixe de son choix. Ce qui protège, c'est le
> carnet et la vérification SPF/DKIM.

## 3. Ce qu'on dit aux adultes

À recopier tel quel dans un message aux grands-parents :

> Raphaël a une petite boîte qui imprime le courrier sur du papier, et il peut la
> relever tout seul — il n'y a pas d'écran.
>
> Pour lui écrire, envoie un e-mail à **raphael.faxme+mamie7fk3@gmail.com**. Tu peux
> taper ton message directement, ou mieux : écris-lui un mot à la main sur une feuille,
> prends-le en photo avec ton téléphone et joins la photo. Si ton téléphone a un mode
> « numériser un document », utilise-le, le résultat sera plus net.
>
> Il verra une lumière s'allumer, appuiera sur un bouton, et ta lettre sortira.

## 4. Utiliser depuis un PC, sans matériel

```bash
faxme -c boite.toml etat                 # courrier en attente, crédits, carnet
faxme -c boite.toml relever              # relève la boîte Gmail
faxme -c boite.toml imprimer-attente -p /dev/usb/lp0
faxme -c boite.toml envoyer photo.jpg --a Mamie
```

L'état vit dans `var/` : `var/state.db` pour la base, `var/messages/` pour les images
en transit.

## 5. Sur le Pi : le service

```bash
faxme -c boite.toml boite \
  --peripherique /dev/usb/lp0 \
  --bouton-envoi 17 --bouton-impression 27 \
  --voyant-courrier 22 --voyant-erreur 23
```

Il relève la boîte toutes les minutes en tâche de fond et surveille deux boutons :
**envoyer** (numérise la fiche et l'envoie) et **imprimer** (sort la lettre reçue la
plus ancienne). Le tableau de bord complet — huit voyants, roue de sélection, quatre
sons — est la phase 4 ; ici deux voyants facultatifs suffisent à ne pas être aveugle.

En service permanent, avec systemd :

```ini
[Unit]
Description=Faxme
After=network-online.target

[Service]
ExecStart=/usr/local/bin/faxme -c /etc/faxme/boite.toml boite
Environment=FAXME_MAIL_PASSWORD=xxxxxxxxxxxxxxxx
Restart=always
RestartSec=5
User=faxme

[Install]
WantedBy=multi-user.target
```

## 6. Les règles que le service applique tout seul

| Règle | Comportement |
|---|---|
| **Quota** | 5 envois par jour, remis à zéro à 4 h. La réception n'est jamais bloquée : on ne punit pas un enfant pour ce qu'un autre a fait. |
| **Mode nuit** | 20 h – 7 h : ni envoi ni impression. Le courrier arrivé la nuit attend le matin, rien n'est perdu. |
| **Idempotence** | Un même e-mail relevé deux fois n'est imprimé qu'une fois, y compris après un redémarrage en plein traitement. |
| **Purge** | L'image est effacée une fois imprimée ou envoyée. La dernière lettre imprimée reste 24 h, pour la réimprimer si le ticket s'est déchiré. |
| **Suppression côté serveur** | Le message est supprimé de Gmail après traitement, corbeille comprise. |

## 7. Ce que la passerelle ne peut pas tenir

**La rétention zéro s'arrête à la boîte aux lettres de l'adulte.** Côté Faxme, tout est
effacé. Côté Mamie, sa copie reste dans sa messagerie pour toujours, et le message a
transité par son fournisseur. C'est inhérent à l'e-mail, et c'est pour cette raison que
le lien entre deux boîtes d'enfants n'utilisera pas l'e-mail mais Tailscale
(cf. `CONCEPT.md` §7.6 et §7.7).

**Le voyant « il a lu ta lettre » ne dit pas la vérité pour un contact e-mail** : il
n'existe aucun accusé de lecture fiable. Il s'allume à l'acceptation du message par le
serveur, ce qui veut dire « partie », pas « lue ».

## Tests

```bash
python -m pytest -q
```

Toute la logique de décision — qui a le droit d'écrire, quel message est authentique,
que contient-il — se teste **hors ligne**, sur des messages fabriqués : c'est la partie
où une erreur laisse un inconnu imprimer chez un enfant. Le transport IMAP/SMTP, lui,
n'est qu'une trentaine de lignes de bibliothèque standard.
