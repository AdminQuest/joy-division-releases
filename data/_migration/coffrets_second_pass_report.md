# Rapport — Seconde passe coffrets (étape 11)

Date : 2026-05-28
Branche : `claude/coffrets-second-pass`
Source : `data/_migration/coffrets_dossier.md` (15 coffrets extraits des XLSX legacy en session amont)

## Synthèse

- 14 BOX-* nouveaux YAML créés.
- 1 BOOT-* nouveau YAML créé (Good Evening boxed CD, non promu).
- 2 variants existants mis à jour avec une note de reclassification (OFF-H-0001, BOOT-0-0018).
- 1 extension du schéma `variant.schema.json` (composants inline pour `box_format.components`).
- 0 modification du script `scripts/build_site_data.py` requise (générique, BOX-* sont inclus automatiquement dans le JSON consolidé).

## Décisions méthodologiques appliquées

| Question | Décision retenue |
|---|---|
| Heart and Soul (OFF-H-0001 préexistant) | Approche A — création de BOX-H-0001 nouveau, OFF-H-0001 conservé avec note de bascule. |
| + - (plus minus) pirate (BOOT-0-0018 préexistant) | Approche A — création de BOX-0-0004 nouveau, BOOT-0-0018 conservé avec note de bascule. |
| Good Evening boxed CD (G.xlsx ligne 4) | Pas de promotion en BOX — création de BOOT-G-0023 (variant bootleg normal) car le « boxing » est home-made autour d'un CD préexistant, sans pressage neuf. |
| 5 King's Chamber | Variant_group commun `BX-K1` (group_role `pressing_variation`), 5 variants BOX-K-0001 à BOX-K-0005. |
| +- vs + - (officiel vs pirate) | Deux éditions distinctes (BOX-0-0003 officiel + BOX-0-0004 pirate). Confirmé par le dossier : la pirate copie le coffret officiel. |
| Composants exclusifs (Heart and Soul, Japan Atmosphere TCD-7, etc.) | Inline avec rôle libre, jamais de variant_id_ref orphelin. |
| Composants à existence commerciale autonome | `variant_id_ref` uniquement quand mapping non ambigu. Pour la majorité des coffrets (UP / Closer / Still / Substance / Bains-Douches / Preston), nombreuses éditions standalone existent et le pressage exact bundlé n'est pas systématiquement identifiable — inline avec mention « cf. série OFF-X-* pour les éditions standalone ». |
| Convention de nommage variant_id | Suit strictement `scripts/migrate_sheets_to_yaml.py:146` `compute_letter()` — strip article (`The / A / An / Le / La / Les / L' / Un / Une`) puis première lettre A-Z, sinon bucket `0`. |

## Tableau des 14 BOX créés

| variant_id | canonical_title | year | country | release_type | doc_quality | source XLSX / row |
|---|---|---:|---|---|---|---|
| BOX-0-0001 | 1977-1980 Japan Box Set | 1991 | Japan | coffret | verified | Coffrets / 6 |
| BOX-0-0002 | 2007 In Memory LP Box Set | 2007 | UK & Europe | coffret | verified | Coffrets / 3 |
| BOX-0-0003 | +- (plus minus) box set Singles 1978-80 | 2010 | Europe | coffret | **needs_review** | Coffrets / 9 |
| BOX-0-0004 | + - (plus minus) [pirate] | 2010 | UK | coffret | verified | Coffrets / 10 |
| BOX-C-0001 | Les Coffret Cultes FNAC (CD + DVD) | 2009 | France | coffret | verified | Coffrets / 4 |
| BOX-F-0001 | Fractured "box set" | 2011 | UK | coffret | verified | Coffrets / 7 |
| BOX-H-0001 | Heart and Soul (4 CD set) | 1997 | UK | coffret | verified | Coffrets / 2 |
| BOX-K-0001 | The King's Chamber — Box Set V1 (clear) | 2025 | USA | coffret | verified | K / 2 |
| BOX-K-0002 | The King's Chamber — Box Set V2 (clear + splatter) | 2025 | USA | coffret | verified | K / 3 |
| BOX-K-0003 | The King's Chamber — Box Set V3 (clear, alt. Vol2) | 2025 | USA | coffret | verified | K / 4 |
| BOX-K-0004 | The King's Chamber — Tote Bag V1 | 2025 | USA | coffret | verified | K / 5 |
| BOX-K-0005 | The King's Chamber — Tote Bag V2 (gold) | 2025 | USA | coffret | verified | K / 6 |
| BOX-R-0001 | Re-Fractured box set | 2004 | UK | coffret | verified | Coffrets / 8 |
| BOX-S-0001 | La Sélection Idéale (3 CD set) | 2012 | France | coffret | verified | Coffrets / 5 |

## Variants reclassifiés (conservés en place avec note de bascule)

| variant_id | canonical_title | BOX canonique |
|---|---|---|
| OFF-H-0001 | Heart and Soul (4 CD set) | BOX-H-0001 |
| BOOT-0-0018 | + - (plus minus) | BOX-0-0004 |

## Variants bootleg nouveaux (non promus en BOX)

| variant_id | canonical_title | Justification |
|---|---|---|
| BOOT-G-0023 | Good Evening We're Joy Division (boxed CD) | Boxing DIY home-made autour d'un CD préexistant (BOOT-G-0002, BG2a) ; pas de pressage neuf, pas de composant additionnel substantiel. |

## Statistiques composants

| Type de référencement | Nombre |
|---|---:|
| `variant_id_ref` (ref vers variants existants) | 3 |
| `inline` (composants sans existence autonome ou pressage non identifiable) | 51 |
| `additional_items` (boîtes, livrets, photos, posters, T-shirts, tote bags, slip-mats, inserts…) | 32 |

Les 3 références `variant_id_ref` sont toutes dans **BOX-K-0005** (Tote Bag V2 gold) → BOOT-K-0001/0002/0003. Le dossier confirme que les Volumes 1/2/3 gold standalones sont le même pressage que les Volumes du Tote Bag V2 (le notes de BOOT-K-0001 le mentionne explicitement).

## Extension du schéma

`schema/variant.schema.json` — `box_format.components.items` accepte désormais :
- soit `{role, variant_id_ref}` (forme historique)
- soit `{role, inline: {description, type?, format?, catalog_number?, color?, tracklist_summary?}}` (nouveau)

Contrainte `oneOf` enforced : exactement un de `variant_id_ref` ou `inline` doit être présent. `role` reste requis (chaîne libre).

Test suite `tests/validate_fixtures.py` : aucune régression (5 valid + 3 invalid passent toujours).

## Cas particuliers et arbitrages

- **BOX-0-0003 (+- Singles 1978-80)** marqué `documentation_quality: needs_review` : le contenu piste-par-piste est noté « cf discogs » dans le XLSX legacy, et aucun accès Discogs n'a été autorisé dans cette session. Le coffret existe avec ses métadonnées (5000 exemplaires, super deluxe 1-500 avec art piece Saville + 2 CDs promo `+` et `-`), seul le détail des singles 7" reste à compléter.
- **BOX-C-0001 (Coffret Cultes FNAC)** référence inline le DVD Grant Gee sans `variant_id_ref` : 3 éditions standalone existent (VID-J-0001/0002/0003 = UK/USA/Australia), mais aucune édition française n'est cataloguée — la version bundlée dans la boîte Fnac est probablement une 4e pressing FR non encore variantisée.
- **BOX-K-0001 à BOX-K-0004 (King's Chamber non-gold)** : les Volumes 1/2/3 sont inline car les pressages clear / clear+splatter ne sont pas catalogués en standalone (seuls les gold le sont, via BOOT-K-0001/0002/0003).
- **BOX-K-0005 edition.notes** : la mention « #36/50 » du legacy XLSX est ambiguë avec la note « 30 individually numbered tote bag sets » du dossier — likely typo legacy, on retient la valeur 30 du dossier mais on note l'ambiguïté.
- **BOX-R-0001 (Re-Fractured) CD 3 (Paradiso)** : aucun variant standalone identifié pour Paradiso 11/1/80, inline.
- **Naming +- vs + -** : BOX-0-0003 conserve le titre legacy avec « +- » (sans espace) pour l'officiel, BOX-0-0004 conserve « + - » (avec espace) pour le pirate — distinction explicite documentée dans le dossier coffret #9.

## Build pipeline

Le script `scripts/build_site_data.py` agrège tous les YAMLs sous `data/variants/*.yml` via `public_view()` — aucun traitement spécifique au release_type. Les 14 nouveaux BOX sont donc automatiquement inclus dans `site/data/all-variants.json` lors du prochain build CI. `site/app.js:172` rend déjà le format `box` (`coffret · N composants`), compatible avec la nouvelle forme inline (`fd.components?.length` itère sur les composants quelle que soit leur shape).

## Reproductibilité

Pour reproduire les 14 YAMLs à partir du dossier, voir la logique inline dans le commit `Create 14 BOX variants for the coffrets second pass`. Toute évolution future (ajout de composants, raffinement des références après accès Discogs) doit passer par éditions ciblées des YAMLs concernés, pas par re-génération massive.
