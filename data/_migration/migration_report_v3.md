# Rapport de migration v2 — 2026-05-27T17:17:56

## Synthese

- XLSX lus : **55**
- Variantes produites : **1669**
- Ownerships produits : **504**
- Series detectees (variant_group) : **135**
- Variants membres d'une serie : **632**
- Reclassifications BOOK -> PARA : **8**
- Coffrets identifies (skippes) : **15**
- Lignes XLSX rejetees : **16**
- Erreurs de validation : **0** (sinon le script aurait stoppe)

## Decomposition par prefixe

| Prefixe | Variantes | Ownerships |
|---|---:|---:|
| BOOT | 1066 | 266 |
| OFF | 309 | 119 |
| PIR | 132 | 34 |
| VID | 27 | 16 |
| BOX | 0 | 0 |
| BOOK | 127 | 62 |
| PARA | 8 | 7 |

## Decomposition BOOT par lettre

| Lettre | Variantes |
|---|---:|
| 0 | 53 |
| A | 96 |
| B | 51 |
| C | 45 |
| D | 66 |
| E | 41 |
| F | 30 |
| G | 22 |
| H | 19 |
| I | 69 |
| J | 3 |
| K | 15 |
| L | 102 |
| M | 76 |
| N | 13 |
| O | 4 |
| P | 57 |
| Q | 1 |
| R | 42 |
| S | 51 |
| T | 49 |
| U | 13 |
| V | 4 |
| W | 132 |
| X | 2 |
| Y | 10 |
| Z | 0 |

## Qualite de documentation

| Statut | Nombre |
|---|---:|
| verified | 1445 |
| needs_review | 224 |
| stub | 0 |

## Top 10 XLSX par variantes produites

| XLSX | Variantes |
|---|---:|
| Livres -.xlsx | 135 |
| Bootlegs - W.xlsx | 133 |
| Bootlegs - A.xlsx | 117 |
| Bootlegs - L.xlsx | 104 |
| Officiels et pirates - Unknown Pleasures.xlsx | 82 |
| Bootlegs - M.xlsx | 77 |
| Bootlegs - I.xlsx | 74 |
| Bootlegs - D.xlsx | 66 |
| Bootlegs - T.xlsx | 61 |
| Bootlegs - P.xlsx | 57 |

## Reclassifications BOOK -> PARA (8)

| XLSX | Ligne | Titre | parent_object |
|---|---:|---|---|
| Livres -.xlsx | 27 | BEST #267 | magazine |
| Livres -.xlsx | 28 | Les Inrockuptibles #9 | magazine |
| Livres -.xlsx | 29 | Les Inrockuptibles #1292 | magazine |
| Livres -.xlsx | 31 | Elegy #49 | magazine |
| Livres -.xlsx | 71 | Peter Hook Signature Collection (auction catalogue) | misc |
| Livres -.xlsx | 87 | MOJO #316 | magazine |
| Livres -.xlsx | 88 | UNCUT MAGAZINE | magazine |
| Livres -.xlsx | 98 | Decades fanzine | fanzine |

## Lignes rejetees (16)

| XLSX | Ligne | Raison |
|---|---:|---|
| Bootlegs - E.xlsx | 8 | titre vide |
| Bootlegs - I.xlsx | 25 | titre vide |
| Bootlegs - I.xlsx | 62 | titre vide |
| Bootlegs - J.xlsx | 5 | titre vide |
| Bootlegs - J.xlsx | 6 | titre vide |
| Bootlegs - J.xlsx | 7 | titre vide |
| Bootlegs - J.xlsx | 8 | titre vide |
| Bootlegs - J.xlsx | 9 | titre vide |
| Bootlegs - J.xlsx | 10 | titre vide |
| Bootlegs - J.xlsx | 11 | titre vide |
| Bootlegs - M.xlsx | 10 | titre vide |
| Livres -.xlsx | 2 | ligne d'en-tete / section |
| Livres -.xlsx | 34 | ligne d'en-tete / section |
| Livres -.xlsx | 37 | ligne d'en-tete / section |
| Officiels et pirates - 7_ - LWTUA.xlsx | 21 | titre vide |
| Officiels et pirates - VHS & DVD.xlsx | 15 | titre vide |

## Coffrets identifies pour seconde passe (15)

| XLSX | Ligne | Titre | Raison |
|---|---:|---|---|
| Bootlegs - G.xlsx | 4 | Good Evening We're Joy Division | format box set |
| Bootlegs - K.xlsx | 2 | The King's Chamber | format box set |
| Bootlegs - K.xlsx | 3 | The King's Chamber | format box set |
| Bootlegs - K.xlsx | 4 | The King's Chamber | format box set |
| Bootlegs - K.xlsx | 5 | The King's Chamber | format box set |
| Bootlegs - K.xlsx | 6 | The King's Chamber | format box set |
| Officiels et pirates - Coffrets.xlsx | 2 | Heart and Soul (4 CD set) | fichier Coffrets.xlsx |
| Officiels et pirates - Coffrets.xlsx | 3 | 2007 In Memory LP Box Set | fichier Coffrets.xlsx |
| Officiels et pirates - Coffrets.xlsx | 4 | Les Coffret Cultes FNAC (CD + DVD) | fichier Coffrets.xlsx |
| Officiels et pirates - Coffrets.xlsx | 5 | La Sélection Idéale (3 CD set) | fichier Coffrets.xlsx |
| Officiels et pirates - Coffrets.xlsx | 6 | 1977-1980 Japan Box Set | fichier Coffrets.xlsx |
| Officiels et pirates - Coffrets.xlsx | 7 | Fractured "box set" | fichier Coffrets.xlsx |
| Officiels et pirates - Coffrets.xlsx | 8 | Re-Fractured box set | fichier Coffrets.xlsx |
| Officiels et pirates - Coffrets.xlsx | 9 | +- (plus minus) box set Singles 1978-80 | fichier Coffrets.xlsx |
| Officiels et pirates - Coffrets.xlsx | 10 | + - (plus minus) | fichier Coffrets.xlsx |

## Variants en needs_review (224)

| variant_id | source | raison |
|---|---|---|
| `BOOT-0-0031` | Bootlegs - A.xlsx row 28 | format audio non parse: None |
| `BOOT-B-0030` | Bootlegs - B.xlsx row 31 | format audio non parse: None |
| `BOOT-C-0002` | Bootlegs - C.xlsx row 3 | format audio non parse: 'Picture LP pink' |
| `BOOT-C-0003` | Bootlegs - C.xlsx row 4 | format audio non parse: 'Picture LP pink' |
| `BOOT-C-0004` | Bootlegs - C.xlsx row 5 | format audio non parse: 'Picture LP green' |
| `BOOT-F-0016` | Bootlegs - F.xlsx row 17 | format audio non parse: 'cf liste sur joydiv.org' |
| `BOOT-F-0027` | Bootlegs - F.xlsx row 28 | format audio non parse: None |
| `BOOT-K-0014` | Bootlegs - K.xlsx row 20 | format audio non parse: 'clear / light brown splatter LP' |
| `BOOT-L-0016` | Bootlegs - L.xlsx row 18 | format audio non parse: None |
| `BOOT-L-0019` | Bootlegs - L.xlsx row 22 | format audio non parse: None |
| `BOOT-L-0070` | Bootlegs - L.xlsx row 73 | format audio non parse: 'translucent black/grey splattered vinyl LP' |
| `BOOT-L-0074` | Bootlegs - L.xlsx row 77 | format audio non parse: 'Black & white LP' |
| `BOOT-L-0082` | Bootlegs - L.xlsx row 85 | format audio non parse: None |
| `BOOT-L-0096` | Bootlegs - L.xlsx row 99 | format audio non parse: None |
| `BOOT-L-0102` | Bootlegs - L.xlsx row 105 | format audio non parse: None |
| `BOOT-O-0001` | Bootlegs - O.xlsx row 2 | format audio non parse: None |
| `BOOT-R-0042` | Bootlegs - R.xlsx row 43 | format audio non parse: None |
| `BOOT-S-0018` | Bootlegs - S.xlsx row 19 | format audio non parse: None |
| `BOOT-T-0044` | Bootlegs - T.xlsx row 41 | format audio non parse: 'Black & White split LP' |
| `BOOT-T-0045` | Bootlegs - T.xlsx row 42 | format audio non parse: 'purple splattered vinyl LP ?' |
| `BOOT-T-0046` | Bootlegs - T.xlsx row 43 | format audio non parse: 'green LP ?' |
| `BOOT-U-0007` | Bootlegs - U.xlsx row 8 | format audio non parse: 'White & Blue Splatter LP' |
| `BOOT-U-0012` | Bootlegs - U.xlsx row 13 | format audio non parse: None |
| `BOOT-V-0001` | Bootlegs - V.xlsx row 2 | format audio non parse: None |
| `BOOT-0-0053` | Bootlegs - W.xlsx row 7 | format audio non parse: None |
| `BOOT-W-0095` | Bootlegs - W.xlsx row 97 | format audio non parse: None |
| `BOOT-W-0096` | Bootlegs - W.xlsx row 98 | format audio non parse: None |
| `BOOT-W-0097` | Bootlegs - W.xlsx row 99 | format audio non parse: None |
| `BOOT-W-0098` | Bootlegs - W.xlsx row 100 | format audio non parse: None |
| `BOOT-W-0099` | Bootlegs - W.xlsx row 101 | format audio non parse: None |
| `BOOT-W-0122` | Bootlegs - W.xlsx row 124 | format audio non parse: None |
| `BOOT-X-0001` | Bootlegs - X.xlsx row 2 | format audio non parse: None |
| `BOOT-X-0002` | Bootlegs - Z.xlsx row 2 | format audio non parse: None |
| `BOOK-J-0001` | Livres -.xlsx row 3 | par defaut |
| `BOOK-H-0001` | Livres -.xlsx row 4 | par defaut |
| `BOOK-J-0002` | Livres -.xlsx row 5 | par defaut |
| `BOOK-S-0001` | Livres -.xlsx row 6 | par defaut |
| `BOOK-J-0003` | Livres -.xlsx row 7 | par defaut |
| `BOOK-U-0001` | Livres -.xlsx row 8 | par defaut |
| `BOOK-J-0004` | Livres -.xlsx row 9 | par defaut |
| `BOOK-I-0001` | Livres -.xlsx row 10 | par defaut |
| `BOOK-J-0005` | Livres -.xlsx row 11 | par defaut |
| `BOOK-J-0006` | Livres -.xlsx row 12 | par defaut |
| `BOOK-J-0007` | Livres -.xlsx row 13 | par defaut |
| `BOOK-M-0001` | Livres -.xlsx row 14 | par defaut |
| `BOOK-N-0001` | Livres -.xlsx row 15 | par defaut |
| `BOOK-0-0001` | Livres -.xlsx row 16 | auteur non renseigne -> 'Inconnu' |
| `BOOK-E-0001` | Livres -.xlsx row 17 | par defaut |
| `BOOK-H-0002` | Livres -.xlsx row 18 | par defaut |
| `BOOK-I-0002` | Livres -.xlsx row 19 | par defaut |
| `BOOK-I-0003` | Livres -.xlsx row 20 | par defaut |
| `BOOK-R-0001` | Livres -.xlsx row 21 | auteur non renseigne -> 'Inconnu' |
| `BOOK-J-0008` | Livres -.xlsx row 22 | par defaut |
| `BOOK-R-0002` | Livres -.xlsx row 23 | par defaut |
| `BOOK-A-0001` | Livres -.xlsx row 24 | editeur non renseigne -> 'Inconnu' |
| `BOOK-F-0001` | Livres -.xlsx row 25 | par defaut |
| `BOOK-J-0009` | Livres -.xlsx row 26 | par defaut |
| `PARA-B-0001` | Livres -.xlsx row 27 | reclassifie BOOK->PARA (magazine) |
| `PARA-I-0001` | Livres -.xlsx row 28 | reclassifie BOOK->PARA (magazine) |
| `PARA-I-0002` | Livres -.xlsx row 29 | reclassifie BOOK->PARA (magazine) |
| `BOOK-R-0003` | Livres -.xlsx row 30 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `PARA-E-0001` | Livres -.xlsx row 31 | reclassifie BOOK->PARA (magazine) |
| `BOOK-S-0002` | Livres -.xlsx row 32 | par defaut |
| `BOOK-J-0010` | Livres -.xlsx row 33 | par defaut |
| `BOOK-0-0002` | Livres -.xlsx row 38 | auteur non renseigne -> 'Inconnu' |
| `BOOK-A-0002` | Livres -.xlsx row 39 | annee de publication non parsee -> 1900 (sentinel); langue non mappee: 'Italien\nanglais' -> 'fr' |
| `BOOK-I-0004` | Livres -.xlsx row 40 | editeur non renseigne -> 'Inconnu' |
| `BOOK-B-0001` | Livres -.xlsx row 41 | par defaut |
| `BOOK-C-0001` | Livres -.xlsx row 42 | par defaut |
| `BOOK-D-0001` | Livres -.xlsx row 43 | par defaut |
| `BOOK-D-0002` | Livres -.xlsx row 44 | par defaut |
| `BOOK-F-0002` | Livres -.xlsx row 45 | par defaut |
| `BOOK-F-0003` | Livres -.xlsx row 46 | par defaut |
| `BOOK-F-0004` | Livres -.xlsx row 47 | editeur non renseigne -> 'Inconnu'; annee de publication non parsee -> 1900 (sentinel) |
| `BOOK-F-0005` | Livres -.xlsx row 48 | par defaut |
| `BOOK-R-0004` | Livres -.xlsx row 49 | par defaut |
| `BOOK-F-0006` | Livres -.xlsx row 50 | par defaut |
| `BOOK-F-0007` | Livres -.xlsx row 51 | langue non mappee: 'italien\nanglais' -> 'fr' |
| `BOOK-H-0003` | Livres -.xlsx row 52 | par defaut |
| `BOOK-I-0005` | Livres -.xlsx row 53 | langue non mappee: 'portugais\nanglais' -> 'fr' |
| `BOOK-J-0011` | Livres -.xlsx row 54 | langue non mappee: 'italien\nanglais' -> 'fr' |
| `BOOK-J-0012` | Livres -.xlsx row 55 | par defaut |
| `BOOK-J-0013` | Livres -.xlsx row 56 | par defaut |
| `BOOK-J-0014` | Livres -.xlsx row 57 | editeur non renseigne -> 'Inconnu' |
| `BOOK-J-0015` | Livres -.xlsx row 58 | par defaut |
| `BOOK-J-0016` | Livres -.xlsx row 59 | par defaut |
| `BOOK-J-0017` | Livres -.xlsx row 60 | auteur non renseigne -> 'Inconnu'; annee de publication non parsee -> 1900 (sentinel) |
| `BOOK-J-0018` | Livres -.xlsx row 61 | par defaut |
| `BOOK-J-0019` | Livres -.xlsx row 62 | par defaut |
| `BOOK-J-0020` | Livres -.xlsx row 63 | par defaut |
| `BOOK-J-0021` | Livres -.xlsx row 64 | auteur non renseigne -> 'Inconnu' |
| `BOOK-J-0022` | Livres -.xlsx row 65 | par defaut |
| `BOOK-J-0023` | Livres -.xlsx row 66 | par defaut |
| `BOOK-M-0002` | Livres -.xlsx row 67 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu'; annee de publication non parsee -> 1900 (sentinel) |
| `BOOK-M-0003` | Livres -.xlsx row 68 | par defaut |
| `BOOK-N-0002` | Livres -.xlsx row 69 | par defaut |
| `BOOK-O-0001` | Livres -.xlsx row 70 | par defaut |
| `PARA-P-0001` | Livres -.xlsx row 71 | reclassifie BOOK->PARA (misc) |
| `BOOK-J-0024` | Livres -.xlsx row 72 | editeur non renseigne -> 'Inconnu' |
| `BOOK-N-0003` | Livres -.xlsx row 73 | editeur non renseigne -> 'Inconnu' |
| `BOOK-S-0003` | Livres -.xlsx row 74 | par defaut |
| `BOOK-S-0004` | Livres -.xlsx row 75 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu'; annee de publication non parsee -> 1900 (sentinel) |
| `BOOK-S-0005` | Livres -.xlsx row 76 | par defaut |
| `BOOK-T-0001` | Livres -.xlsx row 77 | par defaut |
| `BOOK-T-0002` | Livres -.xlsx row 78 | par defaut |
| `BOOK-T-0003` | Livres -.xlsx row 79 | par defaut |
| `BOOK-T-0004` | Livres -.xlsx row 80 | langue non mappee: 'italien\nanglais' -> 'fr' |
| `BOOK-T-0005` | Livres -.xlsx row 81 | par defaut |
| `BOOK-U-0002` | Livres -.xlsx row 82 | par defaut |
| `BOOK-W-0001` | Livres -.xlsx row 83 | editeur non renseigne -> 'Inconnu' |
| `BOOK-W-0002` | Livres -.xlsx row 84 | editeur non renseigne -> 'Inconnu'; annee de publication non parsee -> 1900 (sentinel) |
| `BOOK-W-0003` | Livres -.xlsx row 85 | editeur non renseigne -> 'Inconnu' |
| `BOOK-A-0003` | Livres -.xlsx row 86 | par defaut |
| `PARA-M-0001` | Livres -.xlsx row 87 | reclassifie BOOK->PARA (magazine) |
| `PARA-U-0001` | Livres -.xlsx row 88 | reclassifie BOOK->PARA (magazine) |
| `BOOK-N-0004` | Livres -.xlsx row 89 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu'; annee de publication non parsee -> 1900 (sentinel) |
| `BOOK-N-0005` | Livres -.xlsx row 90 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `BOOK-H-0004` | Livres -.xlsx row 91 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu'; annee de publication non parsee -> 1900 (sentinel) |
| `BOOK-H-0005` | Livres -.xlsx row 92 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu'; annee de publication non parsee -> 1900 (sentinel) |
| `BOOK-N-0006` | Livres -.xlsx row 93 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `BOOK-A-0004` | Livres -.xlsx row 94 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `BOOK-B-0002` | Livres -.xlsx row 95 | auteur non renseigne -> 'Inconnu'; annee de publication non parsee -> 1900 (sentinel) |
| `BOOK-C-0002` | Livres -.xlsx row 96 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu'; annee de publication non parsee -> 1900 (sentinel) |
| `BOOK-D-0003` | Livres -.xlsx row 97 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `PARA-D-0001` | Livres -.xlsx row 98 | reclassifie BOOK->PARA (fanzine) |
| `BOOK-F-0008` | Livres -.xlsx row 99 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `BOOK-F-0009` | Livres -.xlsx row 100 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `BOOK-I-0006` | Livres -.xlsx row 101 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `BOOK-I-0007` | Livres -.xlsx row 102 | editeur non renseigne -> 'Inconnu' |
| `BOOK-J-0025` | Livres -.xlsx row 103 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `BOOK-J-0026` | Livres -.xlsx row 104 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `BOOK-L-0001` | Livres -.xlsx row 105 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `BOOK-P-0001` | Livres -.xlsx row 106 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `BOOK-R-0005` | Livres -.xlsx row 107 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `BOOK-R-0006` | Livres -.xlsx row 108 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu' |
| `BOOK-U-0003` | Livres -.xlsx row 109 | editeur non renseigne -> 'Inconnu' |
| `BOOK-F-0010` | Livres -.xlsx row 110 | par defaut |
| `BOOK-H-0006` | Livres -.xlsx row 111 | editeur non renseigne -> 'Inconnu'; annee de publication non parsee -> 1900 (sentinel) |
| `BOOK-I-0008` | Livres -.xlsx row 112 | editeur non renseigne -> 'Inconnu' |
| `BOOK-I-0009` | Livres -.xlsx row 113 | editeur non renseigne -> 'Inconnu' |
| `BOOK-W-0004` | Livres -.xlsx row 114 | par defaut |
| `BOOK-S-0006` | Livres -.xlsx row 115 | par defaut |
| `BOOK-A-0005` | Livres -.xlsx row 116 | auteur non renseigne -> 'Inconnu' |
| `BOOK-C-0003` | Livres -.xlsx row 117 | par defaut |
| `BOOK-D-0004` | Livres -.xlsx row 118 | auteur non renseigne -> 'Inconnu'; editeur non renseigne -> 'Inconnu'; langue non mappee: 'grec' -> 'fr' |
| `BOOK-D-0005` | Livres -.xlsx row 119 | auteur non renseigne -> 'Inconnu' |
| `BOOK-J-0027` | Livres -.xlsx row 120 | par defaut |
| `BOOK-J-0028` | Livres -.xlsx row 121 | par defaut |
| `BOOK-I-0010` | Livres -.xlsx row 122 | par defaut |
| `BOOK-I-0011` | Livres -.xlsx row 123 | editeur non renseigne -> 'Inconnu' |
| ... | ... | (+74 autres) |

## XLSX non traites (layout inconnu)

Aucun.

