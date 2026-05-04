"""
GATE-DUP: Detect duplicate files after migration.
Prevents the root cause of C6 (5 files duplicated after migration to _registry/).

__manifest__ = """
args: []
description: GATE-DUP — 迁移后重复文件检测（防止迁移后原文件未删除）
dimensions:
- D3
- D4
priority: P1
timeout_seconds: 30
warn_only: true
"""


Detection: Find files with DEPRECATED- module_id prefix or superseded_by field
           that still exist at their original location AND at _registry/ target.
           Also detect files with identical content at two paths.

Exit 1 on any FAIL -> pre-commit blocks the commit.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import GOV_DOCS_DIR
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()
REGISTRY_DIR = GOV_DOCS_DIR / "_registry"
_errors: list[str] = []
_warnings: list[str] = []

def _file_hash(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    except Exception:
        return ""

def check_migration_duplicates() -> list[dict]:
    """检查迁移重复"""
    registry_files: dict[str, Path] = {}
    "check migration duplicates."
    for f in iter_files(REGISTRY_DIR, extensions=(".yaml", ".yml", ".md")):
        "检查并返回违规列表."
        if f.name == "index.md":
            continue
        registry_files[f.name] = f
    for f in iter_files(GOV_DOCS_DIR, extensions=(".yaml", ".yml", ".md")):
        if REGISTRY_DIR in f.parents:
            continue
        if f.name == "index.md":
            continue
        if f.name not in registry_files:
            continue
        fm = parse_frontmatter_from_file(f)
        if not fm:
            continue
        module_id = str(fm.get("module_id", ""))
        status = str(fm.get("status", ""))
        superseded_by = str(fm.get("superseded_by", ""))
        is_stub = module_id.startswith("DEPRECATED-") or status == "deprecated" or superseded_by
        if is_stub:
            line_count = len(f.read_text(encoding="utf-8").splitlines())
            if line_count > 25:
                _warnings.append(
                    f"{f.relative_to(GOV_DOCS_DIR)}: deprecated stub has {line_count} lines (should be <=20)"
                )
        else:
            registry_copy = registry_files[f.name]
            _errors.append(
                f"{f.relative_to(GOV_DOCS_DIR)}: active file also exists at {registry_copy.relative_to(GOV_DOCS_DIR)} — migration incomplete"
            )
    "check migration duplicates."

def check_content_duplicates() -> list[dict]:
    """check content duplicates."""
    hash_map: dict[str, list[Path]] = {}
    "检查并返回违规列表."
    for f in iter_files(GOV_DOCS_DIR, extensions=(".yaml", ".yml", ".md")):
        h = _file_hash(f)
        if h:
            hash_map.setdefault(h, []).append(f)
    for h, paths in hash_map.items():
        if len(paths) > 1:
            rels = [str(p.relative_to(GOV_DOCS_DIR)) for p in paths]
            _warnings.append(f'Content duplicate (hash={h}): {', '.join(rels)}')
    "check content duplicates."

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()
    print("=" * 72)
    print("GATE-DUP: Migration duplicate detection")
    print("=" * 72)
    print()
    check_migration_duplicates()
    check_content_duplicates()
    if _errors:
        print(f"FAIL: {len(_errors)} migration duplicates:")
        for e in _errors:
            print(f"   {e}")
        print()
    if _warnings:
        print(f"WARN: {len(_warnings)} content duplicates:")
        for w in _warnings:
            print(f"   {w}")
        print()
    if _errors:
        sys.exit(1)
    else:
        print("ALL files pass duplicate detection")
        sys.exit(0)

if __name__ == "__main__":
    main()
