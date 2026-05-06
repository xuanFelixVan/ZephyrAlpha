#!/usr/bin/env python3
"""
GATE-FRONTMATTER: Validate frontmatter enum values against vocabulary YAMLs.
Prevents illegal enum values (like layer: L1 instead of l01_infrastructure)
from reaching the codebase—closes the root cause of C8 (9 files with illegal layer values).



Dimensions:
  DIM-1: doc_type values in vocabulary
  DIM-2: status values in vocabulary
  DIM-3: rule_form values in vocabulary
  DIM-4: layer values in vocabulary
  DIM-5: ttl values in vocabulary
  DIM-6: classification values in vocabulary
  DIM-7: All other vocabulary-backed fields

Exit 1 on any FAIL -> pre-commit blocks the commit.
"""

from __future__ import annotations

__manifest__ = """
args: []
description: GATE-FRONTMATTER — frontmatter 枚举值 vs vocabulary YAML 校验（防止非法值如 layer=L1）
dimensions:
- D3
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""


import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXCLUDE_DIRS, GOV_DOCS_DIR
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files
from _shared.yaml_utils import load_yaml

ensure_utf8_stdout()

VOCAB_DIR = GOV_DOCS_DIR / "_registry" / "vocabularies"

VOCAB_FIELD_MAP = {
    "doc_type": "doc_type-vocabulary.yaml",
    "status": "status-vocabulary.yaml",
    "rule_form": "rule_form-vocabulary.yaml",
    "layer": "layer-vocabulary.yaml",
    "ttl": "ttl-vocabulary.yaml",
    "classification": "classification-vocabulary.yaml",
    "language": "language-vocabulary.yaml",
    "created_by": "created_by-vocabulary.yaml",
    "scope": "scope-vocabulary.yaml",
    "stability": "stability-vocabulary.yaml",
    "verifiability": "verifiability-vocabulary.yaml",
}

_errors: list[str] = []
_warnings: list[str] = []

def _load_vocab_values(vocab_name: str) -> set[str]:
    path = VOCAB_DIR / vocab_name
    if not path.exists():
        return set()
    try:
        data = load_yaml(path)
    except Exception:
        return set()
    values = set()
    for entry in data.get("values", []):
        if isinstance(entry, dict):
            val = entry.get("value") or entry.get("id")
            if val:
                values.add(str(val))
        elif isinstance(entry, str):
            values.add(entry)
    return values

def check_frontmatter_values() -> list[dict]:
    """check frontmatter values."""
    vocab_cache: dict[str, set[str]] = {}
    """检查并返回违规列表."""
    for field_name, vocab_file in VOCAB_FIELD_MAP.items():
        vocab_cache[field_name] = _load_vocab_values(vocab_file)

    checked = 0
    for fpath in iter_files(GOV_DOCS_DIR, extensions=(".md", ".yaml", ".yml")):
        if any(part in EXCLUDE_DIRS for part in fpath.parts):
            continue

        fm = parse_frontmatter_from_file(fpath)
        if not fm:
            continue

        checked += 1
        rel = fpath.relative_to(GOV_DOCS_DIR)

        for field_name, valid_values in vocab_cache.items():
            if not valid_values:
                continue
            raw = fm.get(field_name)
            if raw is None:
                continue
            if isinstance(raw, list):
                vals = [str(v) for v in raw]
            else:
                vals = [str(raw)]

            for v in vals:
                if v not in valid_values:
                    _errors.append(
                        f"{rel}: {field_name}={v} not in {VOCAB_FIELD_MAP[field_name]} "
                        f"(valid: {sorted(valid_values)[:5]}...)"
                    )

    return checked
    """check frontmatter values."""

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()

    print("=" * 72)
    print("GATE-FRONTMATTER: Frontmatter enum values vs vocabulary YAMLs")
    print("=" * 72)
    print()

    checked = check_frontmatter_values()

    print(f"  Checked {checked} files against {len(VOCAB_FIELD_MAP)} vocabularies")
    print()

    if _errors:
        print(f"FAIL: {len(_errors)} illegal frontmatter values:")
        for e in _errors:
            print(f"   {e}")
        sys.exit(1)
    else:
        print(f"ALL {checked} files pass vocabulary validation")
        sys.exit(0)

if __name__ == "__main__":
    main()
