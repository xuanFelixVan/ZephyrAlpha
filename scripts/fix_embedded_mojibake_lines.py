#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复“整体 UTF-8 正常，但部分行出现 mojibake（如 æåæ´æ?* ）”的 Markdown 文档。

策略：
- 逐行检测：若一行不含中文（CJK=0）但包含明显 mojibake 迹象（â/Ã/ä/å/æ/é 等组合），
  且该行可用 latin-1 编码，则尝试做 latin1->utf8 反转：line.encode('latin1').decode('utf-8')。
- 若反转后 mojibake 迹象减少或中文增加，则替换该行。

用法：
  python scripts/fix_embedded_mojibake_lines.py docs/10_AI_WORKFLOW/SENTIMENT_ANALYSIS_SHORT_TERM_TECHNICAL_SPECIFICATION.md
  python scripts/fix_embedded_mojibake_lines.py docs/10_AI_WORKFLOW --glob \"*.md\"
"""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil


MOJI_RE = re.compile(r"(?:Ã.|Â.|â.|å.|ä.|é.|è.|ç.|æ.|ï¿½|Â¿)")


def cjk_count(s: str) -> int:
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def moji_count(s: str) -> int:
    return len(MOJI_RE.findall(s))


def reverse_latin1_utf8(s: str) -> str | None:
    try:
        raw = s.encode("latin-1")
    except UnicodeEncodeError:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def fix_text(text: str) -> tuple[str, int]:
    lines = text.splitlines(keepends=False)
    changed = 0
    out: list[str] = []
    for line in lines:
        before_moji = moji_count(line)
        before_cjk = cjk_count(line)
        # 只要 mojibake 迹象明显，就尝试修复；若该行含大量中文且本来正常，
        # reverse_latin1_utf8 会因无法 latin-1 编码而自动跳过。
        if before_moji >= 2:
            cand = reverse_latin1_utf8(line)
            if cand is not None:
                after_moji = moji_count(cand)
                after_cjk = cjk_count(cand)
                if after_moji < before_moji or after_cjk > before_cjk:
                    out.append(cand)
                    changed += 1
                    continue
        out.append(line)
    fixed = "\n".join(out)
    if text.endswith("\n"):
        fixed += "\n"
    return fixed, changed


def iter_targets(path: pathlib.Path, glob_pattern: str | None) -> list[pathlib.Path]:
    if path.is_file():
        return [path]
    if glob_pattern:
        return sorted(path.glob(glob_pattern))
    return sorted(path.rglob("*.md"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="File or directory")
    ap.add_argument("--glob", default=None, help="Glob pattern when path is a directory (e.g. *.md)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backup-ext", default=".bak2")
    args = ap.parse_args()

    path = pathlib.Path(args.path)
    targets = iter_targets(path, args.glob)
    if not targets:
        print("[ERROR] No targets found")
        return 2

    total_changed_lines = 0
    changed_files = 0

    for fp in targets:
        text = fp.read_text(encoding="utf-8", errors="replace")
        fixed, changed = fix_text(text)
        if changed <= 0:
            continue

        if not args.dry_run:
            backup = fp.with_suffix(fp.suffix + args.backup_ext)
            if not backup.exists():
                shutil.copyfile(fp, backup)
            fp.write_text(fixed, encoding="utf-8", newline="\n")

        changed_files += 1
        total_changed_lines += changed
        print(f"[OK] {fp.as_posix()} changed_lines={changed}")

    print(f"ChangedFiles={changed_files} TotalChangedLines={total_changed_lines} DryRun={args.dry_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

