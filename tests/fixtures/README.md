# Fixtures de validation

Echantillons YAML utilises pour verifier que `schema/variant.schema.json` se
comporte comme attendu. Executes par `tests/validate_fixtures.py` :

```
python3 tests/validate_fixtures.py
```

## Contenu

### `valid/` (doivent passer la validation)

- **`bootleg_audio.yml`** — variante audio (`release_type: bootleg`) sur un
  vinyle 12" avec tracklist par face et matrices. Couvre `audio_format`,
  `audio_support`, `audio_content`, `audio_tracklist_side`, `audio_track`.
- **`video_dvd.yml`** — variante video (`release_type: video`) sur un DVD
  multi-region PAL avec chapitres. Couvre `video_format` et `video_support`.
- **`book.yml`** — variante livre (`release_type: livre`) avec ISBN-13 + 10,
  auteurs, dimensions, illustrations. Couvre `book_format`.

### `invalid/` (doivent etre rejetees)

- **`bad_variant_id.yml`** — `variant_id` invalide (prefixe inconnu, minuscule,
  3 chiffres au lieu de 4). Verifie le motif racine.
- **`wrong_format_details.yml`** — `release_type: video` avec un
  `format_details` de type `audio`. Verifie le discriminant
  `release_type -> format_details`.
- **`bad_isbn.yml`** — `isbn_13: 123-4567890123` (ne commence pas par 978/979).
  Verifie le motif ISBN-13 dans `book_format`.

## Note YAML

Plusieurs valeurs sont volontairement quoted pour echapper aux conversions
YAML 1.1 :
- les durees `mm:ss` (parsees sinon comme sexagesimal entier),
- les `aspect_ratio` style `4:3` (idem),
- les dates `release_date` (parsees sinon comme `datetime.date`, alors que le
  schema attend une string format `date`).
