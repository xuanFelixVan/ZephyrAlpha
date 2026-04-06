#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将“mojibake 文本”（UTF-8 字节被当成 latin-1/cp1252 文本写入后形成的 é¦–å¸­...）反转回中文。

做法：
- 对每个文件按 UTF-8 读取为文本
- 若满足：CJK 很少 + mojibake token 很多，则尝试 text.encode('latin1').decode('utf-8')
- 成功后写回 UTF-8
"""

from __future__ import annotations

import argparse
import pathlib
import re

MOJI_RE = re.compile(r"(?:Ã.|Â.|â.|å.|ä.|é.|è.|ç.|æ.)")


def cjk_count(s: str) -> int:
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def moji_count(s: str) -> int:
    return len(MOJI_RE.findall(s))


def reverse_mojibake(s: str) -> str | None:
    try:
        b = s.encode("latin-1")
    except UnicodeEncodeError:
        return None
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return None


def should_try(s: str) -> bool:
    m = moji_count(s)
    c = cjk_count(s)
    # 经验阈值：大量 mojibake 且中文极少
    return m >= 200 and c <= 200


def iter_targets(path: pathlib.Path) -> list[pathlib.Path]:
    if path.is_file():
        return [path]
    return sorted(path.glob("*.md"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.path)
    targets = iter_targets(root)

    changed = 0
    for fp in targets:
        text = fp.read_text(encoding="utf-8", errors="strict")
        if not should_try(text):
            continue
        fixed = reverse_mojibake(text)
        if fixed is None:
            continue
        # 只在明显改善时写回
        if cjk_count(fixed) <= cjk_count(text):
            continue
        if not args.dry_run:
            fp.write_text(fixed, encoding="utf-8", newline="\n")
        changed += 1
        print("[OK]", fp.name)

    print("ChangedFiles=", changed, "DryRun=", args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

