"""Valide les fixtures contre schema/variant.schema.json.

- Verifie d'abord que le schema lui-meme est conforme au meta-schema 2020-12.
- Toutes les fixtures sous tests/fixtures/valid/ doivent valider.
- Toutes les fixtures sous tests/fixtures/invalid/ doivent echouer.
- Sortie code 0 si tout est conforme, 1 sinon.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema" / "variant.schema.json"
VALID_DIR = ROOT / "tests" / "fixtures" / "valid"
INVALID_DIR = ROOT / "tests" / "fixtures" / "invalid"


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    print(f"[meta-schema] OK ({SCHEMA_PATH.relative_to(ROOT)})")

    failures: list[str] = []

    for path in sorted(VALID_DIR.glob("*.yml")):
        data = yaml.safe_load(path.read_text())
        errors = list(validator.iter_errors(data))
        if errors:
            failures.append(f"[valid] {path.name} should pass but failed:")
            for e in errors:
                failures.append(f"    - {list(e.absolute_path)}: {e.message}")
        else:
            print(f"[valid]   {path.name} OK")

    for path in sorted(INVALID_DIR.glob("*.yml")):
        data = yaml.safe_load(path.read_text())
        errors = list(validator.iter_errors(data))
        if not errors:
            failures.append(f"[invalid] {path.name} should fail but passed")
        else:
            messages = "; ".join(e.message.split("\n")[0] for e in errors[:3])
            print(f"[invalid] {path.name} REJECTED ({messages})")

    if failures:
        print()
        print("FAILED:")
        for line in failures:
            print(line)
        return 1

    print()
    print("All fixtures behave as expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
