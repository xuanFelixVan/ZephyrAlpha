# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# -*- coding: utf-8 -*-
"""
按 docs/09_AUDIT/STATE/GOVERNANCE_DECISIONS_LOCKED_20260408.md ADR-OC-001
合并文件开头「双 YAML」为单一 front matter。

用法（仓库根）:
  python scripts/merge_double_yaml_frontmatter.py --list              # 列出双头文件
  python scripts/merge_double_yaml_frontmatter.py --dry-run-dir PATH  # 对前 50 个写 .diff
  python scripts/merge_double_yaml_frontmatter.py --apply             # 全量写回
  python scripts/merge_double_yaml_frontmatter.py --apply --max 200   # 仅处理前 200 个
"""

import argparse
import difflib
import re
from datetime import datetime
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".venv", ".pytest_cache", "__pycache__"}

GOVERNANCE_KEYS = frozenset(
    {
        "module_id",
        "version",
        "status",
        "owner",
        "responsibility",
        "standard_type",
        "applicable_scope",
        "compliance_level",
    }
)


def is_fence(line: str) -> bool:
    s = line.strip("\ufeff \t\r\n")
    return s == "---"


def split_double_or_single(text: str) -> tuple[dict | None, dict | None, str, str] | None:
    """
    返回 (yaml1_dict|None, yaml2_dict|None, raw_before_body, body)
    若非双 YAML 则返回 None（调用方跳过）。
    raw_before_body 为到第二段结束 fence 为止的原文（用于 diff）。
    """
    raw = text
    if text.startswith("\ufeff"):
        text = text[1:]
    lines = text.split("\n")
    if not lines or not is_fence(lines[0]):
        return None

    i = 1
    while i < len(lines) and not is_fence(lines[i]):
        i += 1
    if i >= len(lines):
        return None
    yaml1_text = "\n".join(lines[1:i])
    i += 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines):
        return None
    if not is_fence(lines[i]):
        # 单块 front matter：第二道 fence 后直接是正文
        return None

    j = i + 1
    while j < len(lines) and not is_fence(lines[j]):
        j += 1
    if j >= len(lines):
        return None
    yaml2_text = "\n".join(lines[i + 1 : j])
    body = "\n".join(lines[j + 1 :])
    if body and not body.startswith("\n"):
        body = "\n" + body
    elif not body:
        body = "\n"

    try:
        d1 = yaml.safe_load(yaml1_text) or {}
        d2 = yaml.safe_load(yaml2_text) or {}
    except yaml.YAMLError:
        return None
    if not isinstance(d1, dict) or not isinstance(d2, dict):
        return None

    before = "\n".join(lines[: j + 1])
    if raw.startswith("\ufeff"):
        before = "\ufeff" + before
    return (d1, d2, before, body)


def parse_date(val) -> datetime | None:
    if val is None:
        return None
    s = str(val).strip()[:10]
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if not m:
        return None
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def merge_adr(d1: dict, d2: dict) -> dict:
    """ADR-OC-001: 主块 d2，d1 补缺；治理键以 d2 为准；last_updated 取较新。"""
    out = dict(d2)
    for k, v in d1.items():
        if k not in out or out[k] in (None, "", []):
            out[k] = v

    for k in GOVERNANCE_KEYS:
        if k in d2 and d2[k] not in (None, "", []):
            out[k] = d2[k]
        elif k in d1:
            out[k] = d1[k]

    lu1 = parse_date(d1.get("last_updated"))
    lu2 = parse_date(d2.get("last_updated"))
    if lu1 and lu2:
        out["last_updated"] = max(lu1, lu2).strftime("%Y-%m-%d")
    elif lu2:
        out["last_updated"] = d2.get("last_updated")
    elif lu1:
        out["last_updated"] = d1.get("last_updated")

    return out


def build_merged_content(merged: dict, body: str) -> str:
    dump = yaml.dump(
        merged,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    if dump.endswith("\n"):
        dump = dump[:-1]
    return "---\n" + dump + "\n---" + body


def iter_md() -> list[Path]:
    out: list[Path] = []
    for p in REPO.rglob("*.md"):
        if not p.is_file():
            continue
        if any(x in p.parts for x in SKIP_PARTS):
            continue
        out.append(p)
    return sorted(out)


def find_double_yaml_files() -> list[Path]:
    found: list[Path] = []
    for p in iter_md():
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = p.read_text(encoding="utf-8", errors="replace")
        sp = split_double_or_single(text)
        if sp is not None:
            found.append(p)
    return found


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run-dir", type=str, default="")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--max", type=int, default=0)
    args = ap.parse_args()

    double_files = find_double_yaml_files()
    print(f"双 YAML 头文件数: {len(double_files)}")

    if args.list:
        for p in double_files:
            print(p.relative_to(REPO).as_posix())
        return

    if args.dry_run_dir:
        out_dir = REPO / args.dry_run_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        n = 0
        for p in double_files[:50]:
            text = p.read_text(encoding="utf-8", errors="replace")
            sp = split_double_or_single(text)
            if not sp:
                continue
            d1, d2, _, body = sp
            merged = merge_adr(d1, d2)
            new_content = build_merged_content(merged, body)
            rel = p.relative_to(REPO).as_posix().replace("/", "__")
            diff = difflib.unified_diff(
                text.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{rel}",
                tofile=f"b/{rel}",
            )
            (out_dir / f"{rel}.diff").write_text("".join(diff), encoding="utf-8")
            n += 1
        print(f"Wrote {n} diff files under {out_dir}")
        return

    if args.apply:
        limit = args.max if args.max > 0 else len(double_files)
        changed = 0
        for p in double_files[:limit]:
            text = p.read_text(encoding="utf-8", errors="replace")
            sp = split_double_or_single(text)
            if not sp:
                continue
            d1, d2, _, body = sp
            merged = merge_adr(d1, d2)
            new_content = build_merged_content(merged, body)
            if new_content != text:
                p.write_text(new_content, encoding="utf-8", newline="\n")
                changed += 1
        print(f"Applied merge to {changed} files (limit {limit})")
        return

    ap.print_help()


if __name__ == "__main__":
    main()
