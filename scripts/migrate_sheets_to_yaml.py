#!/usr/bin/env python3
"""Migre les XLSX legacy degonfles vers YAML variants + ownerships.

Pipeline :
  1. Lit scripts/layouts.yml pour le mapping fichier -> positions de colonnes.
  2. Lit scripts/audio_format_patterns.yml pour le parsing des formats libres.
  3. Pour chaque XLSX dans /home/user/_legacy_dump/slimmed/ :
       - Categorise par nom de fichier (bootleg / officiel_or_pirate / video /
         coffret_skip / livre).
       - Pour chaque ligne : determine release_type, lettre du variant_id,
         numero sequentiel par (prefix, lettre), legacy_code reconstruit a
         partir des cellules consecutives.
       - Construit un YAML conforme a variant.schema.json.
       - Si owned == True, construit aussi un YAML conforme a
         ownership.schema.json (avec acquired_at omis, convention 2000-NNN).
       - Valide chaque YAML immediatement contre son schema. Stop si echec.
  4. Ecrit le rapport detaille dans /home/user/_legacy_dump/migration_report.md
     et la table d'audit dans data/_migration/legacy_mapping.csv.

Conformement a la consigne, ce script :
  - Ne touche pas a la branche de joy-division-collection.
  - Ne commit aucun YAML : les sorties restent locales pour relecture.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from openpyxl import load_workbook


# ---------------------------------------------------------------------------
# Constantes de chemins
# ---------------------------------------------------------------------------

REPO_RELEASES = Path("/home/user/joy-division-releases")
REPO_COLLECTION = Path("/home/user/joy-division-collection")
SLIM_DIR = Path("/home/user/_legacy_dump/slimmed")
REPORT_PATH = Path("/home/user/_legacy_dump/migration_report.md")
MAPPING_DIR = REPO_RELEASES / "data" / "_migration"
MAPPING_CSV = MAPPING_DIR / "legacy_mapping.csv"
VARIANTS_DIR = REPO_RELEASES / "data" / "variants"
OWNERSHIP_DIR = REPO_COLLECTION / "data" / "ownership"

LAYOUTS_YML = REPO_RELEASES / "scripts" / "layouts.yml"
PATTERNS_YML = REPO_RELEASES / "scripts" / "audio_format_patterns.yml"

VARIANT_SCHEMA_PATH = REPO_RELEASES / "schema" / "variant.schema.json"
OWNERSHIP_SCHEMA_PATH = REPO_COLLECTION / "schema" / "ownership.schema.json"


# ---------------------------------------------------------------------------
# Mapping linguistique pour les livres
# ---------------------------------------------------------------------------

LANGUAGE_MAP = {
    "français": "fr",
    "francais": "fr",
    "fr": "fr",
    "anglais": "en",
    "english": "en",
    "en": "en",
    "allemand": "de",
    "deutsch": "de",
    "de": "de",
    "italien": "it",
    "italiano": "it",
    "it": "it",
    "espagnol": "es",
    "español": "es",
    "es": "es",
    "néerlandais": "nl",
    "nederlands": "nl",
    "nl": "nl",
}

ARTICLES = ["The ", "A ", "An ", "Le ", "La ", "Les ", "L'", "Un ", "Une "]

SUFFIX_PATTERN = re.compile(r"^[a-e]$")


# ---------------------------------------------------------------------------
# Categorisation par nom de fichier (point 6 du brief)
# ---------------------------------------------------------------------------


def categorize(filename: str) -> tuple[str, str | None]:
    """Retourne (category, prefix).

    category in {bootleg, video, coffret_skip, officiel_or_pirate, livre, unknown}.
    prefix is the variant_id prefix (BOOT, VID, OFF/PIR will be determined per row, etc.)
    or None for skipped categories.
    """
    if filename.startswith("Bootlegs - "):
        return ("bootleg", "BOOT")
    if filename == "Officiels et pirates - VHS & DVD.xlsx":
        return ("video", "VID")
    if filename == "Officiels et pirates - Coffrets.xlsx":
        return ("coffret_skip", None)
    if filename.startswith("Officiels et pirates - "):
        # Y compris "7_ flexi - Komakino" : reste officiel/pirate audio.
        return ("officiel_or_pirate", "OFF_or_PIR")
    if filename.startswith("Livres -"):
        return ("livre", "BOOK")
    return ("unknown", None)


# ---------------------------------------------------------------------------
# Calcul de la lettre du variant_id (regle de tri)
# ---------------------------------------------------------------------------


def compute_letter(title: str | None) -> str | None:
    """Retourne la lettre A..Z ou "0", None si titre vide."""
    if not title:
        return None
    cleaned = str(title).strip()
    if not cleaned:
        return None
    for art in ARTICLES:
        if cleaned.lower().startswith(art.lower()):
            cleaned = cleaned[len(art):].strip()
            break
    if not cleaned:
        return None
    first = cleaned[0].upper()
    if "A" <= first <= "Z":
        return first
    return "0"


# ---------------------------------------------------------------------------
# Lecture des cellules robuste
# ---------------------------------------------------------------------------


def cell_value(ws, row: int, col: int):
    if col is None:
        return None
    cell = ws.cell(row=row, column=col)
    return cell.value


def cell_link(ws, row: int, col: int) -> str | None:
    if col is None:
        return None
    cell = ws.cell(row=row, column=col)
    if cell.hyperlink and cell.hyperlink.target:
        return cell.hyperlink.target
    return None


def parse_year(value) -> int | None:
    if value is None:
        return None
    s = str(value)
    m = re.search(r"\b(19[7-9][0-9]|20[0-3][0-9])\b", s)
    if not m:
        return None
    year = int(m.group(1))
    if 1976 <= year <= 2030:
        return year
    return None


def parse_price_eur(value) -> float | None:
    """Cote/COTE : peut etre 480, '480 + 120 € TVA', '110 £', '/40'.

    On extrait un nombre uniquement si la chaine ressemble a un prix
    (avec un symbole monetaire ou un format clairement numerique).
    Les '/N' (numero de tirage) ne sont PAS un prix.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if value > 0:
            return float(value)
        return None
    s = str(value).strip()
    if not s or s.startswith("/") or s.startswith("#"):
        return None
    m = re.match(r"^\s*(\d+(?:[.,]\d+)?)", s)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", "."))
    except ValueError:
        return None


def parse_copy_number(value) -> str | None:
    """Colonne 'LE' : numero de tirage ou edition limitee.

    Exemples : '/40', '#185/200', '/315', '1500 copies, the first 300...'
    On retourne la chaine telle quelle si elle ressemble a un numero,
    None si vide ou clairement descriptive.
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    # Garde tout sauf si c'est une longue description (>40 chars)
    if len(s) > 40:
        return None
    return s


# ---------------------------------------------------------------------------
# Parsing du format audio
# ---------------------------------------------------------------------------


class AudioFormatParser:
    def __init__(self, patterns_data: dict):
        self.patterns = []
        for entry in patterns_data.get("patterns", []):
            self.patterns.append({
                "regex": re.compile(entry["regex"]),
                "result": entry["result"],
            })
        self.mixed_patterns = [
            re.compile(p) for p in patterns_data.get("mixed_audio_video_patterns", [])
        ]
        self.video_patterns = []
        for entry in patterns_data.get("video_patterns", []):
            self.video_patterns.append({
                "regex": re.compile(entry["regex"]),
                "support_type": entry["support_type"],
            })

    def is_mixed_audio_video(self, format_str: str) -> bool:
        if not format_str:
            return False
        for p in self.mixed_patterns:
            if p.search(format_str):
                return True
        return False

    def parse_audio(self, format_str: str, version_str: str | None = None) -> tuple[dict | None, bool]:
        """Retourne (support_dict, matched_cleanly).

        Si aucun pattern ne matche, retourne ({vinyl, 1}, False) pour
        marquer needs_review.
        """
        if not format_str:
            return ({"support_type": "vinyl", "count": 1}, False)
        s = str(format_str).strip()
        for entry in self.patterns:
            m = entry["regex"].search(s)
            if m:
                result = dict(entry["result"])
                if "count_group" in result:
                    grp_idx = result.pop("count_group")
                    try:
                        count_str = m.group(grp_idx)
                        result["count"] = int(count_str) if count_str else 1
                    except (IndexError, ValueError, TypeError):
                        result["count"] = 1
                if "count" not in result:
                    result["count"] = 1
                # Surcharge color depuis version_str (priorite a une color
                # explicite dans Version).
                if version_str:
                    vs = str(version_str).strip()
                    if vs and "color" not in result:
                        # On garde la version comme color brute, sera
                        # nettoyee plus tard si besoin.
                        if len(vs) <= 60:
                            result["color"] = vs
                return (result, True)
        return ({"support_type": "vinyl", "count": 1}, False)

    def parse_video(self, format_str: str) -> tuple[dict, bool]:
        if not format_str:
            return ({"support_type": "dvd", "count": 1}, False)
        s = str(format_str)
        for entry in self.video_patterns:
            if entry["regex"].search(s):
                count = 1
                # Try to extract leading count
                m = re.match(r"^\s*(\d+)\s*[xX]?", s)
                if m:
                    try:
                        count = int(m.group(1))
                    except ValueError:
                        count = 1
                return ({"support_type": entry["support_type"], "count": count}, True)
        return ({"support_type": "dvd", "count": 1}, False)


# ---------------------------------------------------------------------------
# Construction des YAML
# ---------------------------------------------------------------------------


def build_legacy_code(ws, row: int, layout: dict) -> dict:
    """Lit 4 cellules consecutives a partir de layout.legacy_code_start."""
    start = layout.get("legacy_code_start")
    if start is None:
        return {
            "segments": [],
            "reconstructed": "",
            "has_suffix": False,
            "source_xlsx": None,  # rempli par appelant
            "source_row": row,
        }
    segments = []
    for c in range(start, start + 4):
        v = cell_value(ws, row, c)
        if v is None:
            segments.append(None)
        else:
            segments.append(str(v).strip())
    last = segments[-1] if segments else None
    has_suffix = bool(last and SUFFIX_PATTERN.match(last))
    reconstructed = "".join(s for s in segments if s is not None and s)
    return {
        "segments": segments,
        "reconstructed": reconstructed,
        "has_suffix": has_suffix,
    }


def build_variant_audio(
    ws,
    row: int,
    layout: dict,
    title: str,
    year: int | None,
    parser: AudioFormatParser,
) -> tuple[dict, bool, list[str]]:
    """Construit format_details pour audio. Retourne (format_details, clean, issues)."""
    issues = []
    format_str = cell_value(ws, row, layout.get("format"))
    version_str = cell_value(ws, row, layout.get("version"))
    label_str = cell_value(ws, row, layout.get("label"))
    matrices_str = cell_value(ws, row, layout.get("matrices"))

    support, matched = parser.parse_audio(format_str, version_str)
    if not matched:
        issues.append(f"format audio non parse: {format_str!r}")

    audio_format: dict = {
        "type": "audio",
        "supports": [support],
    }
    if label_str:
        s = str(label_str).strip()
        if s and len(s) <= 200:
            audio_format["label_apparent"] = s

    # matrices : on les met dans le 1er support
    if matrices_str:
        matrices = [
            m.strip()
            for m in re.split(r"[\n;,]+", str(matrices_str))
            if m.strip()
        ]
        if matrices:
            support["matrices"] = matrices[:20]  # cap a 20 entrees

    return (audio_format, matched, issues)


def build_variant_video(
    ws,
    row: int,
    layout: dict,
    parser: AudioFormatParser,
) -> tuple[dict, bool, list[str]]:
    issues = []
    format_str = cell_value(ws, row, layout.get("format"))
    support, matched = parser.parse_video(format_str)
    if not matched:
        issues.append(f"format video non parse: {format_str!r}")
    video_format = {
        "type": "video",
        "supports": [support],
    }
    return (video_format, matched, issues)


def build_variant_book(ws, row: int, layout: dict) -> tuple[dict, list[str]]:
    """Construit book_format depuis le layout livre."""
    issues = []
    author = cell_value(ws, row, layout.get("author"))
    publisher = cell_value(ws, row, layout.get("publisher"))
    language_raw = cell_value(ws, row, layout.get("language"))
    year_raw = cell_value(ws, row, layout.get("year"))
    pages_raw = cell_value(ws, row, layout.get("pages"))
    isbn = cell_value(ws, row, layout.get("isbn"))

    # Auteurs : split sur "et", "&", ","
    if author:
        authors = [
            a.strip()
            for a in re.split(r"\s*(?:,|&|\bet\b)\s*", str(author))
            if a.strip()
        ]
        if not authors:
            authors = ["Inconnu"]
            issues.append("auteur vide -> 'Inconnu'")
    else:
        authors = ["Inconnu"]
        issues.append("auteur non renseigne -> 'Inconnu'")

    if not publisher:
        publisher = "Inconnu"
        issues.append("editeur non renseigne -> 'Inconnu'")
    else:
        publisher = str(publisher).strip()

    pub_year = parse_year(year_raw)
    if pub_year is None:
        pub_year = 2000
        issues.append("annee de publication non parsee -> 2000")

    lang_norm = "fr"  # default
    if language_raw:
        key = str(language_raw).strip().lower()
        lang_norm = LANGUAGE_MAP.get(key, "fr")
        if key not in LANGUAGE_MAP:
            issues.append(f"langue non mappee: {language_raw!r} -> 'fr'")

    book_format = {
        "type": "book",
        "authors": authors,
        "publisher": publisher,
        "publication_year": pub_year,
        "language": lang_norm,
        "format_physical": "softcover",
        "illustrations": True,
        "has_appendices": False,
    }

    # Champs optionnels
    if isbn:
        isbn_str = str(isbn).strip()
        # ISBN-13
        m13 = re.match(r"^(97[89])[-\s]?([\d\-]+)$", isbn_str)
        if m13:
            book_format["isbn_13"] = f"{m13.group(1)}-{m13.group(2).replace(' ', '')}"
        elif re.match(r"^[\dX\-]+$", isbn_str):
            book_format["isbn_10"] = isbn_str.replace(" ", "")

    if pages_raw is not None:
        try:
            book_format["page_count"] = int(pages_raw)
        except (TypeError, ValueError):
            pass

    return (book_format, issues)


# ---------------------------------------------------------------------------
# Determination release_type par cellule O/P
# ---------------------------------------------------------------------------


def determine_op(ws, row: int, op_col: int | None) -> tuple[str, str, bool]:
    """Retourne (release_type, prefix, op_uncertain)."""
    if op_col is None:
        # Pas de colonne O/P : pas applicable (ex. bootlegs, livres)
        return ("officiel", "OFF", False)
    val = cell_value(ws, row, op_col)
    if val is None:
        return ("officiel", "OFF", True)
    s = str(val).strip().upper()
    if s.startswith("O"):
        return ("officiel", "OFF", False)
    if s.startswith("P"):
        return ("pirate", "PIR", False)
    return ("officiel", "OFF", True)


# ---------------------------------------------------------------------------
# Validation inline
# ---------------------------------------------------------------------------


class Validators:
    def __init__(self):
        variant_schema = json.loads(VARIANT_SCHEMA_PATH.read_text())
        ownership_schema = json.loads(OWNERSHIP_SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(variant_schema)
        Draft202012Validator.check_schema(ownership_schema)
        self.variant = Draft202012Validator(
            variant_schema, format_checker=Draft202012Validator.FORMAT_CHECKER
        )
        self.ownership = Draft202012Validator(
            ownership_schema, format_checker=Draft202012Validator.FORMAT_CHECKER
        )

    def check_variant(self, data: dict) -> list[str]:
        return [
            f"{list(e.absolute_path)}: {e.message}"
            for e in self.variant.iter_errors(data)
        ]

    def check_ownership(self, data: dict) -> list[str]:
        return [
            f"{list(e.absolute_path)}: {e.message}"
            for e in self.ownership.iter_errors(data)
        ]


# ---------------------------------------------------------------------------
# Detection fin de donnees
# ---------------------------------------------------------------------------


def is_empty_row(ws, row: int, layout: dict) -> bool:
    """Une ligne est consideree vide si owned, title et legacy_code_start sont tous None."""
    checks = [layout.get("owned"), layout.get("title"), layout.get("legacy_code_start")]
    for c in checks:
        if c is not None:
            if cell_value(ws, row, c) is not None:
                return False
    return True


# ---------------------------------------------------------------------------
# Main migration
# ---------------------------------------------------------------------------


def main() -> int:
    # Nettoyage des sorties precedentes
    for d in (VARIANTS_DIR, OWNERSHIP_DIR, MAPPING_DIR):
        d.mkdir(parents=True, exist_ok=True)
    for f in VARIANTS_DIR.glob("*.yml"):
        f.unlink()
    for f in OWNERSHIP_DIR.glob("*.yml"):
        f.unlink()
    if MAPPING_CSV.exists():
        MAPPING_CSV.unlink()

    layouts_doc = yaml.safe_load(LAYOUTS_YML.read_text())
    patterns_doc = yaml.safe_load(PATTERNS_YML.read_text())
    parser = AudioFormatParser(patterns_doc)
    validators = Validators()

    layouts = layouts_doc.get("layouts", {})
    xlsx_files = sorted(SLIM_DIR.glob("*.xlsx"))

    # Compteurs
    variant_seq: dict[tuple[str, str], int] = defaultdict(int)
    ownership_seq: dict[int, int] = defaultdict(int)
    variants_by_prefix: dict[str, int] = defaultdict(int)
    ownerships_by_prefix: dict[str, int] = defaultdict(int)
    boot_letter_count: dict[str, int] = defaultdict(int)
    quality_count: dict[str, int] = defaultdict(int)
    files_count: dict[str, int] = defaultdict(int)

    rejects: list[dict] = []
    needs_review_list: list[dict] = []
    coffret_skipped: list[dict] = []
    unknown_layout_files: list[dict] = []
    mapping_rows: list[dict] = []

    total_variants = 0
    total_ownerships = 0
    total_xlsx = 0

    for xlsx_path in xlsx_files:
        name = xlsx_path.name
        layout = layouts.get(name)
        if not layout:
            unknown_layout_files.append({"file": name, "reason": "absent de layouts.yml"})
            continue
        category, prefix_hint = categorize(name)
        if category == "unknown":
            unknown_layout_files.append({"file": name, "reason": "category=unknown"})
            continue

        print(f"[XLSX] {name}  (layout={layout.get('layout_id')}, cat={category})")
        total_xlsx += 1

        wb = load_workbook(xlsx_path, data_only=True)
        ws = wb.active
        max_row = ws.max_row
        empty_streak = 0

        for row in range(2, max_row + 1):
            if is_empty_row(ws, row, layout):
                empty_streak += 1
                if empty_streak >= 20:
                    break
                continue
            empty_streak = 0

            # --- Categorie : coffret_skip ---
            if category == "coffret_skip":
                title_val = cell_value(ws, row, layout.get("title"))
                title_str = str(title_val).strip() if title_val else None
                coffret_skipped.append({
                    "file": name, "row": row,
                    "title": title_str or "(titre vide)",
                })
                continue

            # --- Titre ---
            if category == "livre":
                title_val = cell_value(ws, row, layout.get("title"))
            else:
                title_val = cell_value(ws, row, layout.get("title"))
            title = str(title_val).strip() if title_val else ""
            if not title:
                rejects.append({
                    "file": name, "row": row,
                    "reason": "titre vide",
                })
                continue

            letter = compute_letter(title)
            if letter is None:
                rejects.append({
                    "file": name, "row": row,
                    "reason": "lettre indeterminable",
                })
                continue

            # --- release_type et prefix ---
            issues: list[str] = []
            if category == "bootleg":
                release_type, prefix = "bootleg", "BOOT"
            elif category == "video":
                release_type, prefix = "video", "VID"
            elif category == "livre":
                release_type, prefix = "livre", "BOOK"
            elif category == "officiel_or_pirate":
                release_type, prefix, op_uncertain = determine_op(
                    ws, row, layout.get("op_column")
                )
                if op_uncertain:
                    issues.append("cellule O/P vide ou non reconnue -> OFF par defaut")
            else:
                rejects.append({"file": name, "row": row, "reason": f"category={category}"})
                continue

            # --- format mixte audio+video -> bascule en coffret_skip ---
            if category in ("bootleg", "officiel_or_pirate"):
                fmt_str = cell_value(ws, row, layout.get("format"))
                if fmt_str and parser.is_mixed_audio_video(str(fmt_str)):
                    coffret_skipped.append({
                        "file": name, "row": row,
                        "title": title,
                        "reason": "format mixte audio+video",
                    })
                    continue

            # --- numerotation ---
            variant_seq[(prefix, letter)] += 1
            seq = variant_seq[(prefix, letter)]
            variant_id = f"{prefix}-{letter}-{seq:04d}"

            # --- annee ---
            year = parse_year(cell_value(ws, row, layout.get("year")))

            # --- legacy_code ---
            legacy_code = build_legacy_code(ws, row, layout)
            legacy_code["source_xlsx"] = name
            legacy_code["source_row"] = row

            # --- format_details ---
            cleanly_parsed = True
            if release_type in ("bootleg", "officiel", "pirate"):
                fd, matched, fmt_issues = build_variant_audio(
                    ws, row, layout, title,
                    year if year else None,
                    parser,
                )
                if not matched:
                    cleanly_parsed = False
                    issues.extend(fmt_issues)
            elif release_type == "video":
                fd, matched, fmt_issues = build_variant_video(ws, row, layout, parser)
                if not matched:
                    cleanly_parsed = False
                    issues.extend(fmt_issues)
            elif release_type == "livre":
                fd, book_issues = build_variant_book(ws, row, layout)
                if book_issues:
                    issues.extend(book_issues)
                cleanly_parsed = False  # livres toujours en needs_review
            else:
                rejects.append({"file": name, "row": row, "reason": f"release_type={release_type}"})
                variant_seq[(prefix, letter)] -= 1
                continue

            # --- annee : fallback si manquante ---
            if year is None:
                year = 2000  # sentinel
                issues.append("annee non renseignee -> 2000 (placeholder)")
                cleanly_parsed = False

            # --- documentation_quality ---
            if release_type == "livre" or not cleanly_parsed or issues:
                doc_quality = "needs_review"
            else:
                doc_quality = "verified"

            # --- liens externes ---
            joydiv_url = cell_link(ws, row, layout.get("title")) or cell_link(ws, row, layout.get("personal_1") if layout.get("kind") == "audio_or_video" else None)
            discogs_url = cell_link(ws, row, layout.get("discogs"))

            # --- country ---
            country_val = cell_value(ws, row, layout.get("country"))
            country = str(country_val).strip() if country_val else None
            if country:
                # Strip emojis genre "🇺🇸 USA" -> "USA"
                country = re.sub(r"[^\x00-\x7F]", "", country).strip()
                if not country:
                    country = None

            # --- notes (commentaires) ---
            notes = None
            if layout.get("kind") == "audio_or_video":
                comments = cell_value(ws, row, layout.get("comments"))
                if comments:
                    s = str(comments).strip()
                    if s:
                        notes = s[:1000]
            elif layout.get("kind") == "book":
                summary = cell_value(ws, row, layout.get("summary"))
                if summary:
                    notes = str(summary).strip()[:1000]

            # --- variant doc ---
            variant_doc = {
                "variant_id": variant_id,
                "release_type": release_type,
                "canonical_title": title,
                "canonical_artist": "Joy Division",
                "year": year,
                "documentation_quality": doc_quality,
                "format_details": fd,
                "joydiv_letter": letter,
                "joydiv_url": joydiv_url,
                "discogs_url": discogs_url,
                "country_or_pressing_place": country,
                "notes": notes,
                "_legacy_code": legacy_code,
            }
            # Nettoyer les None facultatifs pour limiter le bruit YAML.
            for k in ["joydiv_url", "discogs_url", "country_or_pressing_place", "notes"]:
                if variant_doc.get(k) is None:
                    variant_doc.pop(k)

            # Validation immediate
            v_errors = validators.check_variant(variant_doc)
            if v_errors:
                msg = (
                    f"\n[FATAL] validation variant {variant_id} (source: {name} row {row})"
                    f"\n  Title: {title!r}"
                    f"\n  Errors:"
                )
                for e in v_errors:
                    msg += f"\n    - {e}"
                print(msg, file=sys.stderr)
                return 1

            # Ecrit le YAML
            out = VARIANTS_DIR / f"{variant_id}.yml"
            out.write_text(yaml.safe_dump(
                variant_doc, allow_unicode=True, sort_keys=False, width=120
            ))

            total_variants += 1
            variants_by_prefix[prefix] += 1
            quality_count[doc_quality] += 1
            files_count[name] += 1
            if prefix == "BOOT":
                boot_letter_count[letter] += 1
            if doc_quality == "needs_review":
                needs_review_list.append({
                    "variant_id": variant_id,
                    "source": f"{name} row {row}",
                    "reason": "; ".join(issues) if issues else "livre par defaut",
                })

            # --- ownership ---
            ownership_id = None
            owned_val = cell_value(ws, row, layout.get("owned"))
            owned = (str(owned_val).strip().upper() == "TRUE") if owned_val is not None else False
            if owned:
                # Annee d'acquisition non disponible -> 2000 par convention
                year_acq = 2000
                ownership_seq[year_acq] += 1
                seq_o = ownership_seq[year_acq]
                if seq_o > 999:
                    # On bascule sur l'annee+1 pour ne pas casser le pattern
                    year_acq += 1
                    ownership_seq[year_acq] += 1
                    seq_o = ownership_seq[year_acq]
                ownership_id = f"own-{year_acq:04d}-{seq_o:03d}"

                # personal photo
                photo_link = None
                if layout.get("kind") == "audio_or_video":
                    photo_link = cell_link(ws, row, layout.get("personal_1"))
                    if not photo_link:
                        photo_link = cell_link(ws, row, layout.get("personal_2"))

                price_paid = parse_price_eur(cell_value(ws, row, layout.get("cote")))
                copy_number = parse_copy_number(cell_value(ws, row, layout.get("limited")))

                ownership_doc = {
                    "ownership_id": ownership_id,
                    "variant_id": variant_id,
                }
                if price_paid is not None:
                    ownership_doc["price_paid_eur"] = price_paid
                if copy_number is not None:
                    ownership_doc["copy_number"] = copy_number
                if photo_link:
                    ownership_doc["personal_photos"] = [photo_link]
                if notes:
                    ownership_doc["notes"] = notes[:500]

                o_errors = validators.check_ownership(ownership_doc)
                if o_errors:
                    msg = (
                        f"\n[FATAL] validation ownership {ownership_id} (source: {name} row {row})"
                        f"\n  variant_id: {variant_id}"
                        f"\n  Errors:"
                    )
                    for e in o_errors:
                        msg += f"\n    - {e}"
                    print(msg, file=sys.stderr)
                    return 1

                out_o = OWNERSHIP_DIR / f"{ownership_id}.yml"
                out_o.write_text(yaml.safe_dump(
                    ownership_doc, allow_unicode=True, sort_keys=False, width=120
                ))
                total_ownerships += 1
                ownerships_by_prefix[prefix] += 1

            # Mapping CSV
            mapping_rows.append({
                "source_xlsx": name,
                "source_row": row,
                "legacy_code_reconstructed": legacy_code["reconstructed"],
                "variant_id": variant_id,
                "ownership_id": ownership_id or "",
                "release_type": release_type,
                "title": title,
            })

    # --- Ecrit le CSV ---
    with MAPPING_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "source_xlsx", "source_row", "legacy_code_reconstructed",
            "variant_id", "ownership_id", "release_type", "title",
        ])
        writer.writeheader()
        writer.writerows(mapping_rows)

    # --- Ecrit le rapport ---
    write_report(
        total_xlsx=total_xlsx,
        total_variants=total_variants,
        total_ownerships=total_ownerships,
        coffret_skipped=coffret_skipped,
        rejects=rejects,
        variants_by_prefix=variants_by_prefix,
        ownerships_by_prefix=ownerships_by_prefix,
        boot_letter_count=boot_letter_count,
        quality_count=quality_count,
        files_count=files_count,
        needs_review_list=needs_review_list,
        unknown_layout_files=unknown_layout_files,
    )

    print(f"\n--- Migration terminee ---")
    print(f"Variants : {total_variants}")
    print(f"Ownerships : {total_ownerships}")
    print(f"Rejets : {len(rejects)}")
    print(f"Coffrets skippes : {len(coffret_skipped)}")
    print(f"needs_review : {quality_count['needs_review']}")
    return 0


def write_report(**kw):
    now = dt.datetime.now().isoformat(timespec="seconds")
    out: list[str] = []
    out.append(f"# Rapport de migration — {now}\n")
    out.append("## Synthese\n")
    out.append(f"- XLSX lus : **{kw['total_xlsx']}**")
    out.append(f"- Variantes produites : **{kw['total_variants']}**")
    out.append(f"- Ownerships produits : **{kw['total_ownerships']}**")
    out.append(f"- Coffrets identifies (skippes) : **{len(kw['coffret_skipped'])}**")
    out.append(f"- Lignes XLSX rejetees : **{len(kw['rejects'])}**")
    out.append(f"- Erreurs de validation : **0** (sinon le script aurait stoppe)")
    out.append("")

    out.append("## Decomposition par prefixe\n")
    out.append("| Prefixe | Variantes | Ownerships |")
    out.append("|---|---:|---:|")
    for pfx in ["BOOT", "OFF", "PIR", "VID", "BOX", "BOOK", "PARA"]:
        out.append(f"| {pfx} | {kw['variants_by_prefix'].get(pfx, 0)} | {kw['ownerships_by_prefix'].get(pfx, 0)} |")
    out.append("")

    out.append("## Decomposition BOOT par lettre\n")
    out.append("| Lettre | Variantes |")
    out.append("|---|---:|")
    for letter in ["0"] + [chr(c) for c in range(ord("A"), ord("Z") + 1)]:
        out.append(f"| {letter} | {kw['boot_letter_count'].get(letter, 0)} |")
    out.append("")

    out.append("## Qualite de documentation\n")
    out.append("| Statut | Nombre |")
    out.append("|---|---:|")
    for q in ["verified", "needs_review", "stub"]:
        out.append(f"| {q} | {kw['quality_count'].get(q, 0)} |")
    out.append("")

    out.append("## Top 10 XLSX par variantes produites\n")
    out.append("| XLSX | Variantes |")
    out.append("|---|---:|")
    top10 = sorted(kw['files_count'].items(), key=lambda x: -x[1])[:10]
    for fname, n in top10:
        out.append(f"| {fname} | {n} |")
    out.append("")

    out.append(f"## Lignes rejetees ({len(kw['rejects'])} entrees)\n")
    if kw['rejects']:
        out.append("| XLSX | Ligne | Raison |")
        out.append("|---|---:|---|")
        for r in kw['rejects'][:100]:
            out.append(f"| {r['file']} | {r['row']} | {r['reason']} |")
        if len(kw['rejects']) > 100:
            out.append(f"| ... | ... | (+{len(kw['rejects'])-100} autres) |")
    else:
        out.append("Aucune.")
    out.append("")

    out.append(f"## Coffrets identifies pour seconde passe ({len(kw['coffret_skipped'])} entrees)\n")
    if kw['coffret_skipped']:
        out.append("| XLSX | Ligne | Titre potentiel |")
        out.append("|---|---:|---|")
        for c in kw['coffret_skipped'][:100]:
            out.append(f"| {c['file']} | {c['row']} | {c['title']} |")
        if len(kw['coffret_skipped']) > 100:
            out.append(f"| ... | ... | (+{len(kw['coffret_skipped'])-100} autres) |")
    else:
        out.append("Aucun.")
    out.append("")

    out.append(f"## Variants en needs_review ({len(kw['needs_review_list'])} entrees)\n")
    if kw['needs_review_list']:
        out.append("| variant_id | source | raison |")
        out.append("|---|---|---|")
        for r in kw['needs_review_list'][:150]:
            out.append(f"| `{r['variant_id']}` | {r['source']} | {r['reason']} |")
        if len(kw['needs_review_list']) > 150:
            out.append(f"| ... | ... | (+{len(kw['needs_review_list'])-150} autres) |")
    else:
        out.append("Aucun.")
    out.append("")

    out.append(f"## XLSX non traites (layout inconnu)\n")
    if kw['unknown_layout_files']:
        out.append("| XLSX | Raison |")
        out.append("|---|---|")
        for u in kw['unknown_layout_files']:
            out.append(f"| {u['file']} | {u['reason']} |")
    else:
        out.append("Aucun.")
    out.append("")

    REPORT_PATH.write_text("\n".join(out) + "\n")
    print(f"Rapport ecrit : {REPORT_PATH}")


if __name__ == "__main__":
    sys.exit(main())
