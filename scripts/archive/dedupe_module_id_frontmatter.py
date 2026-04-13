# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# -*- coding: utf-8 -*-
"""
对首个 YAML front matter 内的 module_id 去重：非 canonical 改为 {id}_ARCHIVED_{n}。
符合 ADR-OC-003。仅改首道 front matter，不碰正文。

用法（仓库根）:
  python scripts/dedupe_module_id_frontmatter.py --dry-run
  python scripts/dedupe_module_id_frontmatter.py --apply
"""

import argparse
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".venv", ".pytest_cache", "__pycache__"}
MID_LINE = re.compile(r"^(module_id:\s*)(.+?)\s*$", re.MULTILINE)


def iter_md() -> list[Path]:
    out: list[Path] = []
    for p in REPO.rglob("*.md"):
        if not p.is_file():
            continue
        if any(x in p.parts for x in SKIP_PARTS):
            continue
        if "review_materials_package" in p.parts:
            continue
        out.append(p)
    return sorted(out)


def split_first_front_matter(raw: str) -> tuple[str, str, str] | None:
    """
    返回 (prefix_bom, fm_inner, body) 其中完整文件 = prefix_bom + '---\\n' + fm_inner + '\\n---\\n' + body
    prefix_bom 为 '' 或 '\\ufeff'
    """
    bom = ""
    s = raw
    if s.startswith("\ufeff"):
        bom = "\ufeff"
        s = s[1:]
    lines = s.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    inner: list[str] = []
    i = 1
    while i < len(lines):
        if lines[i].strip() == "---":
            break
        inner.append(lines[i])
        i += 1
    if i >= len(lines):
        return None
    body = "\n".join(lines[i + 1 :])
    fm_inner = "\n".join(inner)
    return (bom, fm_inner, body)


def fm_module_id(fm_inner: str) -> str | None:
    m = MID_LINE.search(fm_inner)
    if not m:
        return None
    return m.group(2).strip().strip('"').strip("'")


def replace_fm_module_id(fm_inner: str, new_id: str) -> str:
    return MID_LINE.sub(lambda m: f"{m.group(1)}{new_id}", fm_inner, count=1)


def canonical_score(rel: str) -> tuple:
    arch = 0
    if "06_ARCHIVE" in rel or "09_ARCHIVE/duplicates" in rel:
        arch += 100
    if "overlap_" in rel:
        arch += 10
    depth = rel.count("/")
    return (arch, depth, rel)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    id_to_paths: dict[str, list[str]] = defaultdict(list)

    for p in iter_md():
        rel = p.relative_to(REPO).as_posix()
        try:
            raw = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        sp = split_first_front_matter(raw)
        if not sp:
            continue
        _, inner, _ = sp
        mid = fm_module_id(inner)
        if not mid or mid.startswith("YOUR_MODULE_ID"):
            continue
        id_to_paths[mid].append(rel)

    dups = {k: sorted(v, key=canonical_score) for k, v in id_to_paths.items() if len(v) > 1}
    print(f"重复 module_id 组数: {len(dups)}")

    changes: list[tuple[str, str]] = []
    for mid, paths in sorted(dups.items(), key=lambda x: -len(x[1])):
        for i, rel in enumerate(paths[1:], start=1):
            new_mid = f"{mid}_ARCHIVED_{i}"
            changes.append((rel, new_mid))

    if args.dry_run:
        for rel, new_mid in changes[:50]:
            print(f"  {rel} -> module_id: {new_mid}")
        print(f"... total {len(changes)} files")
        return

    if not args.apply:
        ap.print_help()
        return

    n = 0
    for rel, new_mid in changes:
        p = REPO / rel
        raw = p.read_text(encoding="utf-8", errors="replace")
        sp = split_first_front_matter(raw)
        if not sp:
            continue
        bom, inner, body = sp
        new_inner = replace_fm_module_id(inner, new_mid)
        if new_inner == inner:
            continue
        out = f"{bom}---\n{new_inner}\n---\n{body}"
        if not body.endswith("\n") and body:
            pass
        p.write_text(out, encoding="utf-8", newline="\n")
        n += 1
    print(f"Updated {n} files")


if __name__ == "__main__":
    main()
