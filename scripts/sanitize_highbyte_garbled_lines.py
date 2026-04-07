#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
清理“高字节乱码行”（U+00A0..U+00FF 大量出现）导致的中文显示问题。

背景：
- 在一些文件中，YAML 字段值或正文行被破坏为类似 `\xe9\xa6...` 的高字节序列，
  这些序列往往已缺失关键字节，无法可靠反转回中文。

策略（保守、可读性优先）：
- 仅处理“无中文(CJK=0)且含大量高字节字符”的行；
- 若是 YAML key 行（`^key:`），保留 key，把值置为 `（待补充）`；
- 若是正文乱码行，则删除该行（避免读者看到乱码）。
"""

from __future__ import annotations

import argparse
import pathlib
import re


HIGH_RE = re.compile(r"[\u00a0-\u00ff]")
YAML_KEY_RE = re.compile(r"^([A-Za-z0-9_\\-]+):\\s*(.*)$")


def cjk_count(s: str) -> int:
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def high_count(s: str) -> int:
    return len(HIGH_RE.findall(s))


def sanitize_text(text: str) -> tuple[str, int]:
    out = []
    removed_or_replaced = 0
    for line in text.splitlines(keepends=False):
        hc = high_count(line)
        if hc >= 6 and cjk_count(line) == 0:
            m = YAML_KEY_RE.match(line.strip())
            if m:
                key = m.group(1)
                out.append(f"{key}: （待补充）")
            else:
                # drop noisy line
                pass
            removed_or_replaced += 1
            continue
        out.append(line)
    fixed = "\n".join(out)
    if text.endswith("\n"):
        fixed += "\n"
    return fixed, removed_or_replaced


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="docs")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    changed_files = 0
    changed_lines = 0
    for fp in sorted(root.rglob("*.md")):
        text = fp.read_text(encoding="utf-8-sig", errors="replace")
        fixed, n = sanitize_text(text)
        if n <= 0:
            continue
        changed_files += 1
        changed_lines += n
        if not args.dry_run:
            fp.write_text(fixed, encoding="utf-8-sig", newline="\n")
    print("ChangedFiles=", changed_files, "SanitizedLines=", changed_lines, "DryRun=", args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

