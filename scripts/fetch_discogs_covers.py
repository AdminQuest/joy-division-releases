#!/usr/bin/env python3
"""Telecharge les pochettes Discogs des variantes du registre.

Spec A->F :
  A. Source : parcours data/variants/*.yml, extrait release_id depuis
     discogs_url via le pattern '(?:release|master)/(\\d+)'.
     Deduplique sur release_id (plusieurs variantes peuvent referencer
     la meme release).
  B. Fetch API : GET https://api.discogs.com/releases/{id} avec un
     User-Agent identifiant le projet (Discogs l'exige). Anonyme.
  C. Selection image : prend l'image marquee 'primary' si presente,
     sinon la premiere de la liste. Champ 'uri' (full-size).
  D. Download : enregistre sous site/covers/{release_id}.{ext},
     extension deduite du Content-Type. Idempotent : skip si le
     fichier existe deja.
  E. Index : ecrit site/data/covers-index.json mappant
     release_id -> chemin relatif (depuis site/).
  F. Rate-limit & reporting : 2.5 s entre requetes ; backoff
     exponentiel sur 429 (5 / 10 / 20 s, puis abandon) ; rapport
     final stdout avec totals et detail des echecs.

Le script est manuel. Le workflow GitHub Pages ne le relance pas a
chaque deploiement ; les covers sont commitees au repo.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
VARIANTS_DIR = ROOT / "data" / "variants"
COVERS_DIR = ROOT / "site" / "covers"
INDEX_PATH = ROOT / "site" / "data" / "covers-index.json"

USER_AGENT = (
    "JoyDivisionRegistry/1.0 "
    "(+https://github.com/adminquest/joy-division-releases)"
)
API_BASE = "https://api.discogs.com"
RATE_LIMIT_DELAY = 2.5  # secondes entre 2 requetes (anonyme = 25/min)
BACKOFFS_429 = (5, 10, 20)  # delais en cas de 429, puis abandon
BACKOFFS_NET = (2, 4, 8)    # delais sur erreur reseau / SSL transitoire

# Pattern unique pour les deux formes d'URL Discogs rencontrees :
#   .../release/{id}-Slug
#   .../Slug/release/{id}
RELEASE_ID_RE = re.compile(r"/(?:release|master)/(\d+)")

# Mapping Content-Type -> extension de fichier.
CONTENT_TYPE_EXT = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}


def extract_release_id(url: str) -> str | None:
    """Extrait l'ID Discogs (release ou master) depuis une URL."""
    if not url:
        return None
    m = RELEASE_ID_RE.search(url)
    return m.group(1) if m else None


def collect_release_ids() -> tuple[dict[str, list[str]], list[tuple[str, str]]]:
    """Parcourt les YAML et retourne :
      - mapping release_id -> [variant_id, ...] (pour reporting)
      - liste (variant_id, url) des URLs non parsables.
    """
    by_id: dict[str, list[str]] = defaultdict(list)
    unparseable: list[tuple[str, str]] = []
    for path in sorted(VARIANTS_DIR.glob("*.yml")):
        data = yaml.safe_load(path.read_text())
        if not isinstance(data, dict):
            continue
        url = data.get("discogs_url")
        if not url:
            continue
        rid = extract_release_id(url)
        vid = data.get("variant_id", path.stem)
        if rid is None:
            unparseable.append((vid, url))
            continue
        by_id[rid].append(vid)
    return by_id, unparseable


def http_get(url: str, accept: str) -> tuple[int, dict, bytes, str]:
    """GET avec User-Agent. Retourne (status, headers, body, error_msg).
    Les cles de headers sont normalisees en lowercase (Cloudflare et
    d'autres CDN renvoient les headers en lowercase, donc on s'aligne
    pour avoir un lookup deterministe). Sur HTTPError, retourne le
    code + body. Sur erreur reseau / SSL transitoire, retry avec
    backoff (2/4/8 s), puis renvoie status=0 et error_msg renseigne.
    """
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": accept},
    )
    last_err = ""
    for attempt in range(len(BACKOFFS_NET) + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                return resp.status, headers, resp.read(), ""
        except urllib.error.HTTPError as e:
            headers = {k.lower(): v for k, v in (e.headers or {}).items()}
            body = e.read() if hasattr(e, "read") else b""
            return e.code, headers, body, ""
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last_err = f"{type(e).__name__}: {e}"
            if attempt < len(BACKOFFS_NET):
                wait = BACKOFFS_NET[attempt]
                print(f"  [net-err] {last_err} -- retry dans {wait}s", flush=True)
                time.sleep(wait)
                continue
            return 0, {}, b"", last_err


def get_release_metadata(release_id: str) -> tuple[int, dict | None, str]:
    """Recupere les metadata d'une release avec backoff sur 429.
    Retourne (status_final, json_or_None, message_si_echec).
    """
    url = f"{API_BASE}/releases/{release_id}"
    attempt = 0
    while True:
        status, headers, body, net_err = http_get(url, accept="application/json")
        if net_err:
            return status, None, f"erreur reseau : {net_err}"
        if status == 200:
            try:
                return status, json.loads(body), ""
            except json.JSONDecodeError as e:
                return status, None, f"reponse JSON invalide : {e}"
        if status == 429 and attempt < len(BACKOFFS_429):
            wait = BACKOFFS_429[attempt]
            print(f"  [429] rate-limited, attente {wait}s...", flush=True)
            time.sleep(wait)
            attempt += 1
            continue
        # 404, 403, autres : echec definitif
        msg = body[:200].decode("utf-8", errors="replace") if body else ""
        return status, None, f"HTTP {status} : {msg.strip()}"


def pick_image_url(metadata: dict) -> str | None:
    """Selectionne l'URL de l'image principale.
    Priorite : image 'primary', sinon premiere de la liste.
    Champ 'uri' (full-size), pas 'uri150' (vignette).
    """
    images = metadata.get("images") or []
    if not images:
        return None
    primary = next((img for img in images if img.get("type") == "primary"), None)
    chosen = primary or images[0]
    return chosen.get("uri") or chosen.get("resource_url")


def download_image(url: str, release_id: str) -> tuple[Path | None, str]:
    """Telecharge l'image et l'enregistre sous COVERS_DIR/{id}.{ext}.
    Retourne (path_local, message_si_echec).
    """
    status, headers, body, net_err = http_get(url, accept="image/*")
    if net_err:
        return None, f"erreur reseau : {net_err}"
    if status != 200:
        return None, f"download HTTP {status}"
    ctype = headers.get("content-type", "").split(";")[0].strip().lower()
    ext = CONTENT_TYPE_EXT.get(ctype)
    if ext is None:
        return None, f"Content-Type inconnu : {ctype!r}"
    out = COVERS_DIR / f"{release_id}.{ext}"
    out.write_bytes(body)
    return out, ""


def find_existing(release_id: str) -> Path | None:
    """Cherche un fichier deja telecharge pour ce release_id."""
    for ext in CONTENT_TYPE_EXT.values():
        candidate = COVERS_DIR / f"{release_id}.{ext}"
        if candidate.exists():
            return candidate
    return None


def main() -> int:
    if not VARIANTS_DIR.is_dir():
        print(f"FATAL: {VARIANTS_DIR} introuvable", file=sys.stderr)
        return 1
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    by_id, unparseable = collect_release_ids()
    total = len(by_id)
    print(f"Variantes avec discogs_url parsables : {sum(len(v) for v in by_id.values())}")
    print(f"Release_ids uniques a traiter        : {total}")
    if unparseable:
        print(f"URLs non parsables (ignorees)        : {len(unparseable)}")
        for vid, url in unparseable:
            print(f"  - {vid} : {url}")

    index: dict[str, str] = {}
    cached: list[str] = []
    downloaded: list[str] = []
    failures: list[tuple[str, str, list[str]]] = []  # (rid, reason, variants)
    no_image: list[tuple[str, list[str]]] = []

    sorted_ids = sorted(by_id.keys(), key=int)
    for i, rid in enumerate(sorted_ids, 1):
        variants = by_id[rid]
        prefix = f"[{i:3d}/{total}] release {rid}"
        existing = find_existing(rid)
        if existing is not None:
            rel = existing.relative_to(ROOT / "site").as_posix()
            index[rid] = rel
            cached.append(rid)
            print(f"{prefix} : cached -> {rel}", flush=True)
            continue

        print(f"{prefix} : fetch metadata...", flush=True)
        status, metadata, err = get_release_metadata(rid)
        if metadata is None:
            print(f"  ECHEC metadata : {err}", flush=True)
            failures.append((rid, err, variants))
            time.sleep(RATE_LIMIT_DELAY)
            continue
        img_url = pick_image_url(metadata)
        if img_url is None:
            print("  pas d'image dans la release", flush=True)
            no_image.append((rid, variants))
            time.sleep(RATE_LIMIT_DELAY)
            continue
        time.sleep(RATE_LIMIT_DELAY)  # respect du quota avant le download

        local, err = download_image(img_url, rid)
        if local is None:
            print(f"  ECHEC download : {err}", flush=True)
            failures.append((rid, err, variants))
            time.sleep(RATE_LIMIT_DELAY)
            continue
        rel = local.relative_to(ROOT / "site").as_posix()
        index[rid] = rel
        downloaded.append(rid)
        print(f"  OK -> {rel} ({local.stat().st_size:,} octets)", flush=True)
        time.sleep(RATE_LIMIT_DELAY)

    # Ecriture de l'index (clefs triees pour diff stable).
    sorted_index = dict(sorted(index.items(), key=lambda kv: int(kv[0])))
    INDEX_PATH.write_text(
        json.dumps(sorted_index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Rapport final.
    print()
    print("=" * 60)
    print("RAPPORT")
    print("=" * 60)
    print(f"Releases uniques        : {total}")
    print(f"  telechargees          : {len(downloaded)}")
    print(f"  deja en cache         : {len(cached)}")
    print(f"  sans image            : {len(no_image)}")
    print(f"  echecs                : {len(failures)}")
    print(f"URLs non parsables      : {len(unparseable)}")
    print(f"Index ecrit             : {INDEX_PATH.relative_to(ROOT)}")
    print(f"Entrees dans l'index    : {len(sorted_index)}")
    if failures:
        print()
        print("Detail des echecs :")
        for rid, reason, variants in failures:
            print(f"  release {rid} ({', '.join(variants)}) : {reason}")
    if no_image:
        print()
        print("Releases sans image :")
        for rid, variants in no_image:
            print(f"  release {rid} ({', '.join(variants)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
