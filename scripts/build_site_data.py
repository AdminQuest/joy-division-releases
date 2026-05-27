#!/usr/bin/env python3
"""Construit le JSON consolide consomme par l'interface publique.

Pipeline :
  1. Parcourt data/variants/*.yml.
  2. Pour chaque variant, applique un filtre de visibilite publique :
     - inclut le tronc commun et format_details ;
     - exclut les champs prefixes par '_' sauf _legacy_code dont seul
       'reconstructed' est conserve.
  3. Agrege en site/data/all-variants.json avec un manifeste de version,
     un timestamp, et trois index recapitulatifs (release_types,
     joydiv_letters, variant_groups).

Le JSON resultant est servi tel quel par GitHub Pages et consomme par
site/app.js cote navigateur.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
VARIANTS_DIR = ROOT / "data" / "variants"
OUTPUT_PATH = ROOT / "site" / "data" / "all-variants.json"

# Champs prefixes par '_' qui restent dans le JSON public sous forme
# filtree. Pour chacun, indique la whitelist de sous-cles a conserver.
INTERNAL_FIELDS_KEEP = {
    "_legacy_code": {"reconstructed"},
}


def public_view(variant: dict) -> dict:
    """Applique le filtre de visibilite publique."""
    out: dict = {}
    for key, value in variant.items():
        if key.startswith("_"):
            if key in INTERNAL_FIELDS_KEEP:
                allowed = INTERNAL_FIELDS_KEEP[key]
                if isinstance(value, dict):
                    sub = {k: v for k, v in value.items() if k in allowed}
                    if sub:
                        out[key] = sub
            # autres champs prefixes par '_' : exclus
            continue
        out[key] = value
    return out


def build_groups_index(variants: list[dict]) -> list[dict]:
    """Indexe les variant_group uniques avec leur count."""
    groups: dict[str, dict] = {}
    for v in variants:
        vg = v.get("variant_group")
        if not vg:
            continue
        gid = vg.get("group_id")
        if not gid:
            continue
        if gid not in groups:
            groups[gid] = {
                "group_id": gid,
                "group_role": vg.get("group_role"),
                "group_description": vg.get("group_description"),
                "count": 0,
            }
        groups[gid]["count"] += 1
    return sorted(groups.values(), key=lambda g: (-g["count"], g["group_id"]))


def build_release_types_index(variants: list[dict]) -> list[dict]:
    counter = Counter(v.get("release_type") for v in variants)
    return [
        {"release_type": k, "count": n}
        for k, n in sorted(counter.items(), key=lambda x: -x[1])
        if k is not None
    ]


def build_letters_index(variants: list[dict]) -> list[dict]:
    counter = Counter(v.get("joydiv_letter") for v in variants)
    return [
        {"letter": k, "count": n}
        for k, n in sorted(counter.items(), key=lambda x: (x[0] is None, x[0]))
        if k is not None
    ]


def main() -> int:
    if not VARIANTS_DIR.is_dir():
        print(f"FATAL: {VARIANTS_DIR} introuvable", file=sys.stderr)
        return 1

    paths = sorted(VARIANTS_DIR.glob("*.yml"))
    if not paths:
        print(f"FATAL: aucun YAML sous {VARIANTS_DIR}", file=sys.stderr)
        return 1

    variants: list[dict] = []
    for path in paths:
        data = yaml.safe_load(path.read_text())
        if not isinstance(data, dict):
            print(f"WARN: {path.name} n'est pas un objet YAML, ignore", file=sys.stderr)
            continue
        variants.append(public_view(data))

    payload = {
        "version": "1.0",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "total_variants": len(variants),
        "release_types": build_release_types_index(variants),
        "joydiv_letters": build_letters_index(variants),
        "variant_groups": build_groups_index(variants),
        "variants": variants,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    size_bytes = OUTPUT_PATH.stat().st_size
    print(f"variants ecrits : {len(variants)}")
    print(f"variant_groups : {len(payload['variant_groups'])}")
    print(f"release_types : {len(payload['release_types'])}")
    print(f"joydiv_letters : {len(payload['joydiv_letters'])}")
    print(f"taille JSON : {size_bytes:,} octets ({size_bytes / 1_000_000:.2f} Mo)")
    print(f"sortie : {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
