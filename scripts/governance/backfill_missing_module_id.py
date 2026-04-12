from __future__ import annotations
# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
为首道 YAML front matter 补全 `module_id`，与 sentinel_l1_governance_scan 口径一致。

处理情形：
1) 首行 `---module_id:` 等「--- 与字段粘连」→ 拆成规范 `---` 换行；
2) 仅有开头 `---`、缺少闭合 `---` → 在首个 `^#{1,6}\\s+\\S` 行前插入闭合 `---`；
3) 已有规范首道 FM 但无 `module_id` → 在 FM 内首行插入 `module_id:`；
4) 全文无首道 FM → 在文首前置最短 `---\\nmodule_id: …\\n---\\n`。

用法（仓库根）:
  python scripts/governance/backfill_missing_module_id.py --dry-run
  python scripts/governance/backfill_missing_module_id.py --apply
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO / "scripts" / "governance") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts" / "governance"))

from sentinel_l1_governance_scan import (  # noqa: E402
    first_front_matter_module_id,
    iter_md_files,
    split_first_front_matter,
)

MODULE_ID_RE = re.compile(r"(?m)^module_id:\s*(.+?)\s*$")
BODY_HEADING_RE = re.compile(r"^#{1,6}\s+\S")


def skip_rel(rel: str) -> bool:
    return rel.startswith("review_materials_package")


def fix_merged_fm_opener(body: str) -> str:
    lines = body.split("\n")
    if not lines:
        return body
    first = lines[0].rstrip("\r")
    if first.startswith("---") and first.strip() != "---":
        rest = first[3:].lstrip()
        lines[0] = "---"
        lines.insert(1, rest)
        return "\n".join(lines)
    return body


def fm_close_line_index(lines: list[str]) -> int | None:
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i
    return None


def close_unterminated_fm(body: str) -> str | None:
    lines = body.split("\n")
    if fm_close_line_index(lines) is not None:
        return None
    if not lines or lines[0].strip() != "---":
        return None
    for k in range(1, len(lines)):
        if BODY_HEADING_RE.match(lines[k].strip()):
            out = lines[:k] + ["---"] + lines[k:]
            return "\n".join(out)
    return None


def normalize_fm_structure(body: str) -> str:
    b = fix_merged_fm_opener(body)
    closed = close_unterminated_fm(b)
    return closed if closed is not None else b


def fm_has_module_id(fm_inner: str) -> bool:
    return bool(MODULE_ID_RE.search(fm_inner))


def path_to_base_id(rel: str) -> str:
    stem = rel[:-3] if rel.lower().endswith(".md") else rel
    parts: list[str] = []
    for seg in stem.split("/"):
        seg = re.sub(r"[^A-Za-z0-9]+", "_", seg)
        seg = re.sub(r"_+", "_", seg).strip("_")
        if seg:
            parts.append(seg)
    s = "_".join(parts).upper() or "DOC"
    if s[0].isdigit():
        s = "M_" + s
    if len(s) > 130:
        h = hashlib.sha256(rel.encode()).hexdigest()[:12].upper()
        s = s[:100] + "_" + h
    return s


def allocate_id(rel: str, used: set[str]) -> str:
    base = path_to_base_id(rel)
    cand = base
    n = 2
    while cand in used:
        cand = f"{base}_{n:03d}"
        n += 1
    used.add(cand)
    return cand


def strip_bom(raw: str) -> tuple[str, str]:
    if raw.startswith("\ufeff"):
        return "\ufeff", raw[1:]
    return "", raw


def insert_module_id_into_normalized_body(body: str, new_id: str) -> str:
    sp = split_first_front_matter(body)
    if sp:
        _bom_p, fm_inner, rest = sp
        if fm_has_module_id(fm_inner):
            return body
        fm2 = f"module_id: {new_id}\n" + fm_inner.lstrip("\n")
        return "---\n" + fm2 + "\n---\n" + rest

    lines = body.split("\n")
    if lines and lines[0].strip() == "---":
        return body

    return f"---\nmodule_id: {new_id}\n---\n\n" + body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="写回文件（默认仅预览）")
    args = ap.parse_args()

    used = collect_used_ids()
    structural: list[tuple[Path, str]] = []
    with_id: list[tuple[Path, str, str]] = []

    for md in iter_md_files():
        rel = md.relative_to(REPO).as_posix()
        if skip_rel(rel):
            continue
        raw = md.read_text(encoding="utf-8", errors="replace")
        bom, body = strip_bom(raw)
        body_n = normalize_fm_structure(body)
        raw_n = bom + body_n

        if first_front_matter_module_id(raw_n):
            if raw_n != raw:
                structural.append((md, raw_n))
            continue

        new_id = allocate_id(rel, used)
        body_f = insert_module_id_into_normalized_body(body_n, new_id)
        raw_f = bom + body_f
        with_id.append((md, new_id, raw_f))

    print(f"structural_fix_only={len(structural)}")
    print(f"add_module_id={len(with_id)}")
    for md, _ in structural[:15]:
        print(f"  [struct] {md.relative_to(REPO).as_posix()}")
    if len(structural) > 15:
        print(f"  ... +{len(structural) - 15} structural")
    for md, nid, _ in with_id[:25]:
        print(f"  [+id] {md.relative_to(REPO).as_posix()} -> {nid}")
    if len(with_id) > 25:
        print(f"  ... +{len(with_id) - 25} id")

    if not args.apply:
        print("(dry-run; use --apply to write)")
        return 0

    for md, txt in structural:
        md.write_text(txt, encoding="utf-8", newline="\n")
    for md, _, txt in with_id:
        md.write_text(txt, encoding="utf-8", newline="\n")
    print("Wrote", len(structural) + len(with_id), "files")
    return 0


def collect_used_ids() -> set[str]:
    used: set[str] = set()
    for md in iter_md_files():
        rel = md.relative_to(REPO).as_posix()
        if skip_rel(rel):
            continue
        raw = md.read_text(encoding="utf-8", errors="replace")
        k = first_front_matter_module_id(raw)
        if k:
            used.add(k)
    return used


if __name__ == "__main__":
    raise SystemExit(main())
