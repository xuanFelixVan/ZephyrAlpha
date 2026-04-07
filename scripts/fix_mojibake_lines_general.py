#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用逐行 mojibake 修复器（适合 BOM/非 BOM 的 UTF-8 文本）。

对每一行：
- 若包含明显 mojibake 字符（Ã/Â/â/å/ä/é/è/ç/æ 等）或控制字符 U+0080..U+009F
- 且整行可视为 0..255 的字节序列（ord<=255）
则尝试：
  bytes(ord(ch) for ch in line).decode('utf-8')
并在满足“中文增加/乱码减少、不引入 U+FFFD”时替换该行。
"""

from __future__ import annotations

import argparse
import pathlib
import re


MOJI_RE = re.compile(r"(?:Ã.|Â.|â.|å.|ä.|é.|è.|ç.|æ.)")
CTRL_RE = re.compile(r"[\u0080-\u009f]")


def cjk_count(s: str) -> int:
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def moji_count(s: str) -> int:
    return len(MOJI_RE.findall(s))


def ctrl_count(s: str) -> int:
    return len(CTRL_RE.findall(s))


def should_attempt(line: str) -> bool:
    return moji_count(line) >= 2 or ctrl_count(line) >= 1


def can_be_bytes(line: str) -> bool:
    return all(ord(ch) <= 255 for ch in line)


def reverse_line(line: str) -> str | None:
    if not can_be_bytes(line):
        return None
    raw = bytes(ord(ch) for ch in line)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def accept(before: str, after: str) -> bool:
    if "\ufffd" in after:
        return False
    b_cjk, a_cjk = cjk_count(before), cjk_count(after)
    b_moji, a_moji = moji_count(before), moji_count(after)
    b_ctl, a_ctl = ctrl_count(before), ctrl_count(after)
    return (a_cjk > b_cjk) or (a_moji < b_moji) or (a_ctl < b_ctl)


def fix_text(text: str) -> tuple[str, int]:
    out = []
    changed = 0
    for line in text.splitlines(keepends=False):
        if should_attempt(line):
            cand = reverse_line(line)
            if cand is not None and accept(line, cand):
                out.append(cand)
                changed += 1
                continue
        out.append(line)
    fixed = "\n".join(out)
    if text.endswith("\n"):
        fixed += "\n"
    return fixed, changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--encoding", default="utf-8-sig", help="read/write encoding (default keeps BOM)")
    args = ap.parse_args()

    fp = pathlib.Path(args.file)
    text = fp.read_text(encoding=args.encoding, errors="strict")
    fixed, changed = fix_text(text)
    if not args.dry_run and changed:
        fp.write_text(fixed, encoding=args.encoding, newline="\n")
    print(f"ChangedLines={changed} DryRun={args.dry_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

