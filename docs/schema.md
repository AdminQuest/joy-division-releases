# Schéma et pipeline

Ce document décrit le schéma de validation des variantes
(`schema/variant.schema.json`) et les choix structurels qui le sous-tendent.

## Format

JSON Schema **draft 2020-12** (`https://json-schema.org/draft/2020-12/schema`).
Le schéma se valide lui-même contre le méta-schéma — vérifié par
`tests/validate_fixtures.py` (`Draft202012Validator.check_schema`).

## Vue d'ensemble

Une **variante** est un objet décrivant une release de Joy Division à la
maille la plus fine pertinente pour un collectionneur ou un discographe :
un pressage spécifique d'un disque, une édition d'un livre, une VHS, un
coffret, etc.

Le schéma combine :

1. Un **tronc commun** (champs partagés par toutes les variantes) — règles
   strictes : `additionalProperties: false`, types nullables explicites
   (`["string", "null"]`), valeurs énumérées pour les champs catégoriels.
2. Un **discriminant** sur `release_type` qui sélectionne dynamiquement le
   schéma à appliquer à `format_details` via `allOf` + `if/then`.
3. Des **extensions typées** dans `$defs` — un `*_format` par grande famille,
   plus des sous-définitions réutilisables (`audio_support`, `audio_track`,
   etc.).

## Tronc commun

Champs requis pour toute variante :

| Champ                   | Type      | Notes                                        |
|-------------------------|-----------|----------------------------------------------|
| `variant_id`            | string    | Motif `^(OFF\|PIR\|BOOT\|VID\|BOX\|BOOK\|PARA)-[A-Z0]-[0-9]{4}$` |
| `release_type`          | enum      | 7 valeurs (voir ci-dessous)                  |
| `canonical_title`       | string    | `minLength: 1`                               |
| `canonical_artist`      | string    | Défaut `"Joy Division"`                      |
| `documentation_quality` | enum      | `verified` / `needs_review` / `stub`         |
| `format_details`        | object    | Validé conditionnellement (cf. discriminant) |

Les champs optionnels (sources, dates, édition, distribution, URLs, notes…)
sont tous nullables — le `null` est un signal explicite « pas de valeur »,
distinct de l'absence du champ.

### `year` — optionnel mais contraint quand présent

`year` est **optionnel**. La migration depuis le legacy a révélé qu'une
part significative des bootlegs anciens et de certains pressages pirates
n'a aucune année documentée. Imposer un fallback arbitraire (`2000`, par
exemple) ajouterait de la fausse information au registre canonique ;
préférable d'accepter l'absence comme une donnée légitime.

Quand `year` est présent, la contrainte reste stricte : `integer` dans la
plage `1976 ≤ year ≤ 2030`. On ne tolère pas une valeur invraisemblable,
seulement l'absence du champ.

La fixture `tests/fixtures/valid/valid_without_year.yml` exerce
explicitement ce cas.

### `_legacy_code`

Champ d'exception : objet permissif (`additionalProperties: true`) pour
conserver l'identifiant et les colonnes Sheets d'origine après la migration
depuis la feuille de calcul historique. Sans validation stricte, il ne
contraint pas la qualité des données mais évite la perte d'information lors
de l'import.

## Discriminant `release_type` → `format_details`

La règle de validation conditionnelle est exprimée par un `allOf` de cinq
clauses `if/then` au niveau racine. Chaque clause teste la valeur de
`release_type` et applique le `$ref` correspondant à `format_details` :

| `release_type`                       | `format_details` valide contre |
|--------------------------------------|--------------------------------|
| `officiel`, `pirate`, `bootleg`      | `#/$defs/audio_format`         |
| `video`                              | `#/$defs/video_format`         |
| `coffret`                            | `#/$defs/box_format`           |
| `livre`                              | `#/$defs/book_format`          |
| `para`                               | `#/$defs/para_format`          |

Chaque `*_format` impose un champ `type` constant (`"audio"`, `"video"`,
`"box"`, `"book"`, `"para"`), ce qui donne un second filet de sécurité :
même si l'on contournait le discriminant racine, l'incohérence
`release_type` ↔ `format_details.type` ressort à la validation. Voir
`tests/fixtures/invalid/wrong_format_details.yml`.

## Motif `variant_id`

Format : `<PREFIX>-<LETTRE>-<NNNN>`.

- **PREFIX** (3 ou 4 lettres) : code de la famille de release.
  - `OFF` officiel
  - `PIR` pirate
  - `BOOT` bootleg
  - `VID` video
  - `BOX` coffret
  - `BOOK` livre
  - `PARA` para-discographique
- **LETTRE** : initiale du titre canonique, en majuscule (`[A-Z]`), ou
  chiffre `0` (cf. bootstrap ci-dessous).
- **NNNN** : numéro d'ordre sur 4 chiffres, locale à la lettre.

### Règle de bootstrap « lettre `0` »

Certains titres ne commencent pas par une lettre alphabétique
(chiffres, symboles, traductions translittérées, titres muets ou
intentionnellement vides). Pour conserver un motif `variant_id`
strictement régulier sans introduire de catégorie spéciale, ces titres
sont regroupés sous la **lettre `0`**. C'est la seule valeur non
alphabétique acceptée par le pattern (`[A-Z0]`).

## Regroupement de sous-variantes — `variant_group`

Champ **optionnel** du tronc commun. Permet d'exprimer qu'un ensemble
de variantes partage un même pressage / une même édition source, tout
en conservant un `variant_id` distinct par sous-variante.

Cas d'usage typique issu de la migration legacy : le bootleg
*Warsaw LP* UK 2018 (catalog `FACT 261`) circule en 8 couleurs de
vinyl issues du même pressage. Chaque couleur a sa propre cotation
sur le marché secondaire (le clear et le splatter ne se vendent pas
au même prix), donc on conserve 8 `variant_id` indépendants pour le
suivi de collection et la veille marchande. Le champ
`variant_group` offre le pont vers une vue consolidée : une interface
publique peut regrouper ces 8 entrées sous une seule fiche
"Warsaw LP — 8 color variations".

### Structure

```yaml
variant_group:
  group_id: BW4               # arbitraire mais stable, partage par le groupe
  group_role: color_variation # nature du regroupement
  group_description: |        # optionnel, texte libre
    Warsaw LP UK 2018 release, 8 color variants
    from the same pressing.
```

### Champs

| Champ               | Type                | Notes                                                                       |
|---------------------|---------------------|-----------------------------------------------------------------------------|
| `group_id`          | string (≥1 char)    | Identifiant arbitraire stable. Partagé par toutes les sous-variantes.       |
| `group_role`        | enum                | `color_variation` / `pressing_variation` / `format_variation` / `other`     |
| `group_description` | string \| null      | Texte libre décrivant le groupe.                                            |

### Conventions

- **Optionnel** : la majorité des variantes ne sont pas regroupées (pressages distincts, éditions distinctes, etc.) et n'ont pas de `variant_group`.
- **`group_id` recyclé du legacy** : pour les bootlegs migrés du legacy, on réutilise le préfixe du code legacy (ex. `BW4` pour la série `BW4a` … `BW4h`) — choix arbitraire mais traçable.
- **Trois `group_role`** :
  - `color_variation` — même pressage, couleurs de vinyl différentes (Warsaw LP).
  - `pressing_variation` — pressages différents (UK 1979 vs Italy 1980 d'un même album) ; à utiliser avec parcimonie, ces cas sont déjà naturellement séparés par `variant_id`.
  - `format_variation` — même édition déclinée en LP + CD + cassette.
  - `other` — échappatoire pour cas non couverts.
- **Pas de contrainte d'unicité** sur `group_id` : un seul variant peut porter un `group_id` (groupe d'un membre, en anticipation d'autres) ; deux variants avec le même `group_id` indiquent un groupe constitué.

La fixture `tests/fixtures/valid/valid_with_variant_group.yml` exerce
ce mécanisme.

## Extensions typées (`$defs`)

| `$def`             | Rôle                                                                 |
|--------------------|----------------------------------------------------------------------|
| `variant_group`    | Regroupement de sous-variantes (cf. section dédiée)                  |
| `edition`          | Caractérise un tirage limité / numéroté                              |
| `distribution`     | Canal de distribution (commercial, promo, presse, pressage privé)    |
| `audio_format`     | Description d'une variante audio (vinyle, CD, cassette…)             |
| `audio_support`    | Support physique audio individuel                                    |
| `audio_content`    | Tracklist côté par côté                                              |
| `audio_track`      | Piste d'une face                                                     |
| `video_format`     | Variante vidéo (DVD, VHS, Blu-ray, UMD)                              |
| `video_support`    | Support physique vidéo individuel                                    |
| `box_format`       | Coffret référençant des variantes par `variant_id_ref` + items bonus |
| `book_format`      | Livre (ISBN, auteurs, éditeur, dimensions…)                          |
| `para_format`      | Para-discographique (magazine, press kit, flexis, fanzine…)          |

Toutes les définitions imposent `additionalProperties: false`, sauf
`_legacy_code` au niveau racine.

## Pipeline

Le pipeline complet d'ingestion → normalisation → validation → publication
sera documenté ici au fur et à mesure de sa construction. Étape actuellement
couverte :

- **Validation** : `python3 tests/validate_fixtures.py` valide le méta-schéma
  puis les fixtures (`tests/fixtures/valid/` doivent passer,
  `tests/fixtures/invalid/` doivent échouer). Le validateur active
  explicitement le `FORMAT_CHECKER` du draft 2020-12 : `format: uri`,
  `format: date`, etc. sont des annotations purement informatives par
  défaut dans `jsonschema` et ne sont enforced qu'avec un format checker
  explicite — sans lui, un `joydiv_url` ou `discogs_url` malformé passerait
  silencieusement.

### Installation locale

```bash
pip install 'jsonschema[format]' pyyaml
python3 tests/validate_fixtures.py
```

L'extra `[format]` installe `rfc3339-validator`, `rfc3987`, etc. —
nécessaires pour que le `FORMAT_CHECKER` puisse réellement valider les
`format` standards (`date`, `date-time`, `uri`, …).

## Notes pour les contributeurs

- Toujours quoter en YAML les durées `mm:ss`, les `aspect_ratio` style `4:3`
  et les dates `YYYY-MM-DD`, sinon PyYAML les interprète respectivement
  comme nombre sexagésimal, sexagésimal, et `datetime.date` — ce qui casse
  la validation `string`.
- Toute modification du schéma doit être accompagnée d'au moins un fixture
  valide et un contre-exemple pour la règle ajoutée.
